#!/usr/bin/env python3

import requests
import argparse
from kubernetes import client, config

def main():
    parser = argparse.ArgumentParser(description='Add reserved nodes')
    parser.add_argument('--label', type=str, required=True)
    parser.add_argument('--output-file', dest='output_file_path', type=str, required=True)

    parsed_args = parser.parse_args()
    label = parsed_args.label
    output_file_path = parsed_args.output_file_path
    config.load_incluster_config()

    kubernetes_api = client.CoreV1Api()
    
    data = {
        "id": 1,
        "jsonrpc":"2.0",
        "method": "system_networkState",
        "params":[]
    }
    reserved_node_pod_stream = kubernetes_api.list_namespaced_pod("default", label_selector=label, watch=True)
    with open(output_file_path, 'w') as output_file:
        for reserved_node_pod in reserved_node_pod_stream:
            reserved_node_ips = [item.status.pod_ip for item in reserved_node_pod.items]
            print(reserved_node_pod)
            for reserved_node_ip in reserved_node_ips:
                json_result = requests.post(f"http://{reserved_node_ip}:9933", json=data).json()
                peerId = json_result['result']['peerId']
                output_file.write(f" --reserved-nodes=/ip4/{reserved_node_ip}/tcp/30333/p2p/{peerId}")

if __name__ == '__main__':
    main()
