#!/usr/bin/env python

import ipfshttpclient

class IPFSClient:
    def __init__(self):
        self._client = ipfshttpclient.connect()

    def upload_test_file(self):
        hash = self._client.add('test.txt')['Hash']
        print('File Hash: ', hash)
        print('File Content: ', self._client.cat(hash))

    def close(self):
        self._client.close()


if __name__ == '__main__':
    ipfs_client = IPFSClient()
    ipfs_client.upload_test_file()
    ipfs_client.close()
