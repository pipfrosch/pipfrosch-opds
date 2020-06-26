pipfrosch-opds
==============
This exists to ease in generation of OPDS files for Pipfrosh Press. Not
applicable elsewhere.

Large publishers probably need to go with a database backend OPDS Atom file
server.

This is specifically for small-time publishing where avoiding the use of a
database backend and using static files for the Atom OPDS files is of
advantage.

Brief Description
-----------------

The script `uuid.py` generates a Type 4 UUID where the first hex character of
the fourth block is always `8` which is what Pipfrosch Press uses for ODPS
feeds for the regular versions of the ePubs.

The feeds for versions of the ePubs with greatly reduced italics will use a
`9` in that place instead, but that is done during generation by the `mkfeed.py`
script.

The `mkfeed.py` script takes a JSON file as argument and generates the
corresponding OPDS Atom feed.

The `mkfeeds.sh` shell script runs `mkfeed.py` on all the JSON files to generate
the OPDS files.

The `cronjob.sh` script checks to see if there are updates to the OPDS system
and pulls them, rerunning the `mkfeeds.sh` script to bring the OPDS feeds up to
current.

The not-yet-written `rsync.sh` script will pull the OPDS Atom files (and cover
and thumbnail images) into the web server serving the OPDS Atom files.

Security
--------

The `cronjob.sh` script is intended to be run once an hour to check for any
updates and when there are updates, it pulls them and executes the scripts.

For obvious security reasons this should not be run on your web server and it
also should not be run from behind a corporate firewall as it grabs remote code
and execute it.

The intent is that it is run from server instance that is secure but is not an
entry point to your web server or your corporate network, as compromising the
git server potentially allows an attacker to run local exploits on the server
instance running the cron job.

The web server will then use rsync over ssh to pull the generated files it needs
but only pull `.atom`, `.jpg`, and `.png` files via rsync so that in the event
the git server is compromised, at worst the web server serves fraudulent Atom
files and/or fraudulent images associated with them.

Even when not executing the `cronjob.sh` script on the web server, I do
recommend that both the script be run by an unprivileged user where it is run
and that an unprivileged user on the web server does the rsync retrieval of the
generated Atom files.

You could also post rsync verify the Atom files only point to other Atom files
on the same server and that acquisition links only point to ePub files on your
ePub server before a second rsync on the OPBS server into the live webroot.

I may write some scripts that do that and make them public.