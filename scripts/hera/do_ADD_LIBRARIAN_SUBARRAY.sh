#! /bin/bash

f=$(basename $2 uvc)
echo ${f}
for ext in HH PH PI PP
    do 
        echo exec upload_to_librarian.py "$1" ${f}$ext.uvc $2
        exec upload_to_librarian.py "$1" ${f}$ext.uvc $2
done

