import json
import commands
import subprocess
import os
import pprint
import logging
import sys
import re

#-*-coding:utf-8-*-


conf_file = '../conf/company.json'

def set_logging_config(log_file, mode):
    '''
    set logging format and level
    '''
    logging.basicConfig(level=logging.DEBUG,
                        format ='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
                        filename = log_file,
                        filemode = mode)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    logging.info("output log both screen and " + log_file)



def list2str_by_key(src_list, key, sep=','):
    '''
    extract company_id list string from company dict list
    '''
    str_list = []

    for item in src_list:

        if key in item.keys():
            str_list.append(item[key])

    return sep.join(str_list)


def parse_json_conf():
    '''
    read conf data from json file
    '''
    logging.info("loading json conf : " + conf_file)
    with open(conf_file) as json_file:
        json_data = json.load(json_file)

        res = json.dumps(json_data,
                         indent=4,
                         ensure_ascii=False,
                         sort_keys=True).encode('utf-8')

        logging.info("loaded json data : " + res)

        return json_data



def complete_cmd_company(cmd, company_list):
    '''
    concate cmd string and company_id
    '''
    logging.info("complete cmd company")
    cmd_list = [ cmd.format(**company) for company in company_list ]
    return cmd_list



def exec_cmd(cmd):
    '''
    execute bash cmd
    '''
    logging.info("execing cmd : " + str(cmd))

    exec_output = subprocess.check_output(cmd, shell=True,
                                          stderr=subprocess.STDOUT)

    if re.search(r'Job not Successful',exec_output):
        logging.error("exec cmd error : " + str(cmd))
        logging.error("error output : " + exec_output)
        raise RuntimeError("cmd exec error : " + str(cmd))

    else:
        logging.info("exec output : " + exec_output)


def flatten_list(nested_list):
    '''
    flatten a nested_list
    '''
    logging.info("flatten nested list" + str(nested_list))
    return [y for l in nested_list for y in flatten_list(l)] if type(nested_list) is list else [nested_list]

def exception_handle(e):
    '''
    exception info log
    '''
    logging.exception(e)
    logging.error(e, exc_info=1)
    logging.critical(e, exc_info=1)
    sys.exit(-1)

def update_conf(json_data):
    '''
    write json data back to conf file
    '''
    logging.info("updating json conf")
    with open(conf_file, 'w') as json_file:
        res = json.dumps(json_data,
                         indent=4,
                         ensure_ascii=False,
                         sort_keys=True).encode('utf-8')

        logging.info("writing into json conf " + res)
        json_file.write(res)


def _dump(json_data):
    '''
    dump json data (for test)
    '''
    print json.dumps(json_data, indent=4).encode('utf-8')


def _test():
    '''
    test function
    '''




if __name__ == "__main__":
    try:
        _main(sys.argv)
    except:
        error = sys.exc_info()[1]
        if len(str(error)) > 2:
            print(error)
