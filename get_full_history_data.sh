#!/bin/bash
touch commits.txt

git log --format="%h" "$1/$2.js" > commits.txt

python ./get_data.py $1 $2 # get the current commit first

while read p; do
    git checkout -f -q --detach $p
    python ./get_data.py $1 $2
done <commits.txt

rm commits.txt
