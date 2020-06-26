#!/bin/bash

# SECURITY WARNING
#  THIS SCRIPT AUTOMATICALLY GRABS REMOTE CONTENT AND EXECUTES IT,
#  RUN AS UNPRIVILEGED USER THAT ONLY HAS WRITE PERMISSION IN /srv/pipfrosch/pipfrosch-opds
# SAFER WOULD BE RUN IN OWN CONTAINER AND RSYNC OVER SSH TO /srv/pipfrosch/pipfrosch-opds
#  SO THAT IS TODO
#
if [ -d /srv/pipfrosch/pipfrosch-opds ]; then
  pushd /srv/pipfrosch/pipfrosch-opds
  git remote update
  git status
  n="`git status -uno |grep -ci "your branch is behind"`"
  if [ ${n} != "0" ]; then
    echo "do stuff"
    git pull
    if [ $? -eq 0 ]; then
      echo "successful pull"
      sh mkfeeds.sh
    fi
  else
    echo "do nothing"
  fi
  popd
fi
# testing 123
