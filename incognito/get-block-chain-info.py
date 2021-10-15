#!/usr/bin/python3.9
import argparse
import datetime
import json
import os
import sys
import time
from builtins import int

import requests

default_endpoint = 'https://lb-fullnode.incognito.org/fullnode'
arg_parser = argparse.ArgumentParser(description="Get beacon and shard block info of a node")
optional_args = arg_parser.add_argument_group("Optional args")
optional_args.add_argument("-e", "--endpoint", default=default_endpoint)
optional_args.add_argument("-i", "--watchInterval", default=10, type=int)
optional_args.add_argument('-w', '--watch', action=argparse.BooleanOptionalAction, default=False)
optional_args.add_argument('-v', '--verbose', action=argparse.BooleanOptionalAction, default=False)
args = arg_parser.parse_args(sys.argv[1:])
change_indicators = ['>', '^', '<', 'v']

headers = {'Content-Type': 'application/json'}
pay_load = {"id": 1, "jsonrpc": "1.0", "method": "getblockchaininfo", "params": []}


def get_info(previous_data={}):
    endpoint = args.endpoint
    try:
        info = requests.post(endpoint, data=json.dumps(pay_load), headers=headers)
    except requests.ConnectionError as e:
        print(f"{e}")
        exit(0)
    os.system('clear') if args.watch else None
    if info.status_code != 200:
        print(f"{info} : {info.text}")
        return
    result = info.json()["Result"]
    best_blocks = result['BestBlocks']
    active_shard = result['ActiveShards']
    print_data = {}
    indicator = change_indicators.pop(0)
    change_indicators.append(indicator)

    if args.verbose:
        max_e_len = max([len(str(best_blocks[f'{i}']['Epoch'])) for i in range(-1, active_shard)])
        max_h_len = max([len(str(best_blocks[f'{i}']['Height'])) for i in range(-1, active_shard)])
        format_str = f"%3s : %{max_e_len}s | %{max_h_len}s | %s %s"
        for i in range(-1, active_shard):
            block = best_blocks[f'{i}']
            prev_data_line = previous_data.get(f'{i}')
            data_line = [f'{i}', block['Epoch'], block['Height'], block['Hash'], ""]
            if data_line[:-1] != prev_data_line[:-1]:
                data_line[-1] = indicator
            print_data[f'{i}'] = data_line
    else:
        format_str = "%3s : %s %s"
        for i in range(-1, active_shard):
            block = best_blocks[f'{i}']
            data_line = [f'{i}', block['Height'], ""]
            prev_data_line = previous_data.get(f'{i}', ["" * len(data_line)])
            if data_line[:-1] != prev_data_line[:-1]:
                data_line[-1] = indicator
            print_data[f'{i}'] = data_line

    print(f"Endpoint: {endpoint} {datetime.datetime.now().strftime('%H:%M:%S')}")
    for i in range(-1, active_shard):
        print(format_str % tuple(print_data[f'{i}']))
    return print_data


if args.watch:
    print(f"Get beacon and shard block height info every {args.watchInterval}s")
    prev_data = {}
    try:
        while True:
            prev_data = get_info(prev_data)
            time.sleep(args.watchInterval)
    except KeyboardInterrupt:
        exit()

get_info()
