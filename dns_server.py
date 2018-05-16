import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import dnslib


SERVER_PUBLIC_IP = '_your_public_ip_'

lock = threading.Lock()
domain_dns_dict = {}


class DnsThread(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        fd.bind(('', 53))

        while True:
            packet, isp_dns_address = fd.recvfrom(2048)
            q = dnslib.DNSRecord.parse(packet)

            a = q.reply()
            q_name = q.questions[0].qname
            a.add_answer(dnslib.RR(q_name, dnslib.QTYPE.A, rdata=dnslib.A(SERVER_PUBLIC_IP), ttl=10))

            lock.acquire()
            domain_dns_dict[str(q_name)] = isp_dns_address
            lock.release()

            fd.sendto(a.pack(), isp_dns_address)
            print('dns request : ', q_name, isp_dns_address)


class ServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        host = self.headers.get('Host').split(':')[0] + '.'
        lock.acquire()
        message = domain_dns_dict.get(host, ('None', 'None'))[0]
        print('message = ', message, 'host = ', host)
        print(domain_dns_dict)
        lock.release()

        self.wfile.write(bytes(message, "utf8"))


if __name__ == '__main__':
    thread1 = DnsThread()
    thread1.start()

    server_address = ('0.0.0.0', 80)
    httpd = HTTPServer(server_address, ServerHandler)
    httpd.serve_forever()

    thread1.join()
