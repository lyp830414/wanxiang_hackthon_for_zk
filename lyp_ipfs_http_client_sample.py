#!/usr/bin/env python

import ipfshttpclient
from ZeroKnowledge.Zk import Zk
import json

class IPFSClient:
    def __init__(self):
        self._client = ipfshttpclient.connect()

    def upload_test_file(self):
        
        hash = self._client.add('test.txt')['Hash']
        print('File Hash: ', hash)
        print('File Content: ', self._client.cat(hash))
            
        # Setup ZK Object
        zero = Zk()

        # Obtain ZK Secret
        secrets = zero.getSecret()
        print(secrets)

        # Commit ZK Data
        commits = zero.create(str(hash))
        
        with open('hash_val.txt', 'w') as f:
            f.write(str(commits))

        # Solve ZK Data
        trueString = zero.solve(secrets, commits)
        print(trueString)
        
        #print(commits)
        #with open('test_ipfs.txt', 'w') as f:
        #    raw = f.write(str(commits))
        
        return hash
        #value = self._client.cat(hash)
        #print('Ipfs Content: ', value)
        
        from py-ipfs-http-client import ipfshttpclient as cl
        client = cl.connect()
        hashv = client.add('test.txt')['Hash']
        print('!!!! File Hash: ', hashv)
        print('!!!! File Content: ', self._client.cat(hashv))
        
        client.close()

    def close(self):
        self._client.close()
    
    def getfile(self, hashv):
        self._client.get(hashv)

if __name__ == '__main__':
    ipfs_client = IPFSClient()
    hashv = ipfs_client.upload_test_file()
    ipfs_client.close()
    #import time
    #time.sleep(3)
    #ipfs_client = IPFSClient()
    #print('NOW TRY GET')
    #value = ipfs_client.getfile(hashv)
    #ipfs_client.close()
    #print(value)



