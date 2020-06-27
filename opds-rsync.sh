#!/bin/bash

# $FROM is the opds directory within the git repo and has no trailing slash.
# $TO   is the parent directory for the odps web root, and assumes that the
#       webroot for odps will be ${PARENT}/odps. Note that the "/odps" is
#       not used.
#
# To copy from one physical machine to another, you need to set up rsync to
#       to use an ssh tunnel, lots of instructions online. This is basic
#       from one directory to another on same machine.

FROM="/home/username/gitrepos/pipfrosch-opds/opds"
TO="/srv/whatever"

rsync -a --include '*/' \
         --include='*.atom' \
         --include='*.jpg' \
         --include='*.png' \
         --exclude="*" \
         --delete ${FROM} ${TO}
