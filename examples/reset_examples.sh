#!/bin/bash

number=1; 
cp -p ./auto_renamed_pdf/*.pdf . 
for file in `ls *.pdf`; do 
	mv $file 'temp_'$file
	echo "$number $file"
	mv 'temp_'$file $number.pdf
	number=$((number+1))
done
rm -Rf ./auto_renamed_pdf
