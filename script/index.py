#!/usr/bin/python
#coding=utf-8
import os

def check_env():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    # 检查运行路径
   
    if (current_dir != "/root/ansible/script"):
        print("请把程序放在/root")
        exit()


check_env()

from python.upload_key import key_upload_taskStart, local_key_upload
import os
import re
import sys
from python.ansible_play import start_play_book

hosts_list = []
fail_file = None
success_file = None
# fail_list = []
# success_list = []

def Arrange():
    # 读取hosts文件内容
    file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "hosts.txt")

    hosts_file = open(file_dir, mode="r")
    hosts_content = hosts_file.read()
    p = re.compile(r"^[\s]*#.*")

    global hosts_list
    temp_hosts_list = hosts_content.split("\n")
    for host in temp_hosts_list:
        if host == "" or host == " ":
            continue
        result = re.match(p, host)
        # 判断是否是注释
        if result is not None:
            continue
        hosts_list.append(host)
    
    # 记录任务是否成功
    path = sys.path[0]
    fail_filedir = os.path.join(path, "fail.txt")
    success_filedir = os.path.join(path, "success.txt")
    global  fail_file
    global  success_file
    fail_file = open(fail_filedir, mode="w")
    success_file = open(success_filedir, mode="w")

def uploadKey():
    fail_file.write("*****密钥上传任务失败主机*****\n")
    success_file.write("*****密钥上传任务成功主机*****\n")
    # 整理需要copyID的主机
    for host in hosts_list:
        # 提取账户密码
        try:
            info_set = host.split()
            server_ip = info_set[0]
            server_passwd = info_set[1]
            try:
                server_port = info_set[2]
            except Exception as e:
                server_port = "22"
        except Exception as e:
            print("我在处理hosts.txt账户信息时出错了,以下是报错信息!\n%s" % (e))
            break
        print("正在处理 %s" % (server_ip))
        # 添加远程的
        remote_result = key_upload_taskStart(server_passwd, "root", server_ip, server_port)
        if remote_result is False:
            fail_file.write(server_ip+"\n")
            continue

        # 添加本地的
        local_result = local_key_upload(server_passwd, "root", server_ip, server_port)
        if local_result == True:
        # OK，还需要在本地登陆一下。
            local_result2 = start_play_book(server_ip, ["/root/ansible/script/ansible/install_pre.yaml"])
            if local_result2 == 0:
                success_file.write(server_ip+"\n")
            else:
                fail_file.write(server_ip+"\n")

        else:
            fail_file.write(server_ip+"\n")
            


def play(playBook, task_name):
    global fail_file
    global success_file
    fail_file.write("*****%s任务失败主机*****\n" % (task_name))
    success_file.write("*****%s任务成功主机*****\n" % (task_name))
   

    for host in hosts_list:
        try:
            host_split = host.split(" ")
        except Exception as e:
            pass
        host_ip = host_split[0]
        
        result = start_play_book(host_ip, [playBook])
        if result != 0:
            fail_file.write(host_ip + "\n")
        else:
            success_file.write(host + "\n")

    



   

def all_opt():
    uploadKey()
    play("/root/ansible/script/ansible/install_brogbackup.yaml", "安装brogback")
    play("/root/ansible/script/ansible/install_clamav.yaml", "安装clamav")

def menu():
    string = '''
        Hi，我能干以下事情
        1. 为hosts.txt清单所指向的服务器安装密钥。（此步骤非常重要，跳板机密钥必须存在于服务器中，如果密钥已经存在，则可以跳过）
        2. 安装BorgBackup并配置。（所有写在清单的服务器都会执行安装）
        3. 安装clamAV安全软件并配置。（所有写在清单的服务器都会执行安装）
        4. 一键完成所有(步骤1，2，3) 
	5. 退出
        '''
    print(string)

    opt = input("请输入操作：")
    opt = int(opt)


    if opt == 1:
        uploadKey()
    elif opt == 2:
        play("/root/ansible/script/ansible/install_brogbackup.yaml", "安装brogback")
    elif opt == 3:
        play("/root/ansible/script/ansible/install_clamav.yaml", "安装clamav")

    elif opt == 4:
        all_opt()
    elif opt == 5:
	    exit()
    else:
        print("我未理解你想进行什么操作？")


def main():
    Arrange()
    menu()



if __name__ == "__main__":
    main()
