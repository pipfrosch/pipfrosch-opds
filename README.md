# pipfrosch-opds
This exists to ease in generation of OPDS files for Pipfrosh Press. Not
applicable elsewhere.

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
