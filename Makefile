# contrib/pg_cooldown/Makefile

MODULE_big = pg_buffer_prepare
OBJS = \
	$(WIN32RES) \
	pg_buffer_prepare.o
EXTENSION = pg_buffer_prepare
PGFILEDESC = "prepares the buffercache for benchmark tests"


ifdef USE_PGXS
PG_CONFIG = pg_config
PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)
else
subdir = contrib/pg_buffer_prepare
top_builddir = ../..
include $(top_builddir)/src/Makefile.global
include $(top_srcdir)/contrib/contrib-global.mk
endif
