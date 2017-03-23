#!/bin/bash
touch commits.txt

git log --format="%h" "$1/$2.js" > commits.txt

python ../react-native-static-analyzer/get_data.py $1 $2 # get the current commit first

while read p; do
    git checkout -f -q --detach $p
    python ../react-native-static-analyzer/get_data.py $1 $2
done <commits.txt

git checkout master 2>/dev/null 1>/dev/null
rm commits.txt
