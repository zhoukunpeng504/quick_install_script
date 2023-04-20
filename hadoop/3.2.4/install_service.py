# coding:utf-8
__author__ = "zkp"
# create by zkp on 2023/4/19
# hadoop 3.2.4 快捷安装脚本。
# 默认安装到/data/hadoop3.2.4目录
import os
import sys

profile_append = \
'''
# ##$hadoop install$##
export JAVA_HOME=/data/jdk8u362-b09
export HADOOP_HOME=/data/hadoop-3.2.4
export HADOOP_INSTALL=$HADOOP_HOME
export HADOOP_MAPRED_HOME=$HADOOP_HOME
export HADOOP_COMMON_HOME=$HADOOP_HOME
export HADOOP_HDFS_HOME=$HADOOP_HOME
export YARN_HOME=$HADOOP_HOME
export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
export PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin
# ## end ##
'''
# main_ip

hostname = 'hadoop324'


hadoop_env_sh_content = '''export JAVA_HOME=/data/jdk8u362-b09
export HADOOP_OS_TYPE=${HADOOP_OS_TYPE:-$(uname -s)}
'''

# hdfs://{hostname}:9003 可以根据自己需要修改
core_site_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<!--
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License. See accompanying LICENSE file.
-->

<!-- Put site-specific property overrides in this file. -->

<configuration>
<property>
  <name>fs.default.name</name>
    <value>hdfs://{hostname}:9003</value>
</property>
</configuration>'''

hdfs_site_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<!--
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License. See accompanying LICENSE file.
-->

<!-- Put site-specific property overrides in this file. -->
<configuration>
<property>
 <name>dfs.replication</name>
 <value>1</value>
</property>

<property>
  <name>dfs.name.dir</name>
    <value>file:///data/hadoop-3.2.4/namenode</value>
</property>

<property>
  <name>dfs.data.dir</name>
    <value>file:///data/hadoop-3.2.4/datanode</value>
</property>

<property> 
    <name>dfs.webhdfs.enabled</name> 
    <value>true</value> 
</property> 

</configuration>'''

yarn_site_content = f'''<?xml version="1.0"?>
<!--
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License. See accompanying LICENSE file.
-->
<configuration>

 <property>
  <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
 </property>
</configuration>'''

mapred_site_content = f'''<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<!--
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License. See accompanying LICENSE file.
-->

<!-- Put site-specific property overrides in this file. -->

<configuration>
 <property>
  <name>mapreduce.framework.name</name>
   <value>yarn</value>
 </property>
</configuration>'''

sbin_dfs_prefix = '''HDFS_DATANODE_USER=root
HADOOP_SECURE_DN_USER=hdfs
HDFS_NAMENODE_USER=root
HDFS_SECONDARYNAMENODE_USER=root'''


sbin_yarn_prefix = '''YARN_RESOURCEMANAGER_USER=root
HADOOP_SECURE_DN_USER=yarn
YARN_NODEMANAGER_USER=root'''


