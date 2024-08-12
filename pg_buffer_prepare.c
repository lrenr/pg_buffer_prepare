#include <limits.h>
#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include "postgres.h"
#include "optimizer/planner.h"
#include "parser/parsetree.h"
#include "storage/bufmgr.h"
#include "storage/lockdefs.h"
#include "utils/elog.h"
#include "utils/guc.h"
#include "access/relation.h"
#include "fmgr.h"
#include "storage/bufmgr.h"
#include "storage/smgr.h"
#include "utils/rel.h"
#include "utils/relcache.h"


PG_MODULE_MAGIC;

typedef enum CacheMode
{
	CACHE_MODE_OFF = 0,
	CACHE_MODE_HOT = 1,
	CACHE_MODE_COLD = 2,
} CacheMode;

static const struct config_enum_entry cache_mode_options[] = {
	{"off", CACHE_MODE_OFF, false},
	{"hot", CACHE_MODE_HOT, false},
	{"cold", CACHE_MODE_COLD, false},
	{NULL, 0, false}
};

static int	cache_mode = CACHE_MODE_OFF;
static int	shuffle_seed = -2;

/* Save previous planner hook user to be a good citizen */
static planner_hook_type prev_planner_hook = NULL;

/* Invalidate all blocks of a Relation in the buffercache */
static void drop_rel(Relation rel) {
	SMgrRelation smgr;

	smgr = RelationGetSmgr(rel);
	DropRelationsAllBuffers(&smgr, 1);
	elog(NOTICE, "MODE=COLD | dropped all blocks of rel: %u\n", rel->rd_id);
}

/* Read all blocks of a Relation into the buffercache */
static void read_rel(Relation rel) {
	Buffer buf;
	uint64 bn, block, precached_blocks;

	bn = RelationGetNumberOfBlocks(rel);
	precached_blocks = 0;
	for (block = 0; block < bn; block++) {
		buf = ReadBuffer(rel, block);
		ReleaseBuffer(buf);
		precached_blocks++;
	}
	elog(NOTICE, "MODE=HOT | precached %u blocks from rel: %u\n", precached_blocks, rel->rd_id);
}

/* Get ID of the Relation associated with a Scan Object */
static Oid get_rel_id(Scan *scan, PlannedStmt *result) {
	Index rtindex;
	RangeTblEntry *rte;

	rtindex = scan->scanrelid;
	rte = rt_fetch(rtindex, result->rtable);
	elog(NOTICE, "Length: %d | Index: %d\nType: %d\nRelId: %u\n",
		list_length(result->rtable), rtindex, rte->type, rte->relid);

	return rte->relid;
}

/* Shuffle the Scan Relation list into a random order (for evaluation) */
static List *shuffle_rel_list(List *rel_list) {
	List *shuffle_list = NIL;
	ListCell *cell;
	int seed;
	Relation* rels = (Relation*)malloc(sizeof(Relation) * rel_list->length);
	int count = 0;

	if (shuffle_seed == -1) seed = time(NULL);
	else seed = shuffle_seed;
	srand(seed);
	elog(NOTICE, "Random Shuffle with Seed=%d\n", seed);

	foreach (cell, rel_list) {
		rels[count] = (Relation)cell->ptr_value;
		count++;
	}
	for (int i = 0; i < rel_list->length - 1; i++) {
		int j = rand() % (rel_list->length - 1);
		Relation tmp = rels[i];
		rels[i] = rels[j];
		rels[j] = tmp;
	}
	for (int i = 0; i < rel_list->length - 1; i++) {
		shuffle_list = lappend(shuffle_list, rels[i]);
	}
	
	free(rels);
	return shuffle_list;
}

/* Custom hook that replaces planner_hook */
static PlannedStmt *pg_buffer_prepare_planner(Query *parse, const char *query_string,
						int cursorOptions, ParamListInfo boundParams)
{
	PlannedStmt *result;
	Plan *next;
	Scan *scan;
	Relation rel;
	Oid oid;
	List *plan_list = NIL;
	List *rel_list = NIL;
	ListCell *cell;

	/* Invoke the planner, possibly via a previous hook user */
	if (prev_planner_hook)
		result = prev_planner_hook(parse, query_string, cursorOptions,
								   boundParams);
	else
		result = standard_planner(parse, query_string, cursorOptions,
								  boundParams);
	
	elog(NOTICE, "Hello from pg_buffer_prepare!\n");

	if (cache_mode == CACHE_MODE_OFF) return result;

	next = result->planTree;
	plan_list = list_make1(next);

	foreach (cell, plan_list) {
		next = cell->ptr_value;

		switch (next->type) {
		case T_SampleScan:
		case T_BitmapHeapScan:
		case T_TidScan:
		case T_TidRangeScan:
		case T_SubqueryScan:
		case T_FunctionScan:
		case T_ValuesScan:
		case T_TableFuncScan:
		case T_CteScan:
		case T_NamedTuplestoreScan:
		case T_WorkTableScan:
		case T_SeqScan:
			scan = &((SeqScan*)next)->scan;
			oid = get_rel_id(scan, result);
			rel_list = lappend(rel_list, relation_open(oid, AccessShareLock));
			break;
		case T_IndexOnlyScan:
		case T_BitmapIndexScan:
		case T_IndexScan:
			scan = &((IndexScan*)next)->scan;
			oid = ((IndexScan*)next)->indexid;
			rel_list = lappend(rel_list, relation_open(oid, AccessShareLock));
			oid = get_rel_id(scan, result);
			rel_list = lappend(rel_list, relation_open(oid, AccessShareLock));
			break;
		default:
			elog(NOTICE, "skipping node\n");
		}

		if (next->lefttree)
			plan_list = lappend(plan_list, (void*)next->lefttree);
		if (next->righttree)
			plan_list = lappend(plan_list, (void*)next->righttree);
		if (next->type)
			elog(NOTICE, "Plan Node Type: %d\n", next->type);
	}

	if (shuffle_seed >= -1) {
		rel_list = shuffle_rel_list(rel_list);
	}

	foreach (cell, rel_list) {
		rel = (Relation)cell->ptr_value;

		switch (cache_mode) {
		case CACHE_MODE_COLD:
			drop_rel(rel);
			break;
		case CACHE_MODE_HOT:
			read_rel(rel);
			break;
		default:
			elog(ERROR, "pg_buffer_prepare: unsupported cache mode setting\n");
		}

		relation_close(rel, AccessShareLock);
	}

	list_free(plan_list);
	list_free(rel_list);

	return result;
}

/* Module load function */
void
_PG_init(void)
{
	DefineCustomEnumVariable("pg_buffer_prepare.cache_mode",
							 "Sets the buffercache preparemode",
							 NULL,
							 &cache_mode,
							 CACHE_MODE_OFF,
							 cache_mode_options,
							 PGC_SUSET,
							 0,
							 NULL,
							 NULL,
							 NULL);
	
	DefineCustomIntVariable("pg_buffer_prepare.shuffle_seed",
							"Set a seed to randomize the rel_list (or -2 to turn off and -1 for time based srand)",
							NULL,
							&shuffle_seed,
							-2,
							-2, INT_MAX,
							PGC_SUSET,
							0,
							NULL,
							NULL,
							NULL);

	MarkGUCPrefixReserved("pg_buffer_prepare");

	prev_planner_hook = planner_hook;
	planner_hook = pg_buffer_prepare_planner;
}
