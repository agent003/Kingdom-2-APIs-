import ConfigParser
from slacker import Slacker
import time
import yaml
import urllib
import requests
import json

config = ConfigParser.ConfigParser()
config.read('slacker_data.ini')
slacker_token = config.get('slacker','token')
slack = Slacker(slacker_token)

down_list = {}
result_variation = {}

def get_data():
    f = open('apis.yml','r')
    cfg = yaml.load(f)
    f.close()
    return cfg

def fetch_thing(url, params, method):
    params = urllib.urlencode(params)
    if method=='POST':
        f = urllib.urlopen(url, params)
    else:
        f = urllib.urlopen(url+'?'+params)
    return json.loads(f.read())

def get_status(url,method):
    s_code = 0
    if(method == 'POST'):
        try:
            r = requests.post(url)
            s_code = r.status_code
        except:
            s_code = 111
    else:
        try:
            r = requests.get(url)
            s_code = r.status_code
        except:
            s_code = 111
    return s_code
        

def get_params(api,mode):
    result = []
    keys = api.keys()
    for values in keys:
        if mode in values:
            result.append(values)
    return result

def verify_match(dict1,dict2):
    keys = dict1.keys()
    flag = 0
    for i in keys:
        if(str(dict1[i]) != str(dict2[i])):
            flag = 1
            break
    return flag
def get_string(dict1,dict2):
    message1 = ''
    message2 = ''
    keys = dict1.keys()
    for i in keys:
        message2 += str(i) + ' : '
        message2 += dict2[i] + '\n'
        message1 += str(i) + ' : '
        message1 += str(dict1[i]) + '\n'
    return [message1,message2]
def notify_developer_url(status_code,endpoint,method,maintainer):
    if(status_code == 200):
        message = 'Site with url: ' + str(endpoint) + ' Method : ' + method + ' is up. Status Code returned: ' + str(status_code)
        slack.chat.post_message(str('@' + maintainer), message)
    else:
        message = 'Site with url: ' + str(endpoint) + ' Method : ' + method + ' is having issue. Status Code returned: ' + str(status_code)
        slack.chat.post_message(str('@' + maintainer), message)

def notify_developer_result(name,payload,message1,maintainer,status):
    if(status == 'down'):
        message = 'Variation in result was detected for '+name+' for ' + payload + '\n response recieved : \n'+message1[1] + ' response expected :' + message1[0]
        slack.chat.post_message(str('@' + maintainer), message)
    else:
        message = 'Variation in result was rectified for '+name+' for ' + payload + '\nresponse recieved : \n'+message1[1] + ' response expected :' + message1[0]
        slack.chat.post_message(str('@' + maintainer), message)
        


def manage_down(name,payload):
    if(name not in result_variation):
        result_variation[name] = [payload]
    else:
        result_variation[name].append(payload)

def check_results(api,name):
    status_code = get_status(api['endpoint'],api['method'])
    if(status_code != 200):
        if(name in down_list):
            pass
        else:
            down_list[name] = 'down'
            notify_developer_url(status_code,api['endpoint'],api['method'],api['maintainer'])
    else:
        if(name in down_list):
            del down_list[name]
            notify_developer_url(status_code,api['endpoint'],api['method'],api['maintainer'])
        total_payload = get_params(api,'payload')
        for payload in total_payload:
            result = fetch_thing(api['endpoint'],api[payload],api['method'])
            if(verify_match(api[str('output' + payload[-1])],result) == 1):
                if(name in result_variation):
                    if(payload not in result_variation[name]):
                        result_variation.append(payload)
                        notify_developer_result(name,payload,get_string(api[str('output' + payload[-1])],result),api['maintainer'],'down')
                else:
                    result_variation[name] = [payload]
                    notify_developer_result(name,payload,get_string(api[str('output' + payload[-1])],result),api['maintainer'],'down')
            else:
                if(name in result_variation):
                    if(payload in result_variation[name]):
                        del result_variation[name][result_variation[name].index(payload)]
                        notify_developer_result(name,payload,get_string(api[str('output' + payload[-1])],result),api['maintainer'],'up')


def main_loop():
    while(True):
        master_list = get_data()
        total_api = master_list.keys()
        for api in total_api:
            try:
                check_results(master_list[api],api)
            except:
                print 'Network issue maybe'

main_loop()
