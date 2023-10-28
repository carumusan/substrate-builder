#!/usr/bin/env python3

import argparse
import base64
import os
import subprocess

from kubernetes import client, config


def main():
    parser = argparse.ArgumentParser(description='Generate node keys')
    parser.add_argument('--hostname', type=str, required=True)
    parser.add_argument('--node-type', dest="node_type", type=str, required=True)
    parser.add_argument('--network', type=str, required=True)
    parser.add_argument('--command-file-volume', dest="command_file_volume", type=str, required=True)
    parser.add_argument('--kube-config', dest="kube_config", type=str)

    parsed_args = parser.parse_args()
    hostname = parsed_args.hostname
    node_type = parsed_args.node_type
    network = parsed_args.network
    command_file_volume = parsed_args.command_file_volume
    kube_config = parsed_args.kube_config
    command_arg_file_path = os.path.join(command_file_volume, "args")
    if kube_config:
        config.load_kube_config(kube_config)
    else:
        config.load_incluster_config()
    kubernetes_api = client.CoreV1Api()
    
    node_key_bytes, public_key = ensure_node_key(hostname, node_type, kubernetes_api)
    write_node_key_file(node_key_bytes, command_file_volume)
    ensure_config_map(hostname, node_type, public_key, network, kubernetes_api)

    if node_type == "sentry":
        set_args(command_arg_file_path, "validator-multiaddresses", "sentry", kubernetes_api)
    elif node_type == "validator":
        set_args(command_arg_file_path, "sentry-multiaddresses", "reserved-nodes", kubernetes_api)
        set_args(command_arg_file_path, "sentry-public-multiaddresses", "sentry-nodes", kubernetes_api)

    if node_type in ("sentry", "public-validator"):
        set_args(command_arg_file_path, f"{node_type}-public-multiaddresses", "public-addr", kubernetes_api, 
        f"{hostname}_multiaddress")

def set_args(command_arg_file_path, config_map_lookup, arg_name, kubernetes_api: client.CoreV1Api, key=None):
    try:
        config_map = kubernetes_api.read_namespaced_config_map(
        name=config_map_lookup, 
        namespace="default")
        multiaddress_data = config_map.data
        if key:
            multiaddresses = [multiaddress_data[key]]
        else:
            multiaddresses = multiaddress_data.values()
        if multiaddresses:
            command_line_args_list = [f"--{arg_name}={x}".rstrip() for x in multiaddresses]
            command_line_args = " " + " ".join(command_line_args_list)
            with open(command_arg_file_path, 'a') as command_arg_file:
                command_arg_file.write(command_line_args)
    except client.rest.ApiException as api_exception: 
        if api_exception.status != 404:
            raise

def write_node_key_file(node_key_bytes, command_file_volume):
    node_key_file_path = os.path.join(command_file_volume, "node-key-file")
    with open(node_key_file_path, 'wb') as node_key_file:
        node_key_file.write(node_key_bytes)

def ensure_node_key(hostname, node_type, kubernetes_api: client.CoreV1Api):
    private_key_name = f"{hostname}-node-key"
    try:
        secret = kubernetes_api.read_namespaced_secret(name=private_key_name, namespace="default")
    except client.rest.ApiException as api_exception:
        if api_exception.status != 404:
            raise
        secret = create_node_key(private_key_name, node_type, kubernetes_api)
    
    node_key_bytes = bytearray.fromhex(base64.b64decode(secret.data['node_key_file']).decode('utf-8'))
    public_key = base64.b64decode(secret.data['public_key']).decode('utf-8')
    return (node_key_bytes, public_key)

def create_node_key(private_key_name, node_type, kubernetes_api: client.CoreV1Api):
    subkey_output = subprocess.run(["subkey", "generate-node-key"], capture_output=True, text=True)
    secret = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {
            "name": private_key_name
        },
        "stringData": {
            "node_key_file": subkey_output.stdout.rstrip(),
            "public_key": subkey_output.stderr.rstrip()
        }
    }
    secret_data = kubernetes_api.create_namespaced_secret("default", secret)
    return secret_data

def ensure_config_map(hostname, node_type, public_key, network, kubernetes_api: client.CoreV1Api):
    config_map_name = f"{node_type}-multiaddresses"
    multiaddress_key = f"{hostname}_multiaddress"
    multiaddress_data = {
        multiaddress_key: f"/dns/{hostname}.tsukistaking-{node_type}/tcp/30333/p2p/{public_key}"
    }
    set_config_map(config_map_name, multiaddress_data, kubernetes_api)

    if node_type in ("sentry", "public-validator"):
        config_map_name = f"{node_type}-public-multiaddresses"
        public_multiaddress_data = {
            multiaddress_key: f"/dns/{hostname}.{network}.tsukistaking.com/tcp/30333/p2p/{public_key}"
        }
        set_config_map(config_map_name, public_multiaddress_data, kubernetes_api)

def set_config_map(config_map_name, multiaddress_data, kubernetes_api: client.CoreV1Api):
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
