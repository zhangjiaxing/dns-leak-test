# dns-leak-test
通过web查询 当前dns
类似这个网站  `http://dnsleak.com/`

依赖:
```bash
pip3 install --user dnslib
yum install daemonize
```

配置:
首先,你的服务器需要一个公网IP.
然后配置你的DNS解析记录, 添加NS类型的记录, 和添加A类型的记录.

| Host | Type | Value |
| ---- | ---- | ----  |
| dns-leak |NS | ns1.dns-leak.writebug.win |
| ns1.dns-leak | A | 35.189.162.161(public IP) |

最后修改程序源码, 将SERVER_PUBLIC_IP修改为你的公网IP.


用法：
```bash
#客户端(bash)
curl $(uuidgen).dns-leak.writebug.win:8053


#服务器
bash run_daemon.sh
```
