#!/bin/bash
if [ -d /srv/pipfrosch/pipfrosch-opds ]; then
  pushd /srv/pipfrosch/pipfrosch-opds > /dev/null 2>&1
  git status
fi
