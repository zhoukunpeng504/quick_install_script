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

sbin_dfs_prefix = '''HDFS_DATANODE_USER=root
HADOOP_SECURE_DN_USER=hdfs
HDFS_NAMENODE_USER=root
HDFS_SECONDARYNAMENODE_USER=root'''

start_dfs_content = \
'''
#!/usr/bin/env bash
HDFS_DATANODE_USER=root
HADOOP_SECURE_DN_USER=hdfs
HDFS_NAMENODE_USER=root
HDFS_SECONDARYNAMENODE_USER=root
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Start hadoop dfs daemons.
# Optinally upgrade or rollback dfs state.
# Run this on master node.

## startup matrix:
#
# if $EUID != 0, then exec
# if $EUID =0 then
#    if hdfs_subcmd_user is defined, su to that user, exec
#    if hdfs_subcmd_user is not defined, error
#
# For secure daemons, this means both the secure and insecure env vars need to be
# defined.  e.g., HDFS_DATANODE_USER=root HDFS_DATANODE_SECURE_USER=hdfs
#

## @description  usage info
## @audience     private
## @stability    evolving
## @replaceable  no
function hadoop_usage
{
  echo "Usage: start-dfs.sh [-upgrade|-rollback] [-clusterId]"
}

this="${BASH_SOURCE-$0}"
bin=$(cd -P -- "$(dirname -- "${this}")" >/dev/null && pwd -P)

# let's locate libexec...
if [[ -n "${HADOOP_HOME}" ]]; then
  HADOOP_DEFAULT_LIBEXEC_DIR="${HADOOP_HOME}/libexec"
else
  HADOOP_DEFAULT_LIBEXEC_DIR="${bin}/../libexec"
fi

HADOOP_LIBEXEC_DIR="${HADOOP_LIBEXEC_DIR:-$HADOOP_DEFAULT_LIBEXEC_DIR}"
# shellcheck disable=SC2034
HADOOP_NEW_CONFIG=true
if [[ -f "${HADOOP_LIBEXEC_DIR}/hdfs-config.sh" ]]; then
  . "${HADOOP_LIBEXEC_DIR}/hdfs-config.sh"
else
  echo "ERROR: Cannot execute ${HADOOP_LIBEXEC_DIR}/hdfs-config.sh." 2>&1
  exit 1
fi

# get arguments
if [[ $# -ge 1 ]]; then
  startOpt="$1"
  shift
  case "$startOpt" in
    -upgrade)
      nameStartOpt="$startOpt"
    ;;
    -rollback)
      dataStartOpt="$startOpt"
    ;;
    *)
      hadoop_exit_with_usage 1
    ;;
  esac
fi


#Add other possible options
nameStartOpt="$nameStartOpt $*"

#---------------------------------------------------------
# namenodes

NAMENODES=$("${HADOOP_HDFS_HOME}/bin/hdfs" getconf -namenodes 2>/dev/null)

if [[ -z "${NAMENODES}" ]]; then
  NAMENODES=$(hostname)
fi

echo "Starting namenodes on [${NAMENODES}]"
hadoop_uservar_su hdfs namenode "${HADOOP_HDFS_HOME}/bin/hdfs" \
    --workers \
    --config "${HADOOP_CONF_DIR}" \
    --hostnames "${NAMENODES}" \
    --daemon start \
    namenode ${nameStartOpt}

HADOOP_JUMBO_RETCOUNTER=$?

#---------------------------------------------------------
# datanodes (using default workers file)

echo "Starting datanodes"
hadoop_uservar_su hdfs datanode "${HADOOP_HDFS_HOME}/bin/hdfs" \
    --workers \
    --config "${HADOOP_CONF_DIR}" \
    --daemon start \
    datanode ${dataStartOpt}
(( HADOOP_JUMBO_RETCOUNTER=HADOOP_JUMBO_RETCOUNTER + $? ))

#---------------------------------------------------------
# secondary namenodes (if any)

SECONDARY_NAMENODES=$("${HADOOP_HDFS_HOME}/bin/hdfs" getconf -secondarynamenodes 2>/dev/null)

if [[ -n "${SECONDARY_NAMENODES}" ]]; then

  if [[ "${NAMENODES}" =~ , ]]; then

    hadoop_error "WARNING: Highly available NameNode is configured."
    hadoop_error "WARNING: Skipping SecondaryNameNode."

  else

    if [[ "${SECONDARY_NAMENODES}" == "0.0.0.0" ]]; then
      SECONDARY_NAMENODES=$(hostname)
    fi

    echo "Starting secondary namenodes [${SECONDARY_NAMENODES}]"

    hadoop_uservar_su hdfs secondarynamenode "${HADOOP_HDFS_HOME}/bin/hdfs" \
      --workers \
      --config "${HADOOP_CONF_DIR}" \
      --hostnames "${SECONDARY_NAMENODES}" \
      --daemon start \
      secondarynamenode
    (( HADOOP_JUMBO_RETCOUNTER=HADOOP_JUMBO_RETCOUNTER + $? ))
  fi
fi

#---------------------------------------------------------
# quorumjournal nodes (if any)

JOURNAL_NODES=$("${HADOOP_HDFS_HOME}/bin/hdfs" getconf -journalNodes 2>&-)

if [[ "${#JOURNAL_NODES}" != 0 ]]; then
  echo "Starting journal nodes [${JOURNAL_NODES}]"

  hadoop_uservar_su hdfs journalnode "${HADOOP_HDFS_HOME}/bin/hdfs" \
    --workers \
    --config "${HADOOP_CONF_DIR}" \
    --hostnames "${JOURNAL_NODES}" \
    --daemon start \
    journalnode
   (( HADOOP_JUMBO_RETCOUNTER=HADOOP_JUMBO_RETCOUNTER + $? ))
fi

#---------------------------------------------------------
# ZK Failover controllers, if auto-HA is enabled
AUTOHA_ENABLED=$("${HADOOP_HDFS_HOME}/bin/hdfs" getconf -confKey dfs.ha.automatic-failover.enabled | tr '[:upper:]' '[:lower:]')
if [[ "${AUTOHA_ENABLED}" = "true" ]]; then
  echo "Starting ZK Failover Controllers on NN hosts [${NAMENODES}]"

  hadoop_uservar_su hdfs zkfc "${HADOOP_HDFS_HOME}/bin/hdfs" \
    --workers \
    --config "${HADOOP_CONF_DIR}" \
    --hostnames "${NAMENODES}" \
    --daemon start \
    zkfc
  (( HADOOP_JUMBO_RETCOUNTER=HADOOP_JUMBO_RETCOUNTER + $? ))
fi

exit ${HADOOP_JUMBO_RETCOUNTER}

# eof
'''
stop_dfs_content = \
'''
#!/usr/bin/env bash
HDFS_DATANODE_USER=root
HADOOP_SECURE_DN_USER=hdfs
HDFS_NAMENODE_USER=root
HDFS_SECONDARYNAMENODE_USER=root

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Stop hadoop dfs daemons.
# Run this on master node.

## @description  usage info
## @audience     private
## @stability    evolving
## @replaceable  no
function hadoop_usage
{
  echo "Usage: stop-dfs.sh"
}

this="${BASH_SOURCE-$0}"
bin=$(cd -P -- "$(dirname -- "${this}")" >/dev/null && pwd -P)

# let's locate libexec...
if [[ -n "${HADOOP_HOME}" ]]; then
  HADOOP_DEFAULT_LIBEXEC_DIR="${HADOOP_HOME}/libexec"
else
  HADOOP_DEFAULT_LIBEXEC_DIR="${bin}/../libexec"
fi

HADOOP_LIBEXEC_DIR="${HADOOP_LIBEXEC_DIR:-$HADOOP_DEFAULT_LIBEXEC_DIR}"
# shellcheck disable=SC2034
HADOOP_NEW_CONFIG=true
if [[ -f "${HADOOP_LIBEXEC_DIR}/hdfs-config.sh" ]]; then
  . "${HADOOP_LIBEXEC_DIR}/hdfs-config.sh"
else
  echo "ERROR: Cannot execute ${HADOOP_LIBEXEC_DIR}/hdfs-config.sh." 2>&1
  exit 1
fi

#---------------------------------------------------------
# namenodes

NAMENODES=$("${HADOOP_HDFS_HOME}/bin/hdfs" getconf -namenodes 2>/dev/null)

if [[ -z "${NAMENODES}" ]]; then
  NAMENODES=$(hostname)
fi

echo "Stopping namenodes on [${NAMENODES}]"

  hadoop_uservar_su hdfs namenode "${HADOOP_HDFS_HOME}/bin/hdfs" \
    --workers \
    --config "${HADOOP_CONF_DIR}" \
    --hostnames "${NAMENODES}" \
    --daemon stop \
    namenode

#---------------------------------------------------------
# datanodes (using default workers file)

echo "Stopping datanodes"

hadoop_uservar_su hdfs datanode "${HADOOP_HDFS_HOME}/bin/hdfs" \
  --workers \
  --config "${HADOOP_CONF_DIR}" \
  --daemon stop \
  datanode

#---------------------------------------------------------
# secondary namenodes (if any)

SECONDARY_NAMENODES=$("${HADOOP_HDFS_HOME}/bin/hdfs" getconf -secondarynamenodes 2>/dev/null)

if [[ "${SECONDARY_NAMENODES}" == "0.0.0.0" ]]; then
  SECONDARY_NAMENODES=$(hostname)
fi

if [[ -n "${SECONDARY_NAMENODES}" ]]; then
  echo "Stopping secondary namenodes [${SECONDARY_NAMENODES}]"

  hadoop_uservar_su hdfs secondarynamenode "${HADOOP_HDFS_HOME}/bin/hdfs" \
    --workers \
    --config "${HADOOP_CONF_DIR}" \
    --hostnames "${SECONDARY_NAMENODES}" \
    --daemon stop \
    secondarynamenode
fi

#---------------------------------------------------------
# quorumjournal nodes (if any)

JOURNAL_NODES=$("${HADOOP_HDFS_HOME}/bin/hdfs" getconf -journalNodes 2>&-)

if [[ "${#JOURNAL_NODES}" != 0 ]]; then
  echo "Stopping journal nodes [${JOURNAL_NODES}]"

  hadoop_uservar_su hdfs journalnode "${HADOOP_HDFS_HOME}/bin/hdfs" \
    --workers \
    --config "${HADOOP_CONF_DIR}" \
    --hostnames "${JOURNAL_NODES}" \
    --daemon stop \
    journalnode
fi

#---------------------------------------------------------
# ZK Failover controllers, if auto-HA is enabled
AUTOHA_ENABLED=$("${HADOOP_HDFS_HOME}/bin/hdfs" getconf -confKey dfs.ha.automatic-failover.enabled | tr '[:upper:]' '[:lower:]')
if [[ "${AUTOHA_ENABLED}" = "true" ]]; then
  echo "Stopping ZK Failover Controllers on NN hosts [${NAMENODES}]"

  hadoop_uservar_su hdfs zkfc "${HADOOP_HDFS_HOME}/bin/hdfs" \
    --workers \
    --config "${HADOOP_CONF_DIR}" \
    --hostnames "${NAMENODES}" \
    --daemon stop \
    zkfc
fi

# eof

'''




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
    os.system("mkdir -p ")
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


    # 4. 修复root用户无法执行start-dfs.sh和 stop-dfs.sh问题
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
    print("start-dfs.sh  stop-dfs.sh修复完成，已允许root用户执行")


    # 5. 完成
    with open("/etc/rc.local", "r") as f:
        _ = f.read()
    if './start-dfs.sh' not in _:
        os.system("echo 'cd /data/hadoop-3.2.4/sbin && ./start-dfs.sh'>> /etc/rc.local")
    print("请执行如下指令启动hdfs:\n"
          "export JAVA_HOME=/data/jdk8u362-b09\n"
          "cd /data/hadoop-3.2.4/sbin && ./start-dfs.sh")


