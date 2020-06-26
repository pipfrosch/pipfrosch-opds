#!/bin/bash

# SECURITY WARNING
#  THIS SCRIPT AUTOMATICALLY GRABS REMOTE CONTENT AND EXECUTES IT,
#  RUN AS UNPRIVILEGED USER THAT ONLY HAS WRITE PERMISSION IN /srv/pipfrosch/pipfrosch-opds
# SAFER WOULD BE RUN IN OWN CONTAINER AND RSYNC PULL OVER SSH TO /srv/pipfrosch/pipfrosch-opds
#  LIMITING BY FILE EXTENSION SO THAT IS TODO
#
OPBSHOME="/srv/pipfrosch/pipfrosch-opds"

if [ -d ${OPBSHOME} ]; then
  pushd ${OPBSHOME} > /dev/null 2>&1
  git remote update > /dev/null 2>&1
  git status > /dev/null 2>&1
  n="`git status -uno |grep -ci "your branch is behind"`"
  if [ ${n} != "0" ]; then
    echo "do stuff"
    git pull > /dev/null 2>&1
    if [ $? -eq 0 ]; then
      sh mkfeeds.sh
    fi
  fi
  popd > /dev/null 2>&1
fi
