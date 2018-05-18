

mkdir -p output

daemonize -e $(realpath ./output/stderr) -o $(realpath ./output/stdout) -p self.pid -l self.lock /usr/bin/python3 $(realpath ./dns_server.py)
