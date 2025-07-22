#coding:utf-8
import sys
import os
import time


if __name__ == '__main__':
    mysql_host = '127.0.0.1'
    mysql_port = '13306'
    mysql_user = 'root'
    mysql_password = '123456'
    current_dir = os.path.abspath(os.path.dirname(__file__))
    # 安装包下载及解压
    #os.system("rm -rf apache-hive-3.1.3-bin.tar.gz")
    os.system("rm -rf /data/apache-hive-3.1.3-bin")
    os.system("wget http://starchain.cn.gcimg.net/apache-hive-3.1.3-bin.tar.gz  -O  apache-hive-3.1.3-bin.tar.gz")
    os.system("cd /data && cp %s/apache-hive-3.1.3-bin.tar.gz  /data/apache-hive-3.1.3-bin.tar.gz" % current_dir)
    os.system("cd /data && tar -zxvf apache-hive-3.1.3-bin.tar.gz")
    # 删除配置文件
    os.system("rm -rf /data/apache-hive-3.1.3-bin/conf")
    os.system("rm -rf /data/apache-hive-3.1.3-bin/lib/guava-*")
    os.system("rm -rf /data/apache-hive-3.1.3-bin/lib/mysql-connector-*")
    # 模板配置文件覆盖
    os.system("mkdir -p /data/apache-hive-3.1.3-bin/lib")
    os.system("cp %s/mysql-connector-*  /data/apache-hive-3.1.3-bin/lib" % current_dir.rstrip("/"))
    os.system("cp %s/guava-* /data/apache-hive-3.1.3-bin/lib" % current_dir.rstrip("/"))
    os.system("cp -a %s/conf /data/apache-hive-3.1.3-bin" % current_dir.rstrip("/"))

    with open("/data/apache-hive-3.1.3-bin/conf/hive-site.xml-tem", "r") as f:
        with open("/data/apache-hive-3.1.3-bin/conf/hive-site.xml", "w") as f1:
            _content = f.read().replace("{mysql_host}", mysql_host).\
                replace('{mysql_port}', mysql_port).replace('{mysql_user}',mysql_user)\
            .replace('{mysql_password}', mysql_password)
            #_content =
            f1.write(_content)

    print("安装完成。请按照如下步骤操作：")
    print("1. 初始化数据库")
    print("cd /data/apache-hive-3.1.3-bin && ./bin/schematool -dbType mysql -initSchema")
    print("2. 启动hive server2服务")
    print("cd /data/apache-hive-3.1.3-bin && nohup  ./bin/hive --service hiveserver2 &")
    print("3. 把/data/apache-hive-3.1.3-bin加入到PATH")

