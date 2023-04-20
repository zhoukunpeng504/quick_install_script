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
- 在B机器安装客户端
```bash
# 建议提前关闭防火墙，并保证wget命令可用
# 适用于主流linux发型版，程序会自动下载jdk及hadoop安装包
# 以root用户执行如下命令即可。
python3  install_client.py
```


参考资料：

https://last2win.com/ubuntu-20.04-install-hadoop/