#!/usr/bin/env python
from __future__ import absolute_import, division, print_function

import os
import time
import subprocess
import logging
from optparse import OptionParser
import ConfigParser

from util import json_decode, config_options_dict
from client_util import get_state
import submit

logger = logging.getLogger('client')


def get_ssh_state():
    try:
        filename = os.path.expanduser('~/glidein_state')
        return json_decode(open(filename).read())
    except Exception:
        logger.warn('error getting ssh state', exc_info=True)

def launch_glidein(cmd, params=[]):
    for p in params:
        cmd += ' --'+p+' '+str(params[p])
    print(cmd)
    if subprocess.call(cmd, shell=True):
        raise Exception('failed to launch glidein')

def get_running(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    return int(p.communicate()[0].strip())

def main():
    parser = OptionParser()
    parser.add_option('--config', type='string', default='cluster.config',
                      help="config file for cluster")
    (options, args) = parser.parse_args()
    config = ConfigParser.ConfigParser()
    config.read(options.config)
    config_dict = config_options_dict(config)

    # Importing the correct class to handle the submit
    if config_dict["Cluster"]["scheduler"] == "htcondor":
        scheduler = submit.SubmitCondor(config_dict)
    elif config_dict["Cluster"]["scheduler"] == "pbs":
        scheduler = submit.SubmitPBS(config_dict)
    elif config_dict["Cluster"]["scheduler"] == "slurm":
        scheduler = submit.SubmitSLURM(config_dict)
    else:
        raise Exception('scheduler not supported')

    # if "glidein_cmd" not in config_dict["Glidein"]:
    #     raise Exception('no glidein_cmd')
    if "running_cmd" not in config_dict["Cluster"]:
        raise Exception('no running_cmd')

    if config_dict["Mode"]["debug"]:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    while True:
        if config_dict["Glidein"]["ssh_state"]:
            state = get_ssh_state()
        else:
            state = get_state(config_dict["Glidein"]["address"])
        if state:
            try:
                glideins_running = get_running(config_dict["Cluster"]["running_cmd"])
            except Exception:
                logger.warn('error getting running job count', exc_info=True)
                continue
            i = 0
            for s in state:
                # Skipping CPU jobs for gpu only clusters
                if "gpu_only" in config_dict["Cluster"]:
                    if config_dict["Cluster"]["gpu_only"] and s["gpus"] == 0:
                        continue
                # skipping GPU jobs for cpu only clusters
                if "cpu_only" in config_dict["Cluster"]:
                    if config_dict["Cluster"]["cpu_only"] and s["gpus"] != 0:
                        continue
                if (i >= config_dict["Cluster"]["limit_per_submit"]
                    or i + glideins_running >= config_dict["Cluster"]["max_total_jobs"]):
                    logger.info('reached limit')
                    break
                scheduler.submit(s)
                i += 1
            logger.info('launched %d glideins', i)
        else:
            logger.info('no state, nothing to do')

        if int(config_dict["Glidein"]["delay"]) < 1:
            break
        time.sleep(config_dict["Glidein"]["delay"])


if __name__ == '__main__':
    main()
