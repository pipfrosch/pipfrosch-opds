#!/bin/bash
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
    fi
  else
    echo "do nothing"
  fi
  popd
fi
# testing 123
