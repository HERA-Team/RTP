#! /bin/bash
set -e

conn_name=$1
librarian_path=$2
f=$(basename $3 uv)

FILE="${f}HH.uv"
echo upload_to_librarian.py $conn_name $FILE $librarian_path/$FILE
upload_to_librarian.py $conn_name $FILE $librarian_path/$FILE
