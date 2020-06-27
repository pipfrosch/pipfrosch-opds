#!/usr/bin/env python3
import sys
import os
import pathlib
import time
import datetime
import json
import re
from xml.dom import minidom
from dateutil import parser

os.environ['TZ'] = 'Europe/London'
time.tzset()

# https://specs.opds.io/opds-1.2.html

# Pipfrosch Press only uses Version 4 UUID
def validateUUID(string, jsonfile):
    if type(string) != str:
        print('Error in ' + jsonfile + ': ' + string + ' is not a valid UUID urn string.')
        sys.exit(1)
    if len(string) != 45:
        print('Error in ' + jsonfile + ': ' + string + ' is not a valid UUID urn string.')
        sys.exit(1)
    header = string[0:9]
    if header != 'urn:uuid:':
        print('Error in ' + jsonfile + ': ' + string + ' is not a valid UUID urn string.')
        sys.exit(1)
    uuidstring = string[9:]
    pattern = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)
    match = re.search(pattern, uuidstring)
    if not match:
        print('Error in ' + jsonfile + ': ' + string + ' is not a valid UUID urn string.')
        sys.exit(1)
    uuidlist = list(uuidstring)
    if uuidlist[14] != '4':
        print('Error in ' + jsonfile + ': ' + uuidstring + ' is not a valid Version 4 UUID.')
        sys.exit(1)
    if uuidlist[19] != '8':
        print('Error in ' + jsonfile + ': ' + 'first character of fourth block in ' + uuidstring + ' is not 8')
        sys.exit(1)

def validateNamespaces(dictionary, jsonfile):
    if type(dictionary) != dict:
        print('The namespaces key in ' + jsonfile + ' does not point to a valid dictionary.')
        sys.exit(1)
    keylist = dictionary.keys()
    pattern = re.compile(r'^[a-z]+$')
    #from https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
    # Note that the purpose of a namespace URI is just to something unique that frequently points to a web page
    # defining the namespace but it does not have to, so yes, localhost is legal in a namespace URI. Bad practice
    # but legal.
    uripattern = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    for ns in keylist:
        match = re.search(pattern, ns)
        if not match:
            print('Error in ' + jsonfile + ': A namespaces key should only contain lower case letters.')
            sys.exit(1)
        if len(ns) > 12:
            print('Error in ' + jsonfile + ': A namespaces key really should not be more than twelve characters in length.')
            sys.exit(1)
        uri = dictionary.get(ns)
        if type(uri) != str:
            print('Error in ' + jsonfile + ': The value associated with the namespaces key ' + ns + ' is not a string.')
            sys.exit(1)
        match = re.search(uripattern, uri)
        if not match:
            print('Error in ' + jsonfile + ': The value associated with the namespaces key ' + ns + ' is not a valid uri.')
            sys.exit(1)

def validateLinks(links, jsonfile):
    if type(links) != list:
        print('Error in ' + jsonfile + ': The links key in " + jsonfile + " does not point to a valid list.')
        sys.exit(1)
    reqatt = ['rel', 'href', 'type']
    for link in links:
        if type(link) != dict:
            print('Error in ' + jsonfile + ': Not all entries in links list are key=value dictionaries.')
            sys.exit(1)
        keys = link.keys()
        for att in reqatt:
            if att not in keys:
                print('Error in ' + jsonfile + ': Some dictionaries in links list are missing the ' + att + ' key.')
                sys.exit(1)
            if type(link.get(att)) != str:
                print('Error in ' + jsonfile + ': The links value associated with ' + att + ' is not a string.')
                sys.exit(1)

def validateAuthors(authors, jsonfile):
    if type(authors) != list:
        print('Error in ' + jsonfile + ': The authors key in ' + jsonfile + ' does not point to a valid list.')
        sys.exit(1)
    for author in authors:
        if type(author) != dict:
            print('Error in ' + jsonfile + ': Some author entries in ' + jsonfile + ' are not dictionaries.')
            sys.exit(1)
        keys = author.keys()
        if 'name' not in author:
            print('Error in ' + jsonfile + ': Some author entries in ' + jsonfile + ' do not have a name key.')
            sys.exit(1)
        for key in keys:
            if type(author.get(key)) != str:
                print('Error in ' + jsonfile + ': Some author keys in ' + jsonfile + ' do not have string values.')
                sys.exit(1)

