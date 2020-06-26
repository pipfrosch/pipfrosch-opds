#!/bin/bash
if [ -d /srv/pipfrosch/pipfrosch-opds ]; then
  pushd /srv/pipfrosch/pipfrosch-opds
  git remote update
  git status
  n="`git status -uno |grep -ci "your branch is behind"`"
  if [ ${n} != "0" ];
    echo "do stuff"
  fi
  popd
fi
