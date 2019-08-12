#!/bin/bash

# Centos7.3安装pip脚本
#判断是否安装python pip

/usr/bin/pip --version &> /dev/null

if [ $? != 0 ]
then
    yum makecache
    yum install -y python-pip
    if [ $? == 0 ]
    then
        echo "安装pip成功"
    else
        echo "安装pip失败"
    fi
else
    echo "已安装pip"
fi

# 升级pip
/usr/bin/pip install --upgrade pip


# 导入包
/usr/bin/pip install -r /root/ansible/packages.txt