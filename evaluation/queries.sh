# determine current database mode
case $1 in
	pgdefault)
		mode=pgdefault
		config="set pg_buffer_prewarm.cache_mode=OFF; \n show pg_buffer_prewarm.cache_mode;"
		;;
	
	hotstart)
		mode=hotstart
		config="set pg_buffer_prewarm.cache_mode=HOT;\n show pg_buffer_prewarm.cache_mode;"
		;;
	
	coldstart)
		mode=coldstart
		config="set pg_buffer_prewarm.cache_mode=COLD; \n show pg_buffer_prewarm.cache_mode;"
		;;
	
	*)
		echo -n "missing or wrong mode attribute"
		exit
esac

# number of iterations per experiment
iterations=$2

# checks if folder with prepared queries already exists
# creates folder if not present
if [ ! -d ./postgres/queries-prep ]; then
	mkdir ./postgres/queries-prep
fi

# check if output path defined in prepared sql file exists
if [ ! -d ./postgres/queries-outp/ ]; then
	mkdir ./postgres/queries-outp
fi

# check if output path defined in prepared sql file exists
if [ ! -d ./postgres/queries-outp/pgdefault ]; then
	mkdir ./postgres/queries-outp/pgdefault
fi

# check if output path defined in prepared sql file exists
if [ ! -d ./postgres/queries-outp/hotstart ]; then
	mkdir ./postgres/queries-outp/hotstart
fi

# check if output path defined in prepared sql file exists
if [ ! -d ./postgres/queries-outp/coldstart ]; then
	mkdir ./postgres/queries-outp/coldstart
fi

# execute queries is random order
# run every experiment multiple times
for ((curr_iter=0; curr_iter < $iterations; curr_iter++)); do
	# following code is done one time per iteration

	# check if target folder is existing before preapering the sql scripts
	if [ ! -d ./postgres/queries-outp/$mode/$curr_iter ]; then
		mkdir ./postgres/queries-outp/$mode/$curr_iter
	fi

	# prepare sql scripts for execution by defining an output file and defining print stats
	cd ./postgres/queries
	for file in *.sql; do 
		printf "$config\n\o /home/postgres/queries-outp/$mode/$curr_iter/$file.json \nEXPLAIN(Analyze, Buffers, Format JSON) \n" | cat - $file > tmp &&
		mv tmp ../queries-prep/$file &&
		echo "$file prepared"
	done

	# iterate over alls queries
	cd ../queries-prep
	echo -n "mode: $mode | iteration: $curr_iter\n"
	for file in $(ls *.sql | shuf); do
		echo -n "$file" &&
		
		# get docker id
		long_id=$(docker ps --no-trunc | sed '1d' | cut -d' ' -f1)

		# read pagefaults
		cat /sys/fs/cgroup/system.slice/docker-$long_id.scope/memory.stat | grep pgfault >> ../queries-outp/$mode/$curr_iter/$file\_memstat_start
		
		# execute sql query
		docker exec -it postgres-benchmark /bin/bash -c "psql imdb -f /home/postgres/queries-prep/$file"
		
		# read pagefaults
		cat /sys/fs/cgroup/system.slice/docker-$long_id.scope/memory.stat | grep pgfault >> ../queries-outp/$mode/$curr_iter/$file\_memstat_end
	done

	# reset path
	cd ../../

done
exit