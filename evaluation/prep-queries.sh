# checks if folder with prepared queries already exists
# creates folder if not present
if [ ! -d ./postgres/queries-prep ]; then
	echo "FOLDER CREATED" &&
	mkdir ./postgres/queries-prep
fi

# extend sql scripts by defining an output file and defining print stats
cd ./postgres/queries
for FILE in *.sql; do 
	printf "\o /home/postgres/queries-outp/$FILE \nEXPLAIN(Analyze, Buffers, Format JSON) \n" | cat - $FILE > tmp &&
	mv tmp ../queries-prep/$FILE &&
	echo $FILE
done
