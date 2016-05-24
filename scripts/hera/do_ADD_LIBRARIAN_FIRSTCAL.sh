#! /bin/bash
f=$(basename $2 uvc)
echo ${f}
#only the hexes get firstcal'd
for ext in HH PH
    do
        echo exec upload_to_librarian.py "$1" ${f}$ext.uvc.npz $2
        exec upload_to_librarian.py "$1" ${f}$ext.uvc.npz $2
done
