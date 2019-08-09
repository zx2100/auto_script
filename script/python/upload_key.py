#coding=utf-8

import pexpect
import sys
import os
import paramiko




def putPublicKey(publicKey, user, server, port, password):

    child = pexpect.spawn("/usr/bin/ssh-copy-id -p %s -i %s %s@%s" %(port, publicKey, user, server))

    index = child.expect(["yes/no", "password", "exist", pexpect.exceptions.EOF, pexpect.TIMEOUT], timeout=5)

    # 匹配结果，如果匹配到4（对应列表），则匹配上超时,默认5s超时
    # 1是成功添加 2是添加失败 3是已经添加
    if index == 4:
        return index
    while index != 4:
        if index == 0:
            # 出现这个之后，输入yes
            child.sendline("yes")
            # 此句需要重新运行，刷新index的值
            index = child.expect(["yes/no", "password", "exist", pexpect.exceptions.EOF, pexpect.TIMEOUT],
                                 timeout=5)
            continue
        elif index == 1:
            child.sendline(password)
            result = child.expect(["added", "exist", pexpect.TIMEOUT], timeout=3)
            if (result == 0 or result == 1) :
                child.close()
                return 1
            else:
                child.close()
                return 2

        else:
            return 3

# 返回1是成功添加 2是失败 3是已经添加


def key_upload_taskStart(password, user="root", servers="127.0.0.1", port="22" ):
    publicKey = "/root/.ssh/id_rsa.pub"  # 指定要上传的公钥
    # 如果指定的公钥不存在，自动创建
    direname = os.path.dirname(publicKey)
    if not os.path.exists(publicKey):

        print("指定公钥不存在，将自动生成私钥和公钥，路径为：%s" % (direname))
        child = pexpect.spawn("ssh-keygen -t rsa -P '' -f %s/id_rsa" % (direname))
        child.expect(pexpect.exceptions.EOF)
        child.close(force=True)
        print("已生成私钥和公钥")

    put_result = putPublicKey(publicKey, user, servers, port, password)
    if put_result == 1:
        print("\t远程公钥已经添加")
        return True
    elif put_result == 2:
        print("\t远程公钥添加失败")
        return False
    elif put_result == 3:
        print("\t远程公钥已经添加")
        return True
    else:
        return False




def local_key_upload(password, user="root", servers="127.0.0.1", port="22" ):
    publicKey = "/root/.ssh/id_rsa.pub"  # 指定要上传的公钥
    # 如果指定的公钥不存在，自动创建
    direname = os.path.dirname(publicKey)
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    #p_key = paramiko.RSAKey.from_private_key_file("/root/.ssh/id_rsa")
    try:
        ssh.connect(hostname=servers, port=int(port), username='root', password=password)
    except Exception as e:
        print("本地登陆失败，本地密钥上传失败")
        return False
    # 检查是否有公钥
    stdin, stdout, stderr = ssh.exec_command("/bin/ls /root/.ssh/id_rsa.pub")
    result = stdout.read().decode('utf-8', 'ignore')
    # 如果没有则创建

    if result is None or result == "":
        ssh.exec_command("/usr/bin/ssh-keygen -t rsa -P '' -f %s/id_rsa" % (direname))
        stdin, stdout, stderr = ssh.exec_command("/bin/ls /root/.ssh/id_rsa.pub")
        if stdout.read().decode('utf-8', 'ignore'):
            print("本地公钥生成成功")
    stdin, stdout, stderr = ssh.exec_command("/bin/cat /root/.ssh/id_rsa.pub")
    localKey = stdout.read().decode('utf-8')
    stdin, stdout, stderr = ssh.exec_command("/bin/cat /root/.ssh/authorized_keys")
    all_key = stdout.read().decode('utf-8')
    #判断是否已经添加?

    temp =  all_key.find(localKey)

    if temp == -1:
        ssh.exec_command("/bin/cat /root/.ssh/id_rsa.pub >> /root/.ssh/"
                                                   "authorized_keys")


    print("\t本地密钥已经添加")
    ssh.close()
    return True

if __name__ == '__main__':
    key_upload_taskStart("523569","root", "192.168.30.22")
