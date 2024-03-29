#!/usr/bin/env python3

import argparse

import requests
from kubernetes import client, config


def main():
    parser = argparse.ArgumentParser(description='Add reserved nodes')
    parser.add_argument('--label', type=str, required=True)
    parser.add_argument('--output-file', dest='output_file_path', type=str, required=True)
    parser.add_argument('--command-line-arg', dest='command_line_arg', type=str, default="reserved-nodes")

    parsed_args = parser.parse_args()
    label = parsed_args.label
    output_file_path = parsed_args.output_file_path
    command_line_arg = parsed_args.command_line_arg
    config.load_incluster_config()

    kubernetes_api = client.CoreV1Api()
    
    data = {
        "id": 1,
        "jsonrpc":"2.0",
        "method": "system_networkState",
        "params":[]
    }
    reserved_node_pods = kubernetes_api.list_namespaced_pod("default", label_selector=label, watch=False, timeout_seconds=10)
    reserved_node_ips = [item.status.pod_ip for item in reserved_node_pods.items]
    with open(output_file_path, 'w') as output_file:
        for reserved_node_ip in reserved_node_ips:
            json_result = requests.post(f"http://{reserved_node_ip}:9933", json=data).json()
            peerId = json_result['result']['peerId']
            output_file.write(f" --{command_line_arg}=/ip4/{reserved_node_ip}/tcp/30333/p2p/{peerId}")

if __name__ == '__main__':
    main()
