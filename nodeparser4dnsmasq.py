#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Jonas aka Wolf"
__email__ = "jonas.hess@mailbox.org"
__license__ = "GPLv3"

import requests
import json
import re


def writeDnsmasqFile(hostarray, path, mode):
    if (len(hostarray) == 0):
        print '-!- The host-array for writDnsmasqFile-function is empty'
        return False

    if mode == 'append':
        try:
            fq = open(path, "a")
        except:
            print '-!- Error on opening file: ' + path
            return False

    elif mode == 'new':
        try:
            fq = open(path, "w")
        except:
            print '-!- Error on opening file: ' + path
            return False

    fq.write('# Entries by nodeparser following:' + "\n")

    for entry in hostarray:
        hostname = entry['host']
        address = entry['addr']
        fq.write('address=/' + hostname + '/' + address + "\n")

    fq.close()


def fqdn(hostname, suffix):
    mapping = [('^', '_'), (':', '-'), (' ', '-'), ('ä', 'ae'), ('ö', 'oe'), ('ü', 'ue'), ('Ä', 'ae'), ('ö', 'oe'), ('Ü', 'ue'), ('@', '.at'), ('(', ''), (')', '')]

    try:
        hostname = hostname.decode('utf8')
    except:
        print '-!- Cannot Decode: "' + hostname + '"'

#     print '- Hostname: ' + hostname.decode('utf8')
    for k, v in mapping:
        try:
            hostname = hostname.replace(k.decode('utf8'), v.decode('utf8'))
        except:
            print '-!- Replacement error on Hostname: "' + hostname + '"'
            return False

    pattern = re.compile("^^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.){2,}([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9]){2,}$")

    if suffix != None and pattern.match(suffix) == False:
        print '-!- Suffix is no FQDN'
        return False

    else:
        if pattern.match(hostname) == False:
            print '-!- Hostname "' + hostname + '" is not a FQDN!'
        else:
            if suffix != None:
                return hostname + '.' + suffix
            else:
                return hostname


def load_nodes(url_mesh_json, suffix):
    r = requests.get(url_mesh_json, timeout=5, allow_redirects=True)
    try:
        if r.status_code != 200:
            print '-!- URL-Error on ' + url_mesh_json
            return False

        try:
            r_json = json.loads(r.content)
            # print r_json['nodes']

        except:
            print '-!- JSON-Error on ' + url_mesh_json
            return False
    except:
        print '-!- Error at loading nodes from ' + url_mesh_json
        return False

    if r_json['nodes'] != None:
        print '-- Checking URL: ' + url_mesh_json
        print '-- {} Nodes found.'. format(len(r_json['nodes']))

        return_arr = []
        for node in r_json["nodes"]:
            if (node['addresses'] != None) and node['is_online'] == True:
                for address in node['addresses']:
                    if node['hostname'] != None and fqdn(node['hostname'], suffix) != False:
                        entry = {'host': fqdn(node['hostname'], suffix), 'addr': address}
                        return_arr.append(entry)
    return return_arr


a_meta_nodes = load_nodes('https://meta.ffbsee.net/data/meshviewer.json', 'ffbsee')
writeDnsmasqFile(a_meta_nodes, '/etc/dnsmasq.d/ffbsee_nodes_meta.conf', 'new')

a_mate_nodes = load_nodes('https://mate.ffbsee.net/data/meshviewer.json', 'ffbsee')
writeDnsmasqFile(a_mate_nodes, '/etc/dnsmasq.d/ffbsee_nodes_mate.conf', 'new')
