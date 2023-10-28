#!/usr/bin/env python3

import requests

def main():
    data = {
        "id": 1,
        "jsonrpc":"2.0",
        "method": "author_rotateKeys",
        "params":[]
    }
    json_result = requests.post(f"http://localhost:9944", json=data).json()
    print(json_result['result'])

if __name__ == '__main__':
    main()
