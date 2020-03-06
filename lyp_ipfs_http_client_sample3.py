#!/usr/bin/env python
#coding=UTF-8

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
    print(r"生成MD5成功. 文件路径: " % fpath_md5)
    fout.flush()
    fout.close()

def generate_zk(zero, secrets, raw_data):
        # Setup ZK Object
        #zero = Zk()

        # Obtain ZK Secret
        #secrets = zero.getSecret()
        #print(secrets)

        # Commit ZK Data
        #print('NOW CREATE: data len: ', len(str(raw_data)))
        commits = zero.create(str(raw_data))
        #print('NOW CREATE END')

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
        
        print('\n++++ 步骤 1. 上传文件%s 到 IPFS....\n' %path)
        time.sleep(1)

        md5 = generate_file_md5value(path)   
        
        ts = datetime.datetime.now().timestamp()

        hash = self._client.add('test.txt')['Hash']
        print('上传完毕.\n')
        print('''文件: %s''' %path)
        print('''   - md5  Hash %s: ''' %(md5))
        print('''   - ipfs Hash %s: ''' %(hash))
        print('文件内容: ', self._client.cat(hash))
        
        
        data1 = {
                    "file": [
                                {
                                    "md5_hash": md5,
                                    "ipfs_hash": hash
                                }
                            ]
                }
        
        print('\n文件内容准备完成（如上所示）。数据长度: %d' %len(data1))
        print('''data1 = {
                   "file": [
                      {
                        "md5_hash": %s,
                        "ipfs_hash": %s
                      }
                    ]
                  }           
              ''' %(md5, hash))
        
        
        print('\n++++ 步骤 2. 根据上述数据产生你的零知识证明数据ZK1....\n')
        
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
        
        print('ZK1 生成完毕.\n')
        print('''ZK1 的数据长度: %d''' %len(str(zk1)))
        
        while True:
            y=input('\n--你是否愿意查看ZK1 数据的原始数据部分? [yes/no]')
            
            if not y:
                continue
            elif y.upper() in ('Y', 'YES'):
                print(str(zk1))
                print('\n')
                break
            elif y.upper() in ('N', 'NO'):
                print('\n好的.跳过.\n')
                break
            else:
                continue
        
        print('\n++++ 步骤 3. 用第一阶段零知识证明ZK1 数据产生你的下一个零知识证明ZK2 数据....\n')

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
        
        print('\nZK2 所需的原始数据部分如下所示. 数据长度: %d' %len(str(data2)))
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

        print('\n为产生零知识证明ZK2 所需的数据准备完毕.数据长度: %d' %len(str(zk1)))
        
        zk2 = generate_zk(zero, secrets, data2)
        print('ZK2 生成完毕.\n')
        print('''ZK2 数据长度: %d''' %len(str(zk2)))
        
        while True:
            y=input('\n--你是否愿意查看ZK2 数据的原始数据部分? [yes/no]')
            
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
        
        print('\n++++ 步骤 4. 用零知识证明数据 ZK1 和 ZK2 来产生你的验证文件file_zk.txt....\n')
        
        with open('file_zk.txt', 'a+') as f:
            f.write(path)
            f.write('\n')
            f.write(str(zk1))
            f.write(str(zk2))
        
        print('文件已产生.\n')
        print('你的file_zk.txt 数据格式如下(如有需要,请打开和查看此文件的原始数据):\n')
        print('%s\n' %path)
        print('<zk1>\n')
        print('<zk2>\n')
        

        print('\n++++ 步骤 5. 上传你的file_zk.txt 文件到IPFS....\n')
        time.sleep(1)
        
        hash = self._client.add('test.txt')['Hash']
        
        print('上传完毕.\n')
        print('''文件: %s''' %path)
        print('''   - md5  Hash: %s''' %(md5))
        print('''   - ipfs Hash: %s''' %(hash))
        print('文件内容: ', self._client.cat(hash))
        
        print('\n++++ 步骤 6. 用file_zk.txt 验证你的文件%s 的正确性....\n' %path)
        
        #print('ZK1 before: len: %d' %len(str(zk1)))
        zk1 = verify_file(zero, secrets, zk2)
        #print('OK, we got len new zk1: %d' %len(str(zk1)))
        #return
        orign_file_info = verify_file(zero, secrets, zk1)
        
        print('验证完毕.\n')
        print('文件内容: ', orign_file_info)
        time.sleep(1)

        #print(zk2)
        
        print('\n========================== 本次Demo 演示完成. 感谢您的参与 ============================\n')
        
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



