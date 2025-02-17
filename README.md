# 测试情况：
1. Centos7-minimal:ok
2. Centos6-minimal:ok
3. Debian9-minimal:ok
4. Debian8-i386-minimal:ok
5. Ubuntu14.04-minimal:ok
6. Ubuntu16.04-minimal:ok

> 脚本是串行执行的，一台一台依次执行，可以多找几台跳板机把500台分成N批，这样会快好多

----------------
# 执行逻辑
脚本会在跳板机上生成密钥，然后复制密钥到hosts.txt文件中定义的服务器中，当密钥复制完成后，会根据脚本事先定义好的任务，自动把任务分发到各服务器上执行。在任务执行时有时候需要访问互联网网下载所需文件。根据以上所述，脚本成功执行需要一些前提条件，并应该满足这些条件。
1. 所有服务器能访问互联网
2. 所有服务器的yum或apt命令能正常运行(即能使用这些命令安装程序包)
3. 所有服务器的SSH服务可用，root账户能使用密钥登陆
4. 需要跳板机，并且跳板机能直接访问hosts.txt文件中定义的服务器
5. 脚本只能在linux上执行，被执行的服务器也必须是linux系统
6. 时间仓促，脚本对运行位置有硬性要求，必须运行在/root目录下。
7. 跳板机以root账户运行此脚本

最好找一台能访问所有服务器的跳板机来执行，这样会省事。
如果出现错误时大多数是因为环境问题，根据报错提示修复后重新运行。



# 如何使用？
在脚本目录下（能看到index.py的目录），此目录下有个hosts.txt文件，把IP和密码填入去后，运行index.py，根据交互式的提示，完成自动化安装即可。全程只需要在跳板机上操作，无需登陆到具体的某一台服务器。再次提醒，自动化安装依赖密钥文件登陆，请保证跳板机能用密钥直接登陆服务器。

## 当运行出错时

1.任务在执行结束后，会判断是否执行成功，执行成功的主机会记录在当前目录的success.txt文件中，失败则记录在fail.txt文件中，当报错主机的问题解决以后，把fail.txt的主机，重新跑一遍就可以了。

2.如果有卡死情况(尤其更新病毒库)，可以取消运行，然后重新跑，多次运行不会有副作用



*******************************************************************************************************
# 更详细的
如果需要后期修改配置，下面的信息应该能帮助到你
**************
## 我的工作内容是什么？
脚本能完成clamav和brogbackup的安装和基本配置，还会在hosts.txt里指定的服务器安装2个密钥文件，1个密钥文件是跳板机的，另一个密钥是自身的，自身的密钥主要用于BorgBackup备份。



## 我是如何工作的？


完成自动化安装程序是由ansible来进行的，脚本已经最大限度的保障其幂等性，多次运行应该是没问题的，然后通过index.py这个脚本把这些自动化任务集成在一起。




## 关于BorgBackup备份

直接使用BorgBackup来备份数据操作不是很友好，因此脚本在此基础上额外安装了一个叫'borgmatic'的工具，这个工具能简化BorgBackup的操作。官方文档在此：https://projects.torsion.org/witten/borgmatic
建议手动备份和恢复也使用这个工具，另外，写在任务计划的定时任务，也是这个工具提供的命令

默认备份/etc/ 和/root 这2个目录

每台服务器默认会生成/backup目录，在此目录中会生成一个和服务器名字同名的目录，备份的数据会存放在这里，数据默认保存7天。* 强烈建议后期对备份策略进行修改，因为每台服务器的备份数据都保存在本地磁盘上，这样的操作几乎没什么意义。*应该找一台服务器专门来负责保存备份数据。又或者对服务器的/backup目录挂载成一个nfs或者其他的共享存储。

如果想修改备份配置，配置文件的路径是：/etc/borgmatic/config.yaml
更建议的做法是在脚本中修改配置模板，修改好后，重新跑一遍。结果是一样的，脚本的好处是能同时批量对多台服务器进行修改~


几个常用命令：
查看备份：borgmatic list
进行备份：borgmatic v 1
恢复备份：borgmatic extract --archive xxxxxxx要恢复备份名称

另外，如果使用原生命令Borg来管理备份的话。请加上主机名，例如：

查看备份：
borg list ssh://root@localhost/backup/debian.borg

最后附上Borgbackup官方文档:https://borgbackup.readthedocs.io


## 关于clamav杀毒

安装过程中，会有一个更新病毒库的过程，这个过程会联系外国服务器，因此可能因为网络环境原因导致更新失败，此时可以手动使用命令：/usr/local/clamAV/bin/freshclam手动更新。又或者重跑一遍脚本。



BorgBackup和ClamAV都加入到计划任务中，每天凌晨1时运行。