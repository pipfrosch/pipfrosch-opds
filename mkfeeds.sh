#!/bin/bash
for json in JoM.json mammals.json vertebrates.json recent.json; do
  noitalics="`echo ${json} |sed -e s?"\.json$"?"-noitalics.json"?`"
  cat ${json} |sed -e s?"\.atom"?"-noitalics.atom"?g > ${noitalics}
  # make sure noitalics have same modification timestamp
  touch -r ${json} ${noitalics}
  python3 mkfeed.py ${json}
  python3 mkfeed.py ${noitalics}
done
cat root.json |sed -e s?"\.json"?"-noitalics.json"?g |sed -e s?"\.atom"?"-noitalics.atom"?g > root-noitalics.json
# make sure root.json has very fresh timestamp
touch -r root-noitalics.json root.json
python3 mkfeed.py root.json
python3 mkfeed.py root-noitalics.json

# cleanup temporary files
rm -rf __pycache__
find . -print |grep "\-noitalics\.json" |while read file; do
  rm -f "${file}"
done
# testing 123
