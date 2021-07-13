#!/bin/bash

number=1; 
for file in `ls *.pdf`; do 
	echo "$number $file"; 
	mv $file $number.pdf ; 
	number=$((number+1)) ; 
done
rm -Rf ./auto_renamed
