import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import dnslib


SERVER_PUBLIC_IP = '35.189.162.161'

lock = threading.Lock()
domain_dns_dict = {}
_later_delete_list = []


def delete_later(d, key):
    _later_delete_list.append(key)

    if len(_later_delete_list) > 1000:
        del_key = _later_delete_list.pop(0)
        d.pop(del_key, None)


class DnsThread(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        fd.bind(('', 53))

        while True:
            packet, isp_dns_address = fd.recvfrom(2048)
            req = dnslib.DNSRecord.parse(packet)

            a = req.reply()
            q_name = req.get_q().qname
            q_type = req.get_q().qtype
            q_type_str = dnslib.QTYPE.get(q_type)

            if q_type_str == 'A':
                a.add_answer(dnslib.RR(q_name, dnslib.QTYPE.A, rdata=dnslib.A(SERVER_PUBLIC_IP), ttl=600))

                lock.acquire()
                k = str(q_name)
                domain_dns_dict[k] = isp_dns_address[0]
                delete_later(domain_dns_dict, k)
                lock.release()

            print('dns request : ', q_name, q_type_str, isp_dns_address)
            fd.sendto(a.pack(), isp_dns_address)


class ServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print('http request : ', self.client_address)

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        host = self.headers.get('Host').split(':')[0] + '.'
        lock.acquire()
        message = domain_dns_dict.pop(host, '')
        lock.release()

        self.wfile.write(bytes(message, "utf8"))


if __name__ == '__main__':
    thread1 = DnsThread()
    thread1.start()

    server_address = ('0.0.0.0', 8053)
    httpd = HTTPServer(server_address, ServerHandler)
    httpd.serve_forever()

    thread1.join()
