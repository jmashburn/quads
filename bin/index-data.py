#!/usr/bin/env python

import argparse
import logging
import os
import sys
import yaml
import re

logger = logging.getLogger('quads-validation')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# used to load the configuration for quads behavior
def quads_load_config(quads_config):
    try:
        with open(quads_config, 'r') as config_file:
            try:
                quads_config_yaml = yaml.safe_load(config_file)
            except Exception, ex:
                print "quads: Invalid YAML config: " + quads_config
                exit(1)
    except Exception, ex:
        print ex
        exit(1)
    return(quads_config_yaml)

def main(argv):
    quads_config_file = os.path.dirname(__file__) + "/../conf/quads.yml"
    quads_config = quads_load_config(quads_config_file)

    if "data_dir" not in quads_config:
        print "quads: Missing \"data_dir\" in " + quads_config_file
        exit(1)

    if "install_dir" not in quads_config:
        print "quads: Missing \"install_dir\" in " + quads_config_file
        exit(1)

    if "quads_base_url" not in quads_config:
        print "quads: Missing \"quads_base_url\" in " + quads_config_file
        exit(1)

    if "elastic_host" not in quads_config:
        print "quads: Missing \"elastic_host\" in " + quads_config_file
        exit(1)

    if "elastic_port" not in quads_config:
        print "quads: Missing \"elastic_port\" in " + quads_config_file
        exit(1)

    sys.path.append(quads_config["install_dir"] + "/lib")
    sys.path.append(os.path.dirname(__file__) + "/../lib")
    from Elastic import Elastic

    parser = argparse.ArgumentParser(description='Index result file into Elastic')
    parser.add_argument('--resultfile',dest='resultfile',default=None, type=str, help="Validation result file generated by quads")
    parser.add_argument('--index',dest='index',default=None, type=str, help="Elastic index")
    parser.add_argument('--type',dest='type',default=None, type=str, help="Elastic type")
    parser.add_argument('--owner',dest='owner',default=None, type=str, help="Owner of the cloud")
    parser.add_argument('--ticket',dest='ticket',default=None, type=str, help="Ticket for the cloud")
    parser.add_argument('--cloud',dest='cloud',default=None, type=str, help="Cloud id")
    _result = None
    options = parser.parse_args()
    try :
        with open(options.resultfile, 'r') as validation_result:
            _result = validation_result.read()
    except Exception, e:
        print "Error reading in result file from validations : {}".format(e)
        exit(1)

    hosts = []
    if len(_result.split()) > 0 :
        for line in _result.split() :
            if re.findall(r'(.*\.)+',line):
                hosts.append(line)
    if len(hosts) < 1 :
        print "Error no hosts could be read in."
        exit(1)

    payload = { "message": _result,
                "hosts": hosts,
                }
    if options.owner :
        payload["owner"] = options.owner
    if options.cloud :
        payload["cloud"] = options.cloud
    if options.ticket :
        payload["ticket"] = options.ticket

    if not options.index :
        print "Missing index"
        exit(1)
    if not options.type :
        print "Missing type"
        exit(1)

    es = Elastic(quads_config['elastic_host'],quads_config['elastic_port'])
    es.index(payload,options.index,options.type)

if __name__ == "__main__":
    main(sys.argv[1:])