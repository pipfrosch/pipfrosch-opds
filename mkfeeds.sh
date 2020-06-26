#!/bin/bash
for json in JoM.json mammals.json vertebrates.json; do
  noitalics="`echo ${json} |sed -e s?"\.json$"?"-noitalics.json"?`"
  cat ${json} |sed -e s?"\.atom"?"-noitalics.atom"?g > ${noitalics}
  touch -r ${json} ${noitalics}
  python3 mkfeed.py ${json}
  python3 mkfeed.py ${noitalics}
done