if __name__ == '__main__':
    # 1 下载安装包并解压
    os.system("mkdir -p /data")
    os.system("rm -rf /data/OpenJDK8U-jdk_x64_linux_hotspot_8u362b09.tar.gz")
    os.system("rm -rf /data/hadoop-3.2.4.tar.gz")
    os.system("cd /data && wget https://mirrors.tuna.tsinghua.edu.cn/Adoptium/8/jdk/x64/linux/"
              "OpenJDK8U-jdk_x64_linux_hotspot_8u362b09.tar.gz --no-check-certificate")
    print("jdk8下载完成")
    os.system("cd /data && wget https://mirrors.tuna.tsinghua.edu.cn/"
              "apache/hadoop/common/hadoop-3.2.4/hadoop-3.2.4.tar.gz --no-check-certificate")
    print("hadoop3.2.4 下载完成")
    # 解压安装包
    os.system("cd /data && tar -zxvf OpenJDK8U-jdk_x64_linux_hotspot_8u362b09.tar.gz")
    os.system("cd /data && tar -zxvf hadoop-3.2.4.tar.gz")
    # os.system("mkdir -p ")
    print("openjdk hadoop解压完成")


    # 2. 环境变量  主机名  ssh免密处理
    with open("/etc/profile", "r") as f:
        profile_ = f.read()
    if '##$hadoop install$##' not in profile_:
        with open("/etc/profile", "w") as f:
            f.write(profile_+'\n'+ profile_append)
    os.system("source /etc/profile")
    # 修改主机名
    os.system("hostname hadoop324")
    os.system("echo 'hadoop324'>/etc/hostname")
    # ssh免密
    os.system("rm -rf ~/.ssh/id_rsa*")
    os.system("ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa")
    os.system("cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys")
    os.system("chmod 0600 ~/.ssh/authorized_keys")


    # 3. 修改hadoop相关配置文件
    with open("/data/hadoop-3.2.4/etc/hadoop/hadoop-env.sh", "w") as f:
        f.write(hadoop_env_sh_content)
    with open("/data/hadoop-3.2.4/etc/hadoop/core-site.xml", "w") as f:
        f.write(core_site_content)
    with open("/data/hadoop-3.2.4/etc/hadoop/hdfs-site.xml", "w") as f:
        f.write(hdfs_site_content)
    with open("/data/hadoop-3.2.4/etc/hadoop/yarn-site.xml", "w") as f:
        f.write(yarn_site_content)
    with open("/data/hadoop-3.2.4/etc/hadoop/mapred-site.xml", "w") as f:
        f.write(mapred_site_content)


    # 4. 修复root用户无法执行start-dfs.sh和 stop-dfs.sh  start-yarn.sh  stop-yarn.sh
    # start-dfs.sh修复，允许root用户
    with open("/data/hadoop-3.2.4/sbin/start-dfs.sh", "r") as f:
        start_dfs_content= f.read()
    if sbin_dfs_prefix not in start_dfs_content:
        start_dfs_content = start_dfs_content.replace('#!/usr/bin/env bash\n',
                                                      '#!/usr/bin/env bash\n' + sbin_dfs_prefix+'\n')
    with open("/data/hadoop-3.2.4/sbin/start-dfs.sh", "w") as f:
        f.write(start_dfs_content)
    # stop-dfs.sh修复，允许root用户
    with open("/data/hadoop-3.2.4/sbin/stop-dfs.sh", "r") as f:
        stop_dfs_content = f.read()
    if sbin_dfs_prefix not in stop_dfs_content:
        stop_dfs_content = stop_dfs_content.replace('#!/usr/bin/env bash\n',
                                                      '#!/usr/bin/env bash\n' + sbin_dfs_prefix + '\n')
    with open("/data/hadoop-3.2.4/sbin/stop-dfs.sh", "w") as f:
        f.write(stop_dfs_content)
    # start-yarn.sh修复，允许root用户
    with open("/data/hadoop-3.2.4/sbin/start-yarn.sh", "r") as f:
        start_yarn_content= f.read()
    if sbin_yarn_prefix not in start_yarn_content:
        start_yarn_content = start_yarn_content.replace('#!/usr/bin/env bash\n',
                                                      '#!/usr/bin/env bash\n' + sbin_dfs_prefix+'\n')
    with open("/data/hadoop-3.2.4/sbin/start-yarn.sh", "w") as f:
        f.write(start_yarn_content)
    # stop-yarn.sh修复，允许root用户
    with open("/data/hadoop-3.2.4/sbin/stop-yarn.sh", "r") as f:
        stop_yarn_content = f.read()
    if sbin_yarn_prefix not in stop_yarn_content:
        stop_yarn_content = stop_yarn_content.replace('#!/usr/bin/env bash\n',
                                                      '#!/usr/bin/env bash\n' + sbin_dfs_prefix + '\n')
    with open("/data/hadoop-3.2.4/sbin/stop-yarn.sh", "w") as f:
        f.write(stop_yarn_content)
    print("start-dfs.sh  stop-dfs.sh start-yarn.sh stop-yarn.sh修复完成，已允许root用户执行")


    # 5. 完成
    with open("/etc/rc.local", "r") as f:
        _ = f.read()
    if './start-dfs.sh' not in _:
        os.system("echo 'cd /data/hadoop-3.2.4/sbin && ./start-dfs.sh'>> /etc/rc.local")
    if './start-yarn.sh' not in _:
        os.system("echo 'cd /data/hadoop-3.2.4/sbin && ./start-yarn.sh'>> /etc/rc.local")
    print("请执行如下指令启动hdfs及yarn:\n"
          "export JAVA_HOME=/data/jdk8u362-b09\n"
          "cd /data/hadoop-3.2.4/sbin && ./start-dfs.sh\n"
          "cd /data/hadoop-3.2.4/sbin && ./start-yarn.sh")


