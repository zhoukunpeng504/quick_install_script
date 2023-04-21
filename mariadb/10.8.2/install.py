# coding:utf-8
__author__ = "zkp"
# create by zkp on 2023/4/20
# mariadb 10.8 docker版快速安装
import os
import sys
import time


mariadb_conf_content = '''[mariadb]  
character-set-server=utf8mb4
symbolic-links=0
innodb_buffer_pool_size = 256M
max_connections=5000
max_allowed_packet = 64M
innodb_flush_log_at_trx_commit = 0
innodb_file_per_table=ON
bulk_insert_buffer_size=10M
innodb_log_buffer_size=16M
server-id=1
log-bin=master
binlog_format=row
expire_logs_days = 1
max_binlog_size = 200M
slow_query_log=1
slow-query-log-file=/var/lib/mysql/mysql-slow.log
long_query_time=3
'''


if __name__ == '__main__':
    while 1:
        dir_ = input("输入要安装到目录(绝对路径)：")
        dir_ = dir_.strip()
        if not dir_.startswith("/"):
            print("目录输入错误！必须是绝对路径！")
            time.sleep(1)
        break
    while 1:
        password = input("输入数据库root密码：")
        password = password.strip()
        if password:
            break
        else:
            print("目录不能为空！")
            time.sleep(1)

    while 1:
        port = input("输入数据库要绑定的端口：(如：3306)")
        port = port.strip()
        try:
            port = int(port)
            assert port >3000
        except Exception as e:
            print("端口必须是大于300的数字！")
            time.sleep(1)
        else:
            break

    data_dir = os.path.join(dir_, 'mariadb_data')
    conf_dir = os.path.join(dir_, 'mariadb_conf')
    os.system("mkdir -p %s" % data_dir)
    os.system("mkdir -p %s" % conf_dir)
    with open(os.path.join(conf_dir,'my.cnf'), "w") as f:
        f.write(mariadb_conf_content)
    cmd = ("docker run --name mariadb_%s -p %s:3306  --restart=always "
              "-v %s:/var/lib/mysql "
              "-v %s:/etc/mysql/conf.d   "
              f"-e  MARIADB_ROOT_PASSWORD=%s  "
              "-d    mariadb:10.8.2 "  % (port,port,data_dir, conf_dir, password))
    print(cmd)
    os.system(cmd)
    print("mariadb 10.8.2安装成功！配置文件在容器内的/etc/mysql/conf.d目录，可自行优化配置！ ")
