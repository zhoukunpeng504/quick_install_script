## hadoop单机版快速安装


各目录说明：

3.2.4    
- 在A机器安装服务
```bash
# hdfs及yarn
# 建议提前关闭防火墙，并保证wget命令可用
# 适用于主流linux发型版，程序会自动下载jdk及hadoop安装包
# 以root用户执行如下命令即可，注意安装过程会自动修改主机名
python3  install_service.py
```
安装完成后，即可查看服务的运行状态：
```bash
yarn web控制台：http://hadoop324:8088/cluster
hdfs web控制台：http://hadoop324:9870/dfshealth.html#tab-overview
9870也是webhdfs的访问端口
```

- 在B机器安装客户端
```bash
# 建议提前关闭防火墙，并保证wget命令可用
# 适用于主流linux发型版，程序会自动下载jdk及hadoop安装包
# 以root用户执行如下命令即可。
python3  install_client.py
```


参考资料：

- 安装过程 https://last2win.com/ubuntu-20.04-install-hadoop/

- 如果需要优化yarn的参数。可以参考：
```bash
# 摘自： https://blog.csdn.net/qq_25302531/article/details/80623791
在YARN的NodeManager节点上，会将机器的CPU和内存的一定值抽离出来，抽离成虚拟的值，然后这些虚拟的值在根据配置组成多个Container，当application提出申请时，就会分配相应的Container资源。关于默认值我们可以查看官网，如下表所示。

#参数                                 	默认值
yarn.nodemanager.resource.memory-mb     -1
yarn.nodemanager.resource.cpu-vcores    -1
yarn.scheduler.minimum-allocation-mb    1024
yarn.scheduler.maximum-allocation-mb    8192
yarn.scheduler.minimum-allocation-vcores 1
yarn.scheduler.maximum-allocation-vcores 4
#内存配置
yarn.nodemanager.resource.memory-mb默认值为-1，代表着YARN的NodeManager占总内存的80%。也就是说加入我们的机器为64GB内存，出去非YARN进程需要的20%内存，我们大概需要64*0.8≈51GB，在分配的时候，单个任务可以申请的默认最小内存为1G，任务量大的话可最大提高到8GB。
在生产场景中，简单的配置，一般情况下：yarn.nodemanager.resource.memory-mb直接设置成我们需要的值，且要是最大和最小内存需求的整数倍；（一般Container容器中最小内存为4G，最大内存为16G）
假如：64GB的机器内存，我们有51GB的内存可用于NodeManager分配，根据上面的介绍，我们可以直接将yarn.nodemanager.resource.memory-mb值为48GB，然后容器最小内存为4GB，最大内存为16GB，也就是在当前的NodeManager节点下，我们最多可以有12个容器，最少可以有3个容器。
#CPU配置
此处的CPU指的是虚拟的CPU（CPU virtual core），之所以产生虚拟CPU（CPU vCore）这一概念，是因为物理CPU的处理能力的差异，为平衡这种差异，就引入这一概念。
yarn.nodemanager.resource.cpu-vcores  表示能够分配给Container的CPU核数，默认配置为-1，
代表值为8个虚拟CPU，推荐该值的设置和物理CPU的核数数量相同，若不够，则需要调小该值。
yarn.scheduler.minimum-allocation-vcores  默认值为1，
表示每个Container容器在处理任务的时候可申请的最少CPU个数为1个。
yarn.scheduler.maximum-allocation-vcores   默认值为4，
表示每个Container容器在处理任务的时候可申请的最大CPU个数为4个。
```
yarn配置修改后， 执行stop-yarn.sh 再 start-yarn.sh 即可， 无需重启hdfs。