def createAtomFeed(cwd, jsonfile):
    mtime = []
    try:
        ts = datetime.datetime.fromtimestamp(os.path.getmtime(jsonfile))
    except:
        print('File ' + jsonfile + ' does not exist.')
        sys.exit(1)
    mtime.append(ts.strftime('%Y-%m-%dT%H:%M:%SZ'))
    try:
        with open(jsonfile) as f:
            jsondata = json.load(f)
    except:
        print(jsonfile + ' does not appear to be valid JSON.')
        sys.exit(1)
    if 'output' not in jsondata.keys():
        print(jsonfile + ' does not specify proper output file.')
        sys.exit(1)
    if type(jsondata.get('output')) != str:
        print('Value for output key in ' + jsonfile + ' is not a string.')
        sys.exit(1)
    string = jsondata.get('output')
    atom = os.path.join(cwd, string)
    string = '<feed/>'
    mydom = minidom.parseString(string)
    root = mydom.getElementsByTagName('feed')[0]
    # add namespaces
    root.setAttribute('xmlns', 'http://www.w3.org/2005/Atom')
    if 'namespaces' in jsondata.keys():
        namespaces = jsondata.get('namespaces')
        validateNamespaces(namespaces, jsonfile)
        nskeys = namespaces.keys()
        for ns in nskeys:
            root.setAttribute('xmlns:' + ns, namespaces.get(ns))
    # get id
    if 'id' not in jsondata.keys():
        print(jsonfile + ' does not specify id.')
        sys.exit(1)
    validateUUID(jsondata.get('id'), jsonfile)
    stringlist = list(jsondata.get('id'))
    if "-noitalics" in jsonfile:
        # indicate noitalics by changing first hex of fourth group to 9
        stringlist[28] = '9'
    string = ''.join(stringlist)
    text = mydom.createTextNode(string)
    node = mydom.createElement('id')
    node.appendChild(text)
    root.appendChild(node)
    # get links
    if 'links' not in jsondata.keys():
        print(jsonfile + ' does not specify links.')
        sys.exit(1)
    links = jsondata.get("links")
    validateLinks(links, jsonfile)
    for link in links:
        node = mydom.createElement('link')
        node.setAttribute('rel', link.get('rel'))
        node.setAttribute('href', link.get('href'))
        node.setAttribute('type', link.get('type'))
        root.appendChild(node)
    # feed title
    if 'title' not in jsondata.keys():
        print(jsonfile + ' does not specify title.')
        sys.exit(1)
    if type(jsondata.get('title')) != str:
        print('The title value in ' + jsonfile + ' is not a string.')
        sys.exit(1)
    string = jsondata.get('title')
    text = mydom.createTextNode(string)
    node = mydom.createElement('title')
    node.appendChild(text)
    root.appendChild(node)
    # create update node but do not fill it yet
    modified = mydom.createElement('updated')
    root.appendChild(modified)
    # author(s)
    if 'authors' not in jsondata.keys():
        print(jsonfile + ' does not specify author(s).')
        sys.exit(1)
    authors = jsondata.get('authors')
    validateAuthors(authors, jsonfile)
    for author in authors:
        authornode = mydom.createElement('author')
        string = author.get('name')
        text = mydom.createTextNode(string)
        name = mydom.createElement('name')
        name.appendChild(text)
        authornode.appendChild(name)
        if 'uri' in author.keys():
            string = author.get('uri')
            text = mydom.createTextNode(string)
            uri = mydom.createElement('uri')
            uri.appendChild(text)
            authornode.appendChild(uri)
        root.appendChild(authornode)
    testcounter = 0
    # acquisition nodes
    if 'acquisitions' in jsondata.keys():
        testcounter += 1
        acquisitions = jsondata.get('acquisitions')
        if type(acquisitions) != list:
            print('The acquisitions entry in ' + jsonfile + ' is not a list.')
            sys.exit(1)
        for feed in acquisitions:
            feedjson = os.path.join(cwd, feed)
            try:
                with open(feedjson) as g:
                    feeddata = json.load(g)
            except:
                print(feedjson + ' does not appear to be valid JSON.')
                sys.exit(1)
            entry = mydom.createElement('entry')
            # feed title
            if 'title' not in feeddata.keys():
                print(feedjson + ' does not specify title.')
                sys.exit(1)
            if type(feeddata.get('title')) != str:
                print('The title value in ' + feedjson + ' is not a string.')
                sys.exit(1)
            string = feeddata.get('title')
            text = mydom.createTextNode(string)
            node = mydom.createElement('title')
            node.appendChild(text)
            entry.appendChild(node)
            # feed link
            node = mydom.createElement('link')
            if 'rootrel' in feeddata.keys():
                if type(feeddata.get('rootrel')) != str:
                    print('The rootrel entry in ' + feedjson + ' is not a string.')
                    sys.exit(1)
                string = feeddata.get('rootrel')
            else:
                string = 'subsection'
            node.setAttribute('rel', string)
            if 'output' not in feeddata.keys():
                print(feedjson + ' does not specify its output file.')
                sys.exit(1)
            if type(feeddata.get('output')) != str:
                print('Value for output key in ' + feedjson + ' is not a string.')
                sys.exit(1)
            prestring = feeddata.get('output')
            string = prestring[4:]
            node.setAttribute('href', string)
            node.setAttribute('type', 'application/atom+xml;profile=opds-catalog;kind=acquisition')
            entry.appendChild(node)
            # updated
            atomfile = os.path.join(cwd, feeddata.get('output'))
            try:
                atomdom = minidom.parse(atomfile)
            except:
                print('Could not parse the XML Atom file ' + atomfile)
                sys.exit(1)
            # import updated node
            nodelist = atomdom.getElementsByTagName('updated')
            if len(nodelist) == 0:
                print('The XML Atom file ' + atomfile + 'does not contain an updated node.')
                sys.exit(1)
            impnode = mydom.importNode(nodelist[0], True)
            entry.appendChild(impnode)
            # import id node
            nodelist = atomdom.getElementsByTagName('id')
            if len(nodelist) == 0:
                print('The XML Atom file ' + atomfile + 'does not contain an id node.')
                sys.exit(1)
            impnode = mydom.importNode(nodelist[0], True)
            entry.appendChild(impnode)
            # content
            if 'content' in feeddata.keys():
                string = feeddata.get('content')
                if type(string) != str:
                    print('The content value in ' + feedjson + ' is not a string.')
                    sys.exit(1)
                text = mydom.createTextNode(string)
                node = mydom.createElement('content')
                node.setAttribute('type', 'text')
                node.appendChild(text)
                entry.appendChild(node)
            # append the entry
            root.appendChild(entry)
    # entry nodes
    if 'entries' in jsondata.keys():
        testcounter += 1
        entries = jsondata.get('entries')
        if type(entries) != list:
            print('The entries key in ' + jsonfile + ' is not for a list.')
            sys.exit(1)
        for filename in entries:
            if type(filename) != str:
                print('The entries list in ' + jsonfile + ' contains types other than strings.')
                sys.exit(1)
            atomfile = os.path.join(cwd, filename)
            ts = datetime.datetime.fromtimestamp(os.path.getmtime(atomfile))
            mtime.append(ts.strftime('%Y-%m-%dT%H:%M:%SZ'))
            try:
                atomdom = minidom.parse(atomfile)
            except:
                print('Could not parse the XML Atom file ' + atomfile)
                sys.exit(1)
            nodelist = atomdom.getElementsByTagName('entry')
            if len(nodelist) == 0:
                print('The XML Atom file ' + atomfile + 'does not contain an entry node.')
                sys.exit(1)
            impnode = mydom.importNode(nodelist[0], True)
            attributes = impnode.attributes.items()
            for att in attributes:
                attname = att[0]
                if len(attname) > 4:
                    test = attname[0:5]
                    if test == 'xmlns':
                        impnode.removeAttribute(attname)
            whitelist = ['text/html', 'image/jpeg', 'image/png', 'application/epub+zip']
            linklist = impnode.getElementsByTagName('link')
            i = len(linklist) - 1
            while i >= 0 :
                node = linklist[i]
                if node.hasAttribute('type'):
                    ntype = node.getAttribute('type')
                    if ntype not in whitelist:
                        impnode.removeChild(node)
                else:
                    impnode.removeChild(node)
                i -= 1
            root.appendChild(impnode)
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
        fh = open(atom, 'w')
        fh.write(string)
        fh.close()
    except:
        print('Could not write to file ' + atom)
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print('fubar')
        sys.exit(1)
    cwd = os.getcwd()
    createAtomFeed(cwd, sys.argv[1])

if __name__ == '__main__':
    main()