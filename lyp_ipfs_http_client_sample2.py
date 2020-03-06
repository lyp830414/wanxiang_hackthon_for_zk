#!/usr/bin/env python

import ipfshttpclient
from ZeroKnowledge.Zk import Zk
import json,datetime
from hashlib import md5

def generate_file_md5value(fpath):
    m = md5()
    a_file = open(fpath, 'rb') 
    m.update(a_file.read())
    a_file.close()
    return m.hexdigest()
          
def generate_file_md5sumFile(fpath):
    fname = os.path.basename(fpath)
    fpath_md5 = "%s.md5" % fpath
    fout = open(fpath_md5, "w")
    fout.write("%s %s\n" % (generate_file_md5value(fpath), fname.strip()))
    print("generate success, fpath:%s") %fpath_md5
    fout.flush()
    fout.close()

def generate_zk(zero, secrets, raw_data):
        # Setup ZK Object
        #zero = Zk()

        # Obtain ZK Secret
        #secrets = zero.getSecret()
        #print(secrets)

        # Commit ZK Data
        print('NOW CREATE: data len: ', len(str(raw_data)))
        commits = zero.create(str(raw_data))
        print('NOW CREATE END')

        ## Solve ZK Data
        #trueString = zero.solve(secrets, commits)
        #if 'zk2' in trueString:
        #    print('trueString:', eval(trueString)['zk2'], ', len: ', len(trueString))
        
        return commits

def verify_file(zero, secrets, commits):
    trueString = zero.solve(secrets, commits)
    return trueString

class IPFSClient:
    def __init__(self):
        self._client = ipfshttpclient.connect()

    def upload_test_file(self, path):
        import time
        
        print('\n++++ Step 1. Send file %s to IPFS....\n' %path)
        time.sleep(1)

        md5 = generate_file_md5value(path)   
        
        ts = datetime.datetime.now().timestamp()

        hash = self._client.add('test.txt')['Hash']
        print('Done.\n')
        print('''File: %s''' %path)
        print('''   - md5  Hash %s: ''' %(md5))
        print('''   - ipfs Hash %s: ''' %(hash))
        print('File Content: ', self._client.cat(hash))
        
        
        data1 = {
                    "file": [
                                {
                                    "md5_hash": md5,
                                    "ipfs_hash": hash
                                }
                            ]
                }
        
        print('\nFile data prepared as following. Len of data: %d' %len(data1))
        print('''data1 = {
                   "file": [
                      {
                        "md5_hash": %s,
                        "ipfs_hash": %s
                      }
                    ]
                  }           
              ''' %(md5, hash))
        
        
        print('\n++++ Step 2. Generate your ZK1 with prepared data above....\n')
        
        time.sleep(1)
        
        
        # Setup ZK Object
        zero = Zk()

        # Obtain ZK Secret
        secrets = zero.getSecret()
        
        zk1 = generate_zk(zero, secrets, data1)
        #print('FAKE HERE BEGIN')
        #import sys
        #orign_file_info = verify_file(zero, secrets, zk1)
        #print('FAKE HERE END: ', orign_file_info)
        #sys.exit(0)
        
        print('Done.\n')
        print('''len of ZK1 data: %d''' %len(str(zk1)))
        
        while True:
            y=input('\n--Do you want to view the raw data of ZK1 ? [yes/no]')
            
            if not y:
                continue
            elif y.upper() in ('Y', 'YES'):
                print(str(zk1))
                print('\n')
                break
            elif y.upper() in ('N', 'NO'):
                print('\nOk skip.\n')
                break
            else:
                continue
        
        print('\n++++ Step 3. Generate your ZK2 with ZK1....\n')

        time.sleep(1)
        
        data2 = {   
                    "zk1":  zk1,
                    "zk2":  [
                            {
                                "md5_hash": md5,
                                "add_time": ts
                            }
                        ]
                }
        
        print('\nFile data prepared as following. Len of data: %d' %len(str(data2)))
        print('''data2 = {   
                   "zk1": <zk1>,
                   "zk2": [
                     {
                       "md5_hash": %s,
                       "add_time": %s
                     }
                   ]
                }
               ''' %(md5, ts))

        print('\nZK1 data prepared for ZK: Len of data: %d' %len(str(zk1)))
        
        zk2 = generate_zk(zero, secrets, data2)
        print('Done.\n')
        print('''len of ZK2 data: %d''' %len(str(zk2)))
        
        while True:
            y=input('\n--Do you want to view the raw data of ZK2 ? [yes/no]')
            
            if not y:
                continue
            elif y.upper() in ('Y', 'YES'):
                print(str(zk2))
                print('\n')
                break
            elif y.upper() in ('N', 'NO'):
                print('\nOk skip.\n')
                break
            else:
                continue
        
        print('\n++++ Step 4. Generate your file_zk.txt file with ZK1 and ZK2....\n')
        
        with open('file_zk.txt', 'a+') as f:
            f.write(path)
            f.write('\n')
            f.write(str(zk1))
            f.write(str(zk2))
        
        print('Done.\n')
        print('Your file_zk.txt data(Please check the file raw_data if need):\n')
        print('%s\n' %path)
        print('<zk1>\n')
        print('<zk2>\n')
        

        print('\n++++ Step 5. Upload your file_zk.txt file to IPFS....\n')
        time.sleep(1)
        
        hash = self._client.add('test.txt')['Hash']
        
        print('Done.\n')
        print('''File: %s''' %path)
        print('''   - md5  Hash: %s''' %(md5))
        print('''   - ipfs Hash: %s''' %(hash))
        print('File Content: ', self._client.cat(hash))
        
        print('\n++++ Step 6. Verify your file %s with file_zk.txt....\n' %path)
        
        print('ZK1 before: len: %d' %len(str(zk1)))
        zk1 = verify_file(zero, secrets, zk2)
        print('OK, we got len new zk1: %d' %len(str(zk1)))
        #return
        orign_file_info = verify_file(zero, secrets, zk1)
        
        print('Done.\n')
        print('File Content: ', orign_file_info)
        time.sleep(1)

        #print(zk2)
        
        print('\n========================== OK. Demo end. Thank you ============================\n')
        
        return hash

    def close(self):
        self._client.close()
    
    def getfile(self, hashv):
        self._client.get(hashv)

if __name__ == '__main__':
    ipfs_client = IPFSClient()
    hashv = ipfs_client.upload_test_file('test.txt')
    ipfs_client.close()
    #import time
    #time.sleep(3)
    #ipfs_client = IPFSClient()
    #print('NOW TRY GET')
    #value = ipfs_client.getfile(hashv)
    #ipfs_client.close()
    #print(value)



