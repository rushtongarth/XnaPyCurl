#!/bin/bash

basepage=$1
cookie=$2
C='JSESSIONID='$cookie
function reformat {
	metadata=$@
	# extract field names
	awk -f <(cat - <<-'_EOF_'
BEGIN {
	FS=",";
}{
	if($NF!=2){
		if(!match($3,"AS"))
		printf("\t\"%s\":\"%s\"\n",$2,$3)
	}
}
_EOF_
) <( echo "$metadata" )
}

fields=`curl -s -b $C $basepage/search/elements?format=csv | tail -n+2 | awk -F',' '{print $1}'`

for field in ${fields}
do
	printf "\"%s\":{\n" $field
	recs=`curl -s -b $C $basepage/search/elements/${field}?format=csv | tail -n+2`
	reformat "$recs"
	printf "},\n"


	#| grep -v '-' | grep -v '+' | grep -v 'WHEN'
done
