# dns-leak-test
通过web查询 当前dns
类似这个网站  `http://dnsleak.com/`

依赖
```
pip3 install --user dnslib
yum install daemonize
```

用法：
```
客户端
(bash)
curl $(uuidgen).dns-leak.writebug.win:8053

服务器
bash run_daemon.sh
```
