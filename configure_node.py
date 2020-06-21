#!/usr/bin/env python3

import requests
import argparse
import base64
from kubernetes import client, config
import subprocess
import os 

def main():
    parser = argparse.ArgumentParser(description='Generate node keys')
    parser.add_argument('--hostname', type=str, required=True)
    parser.add_argument('--node-type', dest="node_type", type=str, required=True)
    parser.add_argument('--command-file-volume', dest="command_file_volume", type=str, required=True)

    parsed_args = parser.parse_args()
    hostname = parsed_args.hostname
    node_type = parsed_args.node_type
    command_file_volume = parsed_args.command_file_volume
    command_arg_file_path = os.path.join(command_file_volume, "args")

    config.load_incluster_config()
    kubernetes_api = client.CoreV1Api()
    
    node_key_data, public_key = ensure_node_key(hostname, node_type, kubernetes_api)
    write_node_key_file(node_key_data, command_file_volume)
    ensure_config_map(hostname, node_type, public_key, kubernetes_api)

    if node_type == "sentry":
        set_args(command_arg_file_path, "validator", "sentry", kubernetes_api)
    elif node_type == "validator":
        set_args(command_arg_file_path, "sentry", "reserved-nodes", kubernetes_api)

def set_args(command_arg_file_path, node_type, arg_name, kubernetes_api: client.CoreV1Api):
    try:
        config_map = kubernetes_api.read_namespaced_config_map(
        name=f"{node_type}-multiaddresses", 
        namespace="default")
        multiaddresses = config_map.data.values()
        if multiaddresses:
            command_line_args_list = [f"--{arg_name}={x}".rstrip() for x in multiaddresses]
            command_line_args = " " + " ".join(command_line_args_list)
            with open(command_arg_file_path, 'w') as command_arg_file:
                command_arg_file.write(command_line_args)
    except client.rest.ApiException as api_exception: 
        if api_exception.status != 404:
            raise

def write_node_key_file(node_key_data, command_file_volume):
    node_key_file_path = os.path.join(command_file_volume, "node-key-file")
    with open(node_key_file_path, 'wb') as node_key_file:
        node_key_file.write(node_key_data)

def ensure_node_key(hostname, node_type, kubernetes_api: client.CoreV1Api):
    private_key_name = f"{hostname}-node-key"
    try:
        secret = kubernetes_api.read_namespaced_secret(name=private_key_name, namespace="default")
    except client.rest.ApiException as api_exception:
        if api_exception.status != 404:
            raise
        secret = create_node_key(private_key_name, node_type, kubernetes_api)
    
    node_key_base64_bytes = secret.data['node_key_file'].encode('utf-8')
    node_key_data = base64.decodebytes(node_key_base64_bytes)

    public_key_bytes = base64.b64decode(secret.data['public_key'])
    public_key = public_key_bytes.decode('utf-8')
    return (node_key_data, public_key)

def create_node_key(private_key_name, node_type, kubernetes_api: client.CoreV1Api):
    subkey_output = subprocess.run(["subkey", "-e", "generate-node-key", "generated_key_file"], 
    capture_output=True, text=True)
    with open("generated_key_file", "rb") as node_key_file:
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
        },
        "stringData": {
            "public_key": subkey_output.stdout.rstrip()
        }
    }
    secret_data = kubernetes_api.create_namespaced_secret("default", secret)
    return secret_data

def ensure_config_map(hostname, node_type, public_key, kubernetes_api: client.CoreV1Api):
    config_map_name = f"{node_type}-multiaddresses"
    multiaddress_key = f"{hostname}_multiaddress"
    multiaddress_data = {
        multiaddress_key: f"/dns/{hostname}.tsukistaking-{node_type}/tcp/30333/p2p/{public_key}"
    }
    try:
        config_map = kubernetes_api.read_namespaced_config_map(name=config_map_name, 
        namespace="default")
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
