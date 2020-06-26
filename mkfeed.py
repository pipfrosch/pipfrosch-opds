#!/usr/bin/env python3
import sys
import os
import pathlib
import time
import datetime
import pytz
import json
import re
from xml.dom import minidom
from dateutil import parser

os.environ['TZ'] = 'Europe/London'
time.tzset()

# https://specs.opds.io/opds-1.2.html#23-acquisition-feeds

def validateUUID(string):
    if type(string) != str:
        print(string + " is not a valid UUID urn string.")
        sys.exit(1)
    if len(string) != 45:
        print(string + " is not a valid UUID urn string.")
        sys.exit(1)
    header = string[0:9]
    if header != "urn:uuid:":
        print(string + " is not a valid UUID urn string.")
        sys.exit(1)
    uuidstring = string[9:]
    pattern = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)
    match = re.search(pattern, uuidstring)
    if not match:
        print(string + " is not a valid UUID urn string.")
        sys.exit(1)
    uuidlist = list(uuidstring)
    if uuidlist[14] != "4":
        print(uuidstring + " is not a valid Version 4 UUID.")
        sys.exit(1)
    if uuidlist[19] != "8":
        print("first character of fourth block in " + uuidstring + " is not 8")
        sys.exit(1)

def createAtomFeed(cwd, jsonfile):
    mtime = []
    try:
        ts = datetime.datetime.fromtimestamp(os.path.getmtime(jsonfile))
    except:
        print('File ' + jsonfile + ' does not exist.')
        sys.exit(1)
    mtime.append(ts.strftime("%Y-%m-%dT%H:%M:%SZ"))
    try:
        with open(jsonfile) as f:
            jsondata = json.load(f)
    except:
        print(jsonfile + ' does not appear to be valid JSON.')
        sys.exit(1)
    if "output" not in jsondata.keys():
        print(jsonfile + ' does not specify proper output file.')
        sys.exit(1)
    if type(jsondata.get("output")) != str:
        print("Value for output key in " + jsonfile + " is not a string.")
        sys.exit(1)
    string = jsondata.get("output")
    atom = os.path.join(cwd, string)
    string = "<feed/>"
    mydom = minidom.parseString(string)
    root = mydom.getElementsByTagName('feed')[0]
    # add namespaces
    root.setAttribute('xmlns', 'http://www.w3.org/2005/Atom')
    if "namespaces" in jsondata.keys():
        namespaces = jsondata.get("namespaces")
        # TODO verify ns and attribute are valid XMLNS
        if type(namespaces) != dict:
            print("The namespaces key in " + jsonfile + "is not a key=value dictionary.")
            sys.exit(1)
        nskeys = namespaces.keys()
        for ns in nskeys:
            if type(namespaces.get(ns)) != str:
                print("The specified namespace associated with " + ns + " is not a string")
                sys.exit(1)
            root.setAttribute('xmlns:' + ns, namespaces.get(ns))
    # get id
    if "id" not in jsondata.keys():
        print(jsonfile + ' does not specify id.')
        sys.exit(1)
    validateUUID(jsondata.get("id"))
    stringlist = list(jsondata.get("id"))
    if "-noitalics" in jsonfile:
        # indicate noitalics by changing first hex of fourth group to 9
        stringlist[28] = "9"
    string = ''.join(stringlist)
    text = mydom.createTextNode(string)
    node = mydom.createElement('id')
    node.appendChild(text)
    root.appendChild(node)
    # get links
    if "links" not in jsondata.keys():
        print(jsonfile + ' does not specify links.')
        sys.exit(1)
    links = jsondata.get("links")
    if type(links) != list:
        print("The links key in " + jsonfile + "is not a list.")
        sys.exit(1)
    for link in links:
        if type(link) != dict:
            print("some entries in the links key in " + jsonfile  + " are not a key=value dictionary.")
            sys.exit(1)
        node = mydom.createElement('link')
        if "rel" not in link.keys():
            print("some dictionaries in the links key in " + jsonfile + " do not have a rel key.")
            sys.exit(1)
        if type(link.get("rel")) != str:
            print("Some rel keys in dictionaries within the links key in " + jsonfile + " do not have a string value.")
            sys.exit(1)
        node.setAttribute("rel", link.get("rel"))
        if "href" not in link.keys():
            print("some dictionaries in the links key in " + jsonfile + " do not have a href key.")
            sys.exit(1)
        if type(link.get("href")) != str:
            print("Some href keys in dictionaries within the links key in " + jsonfile + " do not have a string value.")
            sys.exit(1)
        node.setAttribute("href", link.get("href"))
        if "type" not in link.keys():
            print("some dictionaries in the links key in " + jsonfile + " do not have a type key.")
            sys.exit(1)
        if type(link.get("type")) != str:
            print("Some type keys in dictionaries within the links key in " + jsonfile + " do not have a string value.")
            sys.exit(1)
        node.setAttribute("type", link.get("type"))
        root.appendChild(node)
    # feed title
    if "title" not in jsondata.keys():
        print(jsonfile + ' does not specify title.')
        sys.exit(1)
    if type(jsondata.get("title")) != str:
        print("The title value in " + jsonfile + " is not a string.")
        sys.exit(1)
    string = jsondata.get("title")
    text = mydom.createTextNode(string)
    node = mydom.createElement('title')
    node.appendChild(text)
    root.appendChild(node)
    # create update node but do not fill it yet
    modified = mydom.createElement('updated')
    root.appendChild(modified)
    # author(s)
    if "authors" not in jsondata.keys():
        print(jsonfile + ' does not specify author(s).')
        sys.exit(1)
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
    testcounter = 0
    # acquisition nodes
    if "acquisitions" in jsondata.keys():
        testcounter += 1
        acquisitions = jsondata.get("acquisitions")
        for feed in acquisitions:
            feedjson = os.path.join(cwd, feed)
            with open(feedjson) as g:
                feeddata = json.load(g)
            entry = mydom.createElement("entry")
            # feed title
            string = feeddata.get("title")
            text = mydom.createTextNode(string)
            node = mydom.createElement('title')
            node.appendChild(text)
            entry.appendChild(node)
            # feed link
            node = mydom.createElement('link')
            if "rootrel" in feeddata.keys():
                string = feeddata.get('rootrel')
            else:
                string = 'subsection'
            node.setAttribute('rel', string)
            prestring = feeddata.get('output')
            string = prestring[4:]
            node.setAttribute('href', string)
            node.setAttribute('type', 'application/atom+xml;profile=opds-catalog;kind=acquisition')
            entry.appendChild(node)
            # updated
            atomfile = os.path.join(cwd, feeddata.get('output'))
            atomdom = minidom.parse(atomfile)
            modifiednode = atomdom.getElementsByTagName('updated')[0]
            nodevalue = modifiednode.firstChild.nodeValue
            text = mydom.createTextNode(nodevalue)
            node = mydom.createElement('updated')
            node.appendChild(text)
            entry.appendChild(node)
            # get the ID
            idnode = atomdom.getElementsByTagName('id')[0]
            nodevalue = idnode.firstChild.nodeValue
            text = mydom.createTextNode(nodevalue)
            node = mydom.createElement('id')
            node.appendChild(text)
            entry.appendChild(node)
            # content
            string = feeddata.get("content")
            text = mydom.createTextNode(string)
            node = mydom.createElement('content')
            node.setAttribute('type', 'text')
            node.appendChild(text)
            entry.appendChild(node)
            # append the entry
            root.appendChild(entry)
    # entry nodes
    if "entries" in jsondata.keys():
        testcounter += 1
        entries = jsondata.get("entries")
        for atomfile in entries:
            filepath = os.path.join(cwd, atomfile)
            ts = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
            mtime.append(ts.strftime("%Y-%m-%dT%H:%M:%SZ"))
            entrydom = minidom.parse(filepath)
            entrynode = mydom.importNode(entrydom.childNodes[0], True)
            entrynode.removeAttribute('xmlns')
            entrynode.removeAttribute('xmlns:dc')
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
    if testcounter == 0:
        print(jsonfile + ' does not have acquisition or entry nodes.')
        sys.exit(1)
    # update the modified
    mtime.sort(reverse=True)
    text = mydom.createTextNode(mtime[0])
    modified.appendChild(text)
    # dump to file
    string = mydom.toprettyxml(indent="  ",newl="\n",encoding="UTF-8").decode()
    string = '\n'.join([x for x in string.split("\n") if x.strip()!=''])
    try:
        fh = open(atom, "w")
        fh.write(string)
        fh.close()
    except:
        print('Could not write to file ' + atom)
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("fubar")
        sys.exit(1)
    cwd = os.getcwd()
    createAtomFeed(cwd, sys.argv[1])

if __name__ == "__main__":
    main()