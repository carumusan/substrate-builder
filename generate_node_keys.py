#!/usr/bin/env python3

import requests
import argparse
import base64
from kubernetes import client, config
import subprocess

def main():
    parser = argparse.ArgumentParser(description='Add reserved nodes')
    parser.add_argument('--hostname', type=str, required=True)
    parser.add_argument('--node-type', dest="node_type", type=str, required=True)

    parsed_args = parser.parse_args()
    hostname = parsed_args.hostname
    node_type = parsed_args.node_type

    config.load_incluster_config()
    kubernetes_api = client.CoreV1Api()
    
    private_key_name = f"{hostname}-node-private-key-file"
    kubernetes_api.create_namespaced_config_map
    try:
        secret = kubernetes_api.read_namespaced_secret(name=private_key_name, namespace="default")
    except client.rest.ApiException as api_exception:
        if api_exception.status != 404:
            raise
        create_node_key(private_key_name, hostname, node_type, kubernetes_api)

def create_node_key(private_key_name, hostname, node_type, kubernetes_api: client.CoreV1Api):
    subkey_output = subprocess.run(["subkey", "-e", "generate-node-key", "node_key_file"], 
    capture_output=True, text=True)
    with open("node_key_file", "rb") as node_key_file:
        base64_encoded_data = base64.b64encode(node_key_file.read())
        base64_encoded_string = base64_encoded_data.decode('utf-8')
    secret = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {
            "name": private_key_name
        },
        "data": {
            "node_key_file": base64_encoded_string
        }
    }
    kubernetes_api.create_namespaced_secret("default", secret)

    config_map_name = f"{node_type}-multiaddresses"
    multiaddress_key = f"{hostname}_multiaddress"
    multiaddress_data = {
        multiaddress_key: f"/ip4/{hostname}/tcp/30333/p2p/{subkey_output.stdout}"
    }
    try:
        config_map = kubernetes_api.read_namespaced_config_map(name=config_map_name, 
        namespace="default")
        if multiaddress_key not in config_map.data:
            patch = {            
                "data": multiaddress_data
            }
            kubernetes_api.patch_namespaced_config_map(name=config_map_name, namespace="default", 
            body=patch)
    except client.rest.ApiException as api_exception:
        if api_exception.status != 404:
            raise
        config_map = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": config_map_name
            },
            "data": multiaddress_data
        }
        kubernetes_api.create_namespaced_config_map("default", config_map)

if __name__ == "__main__":
    main()
