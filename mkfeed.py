#!/usr/bin/env python3
import sys
import os
import pathlib
import time
import datetime
import pytz
import json
from xml.dom import minidom
from dateutil import parser

os.environ['TZ'] = 'Europe/London'
time.tzset()

# https://specs.opds.io/opds-1.2.html#23-acquisition-feeds

def createAtomFeed(cwd, jsonfile):
    mtime = []
    ts = datetime.datetime.fromtimestamp(os.path.getmtime(jsonfile))
    mtime.append(ts.strftime("%Y-%m-%dT%H:%M:%SZ"))
    with open(jsonfile) as f:
        jsondata = json.load(f)
    string = jsondata.get("output")
    atom = os.path.join(cwd, string)
    roottag = jsondata.get("root")
    string = "<" + roottag + "/>"
    mydom = minidom.parseString(string)
    root = mydom.getElementsByTagName(roottag)[0]
    # add namespaces
    root.setAttribute('xmlns', 'http://www.w3.org/2005/Atom')
    namespaces = jsondata.get("namespaces")
    nskeys = namespaces.keys()
    for ns in nskeys:
        root.setAttribute('xmlns:' + ns, namespaces.get(ns))
    # get id
    string = jsondata.get("id")
    text = mydom.createTextNode(string)
    node = mydom.createElement('id')
    node.appendChild(text)
    root.appendChild(node)
    # get links
    links = jsondata.get("links")
    for link in links:
        node = mydom.createElement('link')
        node.setAttribute("rel", link.get("rel"))
        node.setAttribute("href", link.get("href"))
        node.setAttribute("type", link.get("type"))
        root.appendChild(node)
    # feed title
    string = jsondata.get("title")
    text = mydom.createTextNode(string)
    node = mydom.createElement('title')
    node.appendChild(text)
    root.appendChild(node)
    # create modified node
    modified = mydom.createElement('updated')
    root.appendChild(modified)
    # author(s)
    authors = jsondata.get("authors")
    for author in authors:
        string = author.get("name")
        text = mydom.createTextNode(string)
        name = mydom.createElement("name")
        name.appendChild(text)
        string = author.get("uri")
        text = mydom.createTextNode(string)
        uri = mydom.createElement("uri")
        uri.appendChild(text)
        authornode = mydom.createElement('author')
        authornode.appendChild(name)
        authornode.appendChild(uri)
        root.appendChild(authornode)
    # TODO - retrieve the entry nodes
    entries = jsondata.get("entries")
    for atomfile in entries:
        filepath = os.path.join(cwd, atomfile)
        ts = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
        mtime.append(ts.strftime("%Y-%m-%dT%H:%M:%SZ"))
        entrydom = minidom.parse(filepath)
        entrynode = mydom.importNode(entrydom.childNodes[0], True)
        entrynode.removeAttribute('xmlns')
        entrynode.removeAttribute('xmlns:dcterms')
        whitelist = ["text/html", "image/jpeg", "image/png", "application/epub+zip"]
        linklist = entrynode.getElementsByTagName("link")
        i = len(linklist) - 1
        while i >= 0 :
            node = linklist[i]
            ntype = node.getAttribute('type')
            if ntype not in whitelist:
                entrynode.removeChild(node)
            i -= 1
        root.appendChild(entrynode)
        
    # update the modified
    mtime.sort(reverse=True)
    text = mydom.createTextNode(mtime[0])
    modified.appendChild(text)
    # dump to file
    string = mydom.toprettyxml(indent="  ",newl="\n",encoding="UTF-8").decode()
    string = '\n'.join([x for x in string.split("\n") if x.strip()!=''])
    fh = open(atom, "w")
    fh.write(string)
    fh.close()

def main():
    if len(sys.argv) != 2:
        print("fubar")
        sys.exit(1)
    cwd = os.getcwd()
    createAtomFeed(cwd, sys.argv[1])

if __name__ == "__main__":
    main()