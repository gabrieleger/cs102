import asyncore
import asynchat
import socket
import multiprocessing
import logging
import mimetypes
import os
import sys
from urllib.parse import unquote

# from urlparse import parse_qs
# import urllib

import argparse
from time import strftime, gmtime


def url_normalize(path):
    if path.startswith("."):
        path = "/" + path
    while "../" in path:
        p1 = path.find("/..")
        p2 = path.rfind("/", 0, p1)
        if p2 != -1:
            path = path[:p2] + path[p1 + 3:]
        else:
            path = path.replace("/..", "", 1)
    path = path.replace("/./", "/")
    path = unquote(path)
    if "?" in path:
        path = path[:path.find('?')]
    return path


def read_file(path):
    file = bytes()
    fp = FileProducer(open(path, 'rb'))
    while True:
        cur_chunk = fp.more()
        if not cur_chunk:
            break
        file += cur_chunk
    file = file.replace(b'\r\n', b'\n')
    return file


class FileProducer(object):
    def __init__(self, file, chunk_size=4096):
        self.file = file
        self.chunk_size = chunk_size

    def more(self):
        if self.file:
            data = self.file.read(self.chunk_size)
            if data:
                return data
            self.file.close()
            self.file = None
        return ""


class AsyncServer(asyncore.dispatcher):
    def __init__(self, host="127.0.0.1", port=9000, handler_class=None):
        super().__init__()
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        self.handler_class = handler_class
        self.host = host
        self.port = port

    def handle_accepted(self, sock, addr):
        logging.debug(f"Incoming connection from {addr}")
        if self.handler_class is not None:
            self.handler_class(sock, self.host, self.port)

    def serve_forever(self):
        try:
            asyncore.loop()
        except KeyboardInterrupt:
            logging.debug("Stopping server...")
        finally:
            self.close()


class AsyncHTTPRequestHandler(asynchat.async_chat):
    responses = {
        200: ('OK', 'Request fulfilled, document follows'),
        400: ('Bad Request',
              'Bad request syntax or unsupported method'),
        403: ('Forbidden',
              'Request forbidden -- authorization will not help'),
        404: ('Not Found', 'Nothing matches the given URI'),
        405: ('Method Not Allowed',
              'Specified method is invalid for this resource.'),
    }

    def __init__(self, sock, host, port):
        super().__init__(sock)
        self.default_terminator = '\r\n'
        self.set_terminator(self.default_terminator.encode('utf-8'))
        self.ibuffer = ''
        self.obuffer = ''
        self.reading_headers = True
        self.headers = {}
        self.path = ''
        self.response = ''
        self.method = ''
        self.limiter = ''
        self.server_name = host
        self.server_port = port

    def init_response(self, code, message=None):
        self.response = f"HTTP/1.1 {code} {message}"
        self.end_headers()

    def collect_incoming_data(self, data):
        logging.debug(f"Incoming data: {data}")
        self.ibuffer += data.decode('utf-8')

    def found_terminator(self):
        self.parse_request()

    def parse_request(self):
        self.reading_headers = False
        if 'method' not in self.headers:
            self.method, self.path, self.ibuffer = self.ibuffer.split(' ', 2)
        self.parse_headers()

        if self.headers['method'] == "POST":
            try:
                if not self.limiter:
                    self.ibuffer = ''
                    self.limiter = self.headers['content-type'][self.headers['content-type'].index('boundary=') + 9:]
                    content_length = self.headers['content-length']
                    if int(content_length) == 0:
                        self.send_error(400)
                    self.set_terminator(int(content_length))
                    self.reading_headers = True
                else:
                    self.obuffer = self.ibuffer[self.ibuffer.index(self.default_terminator) + 4:self.ibuffer.find('--' + self.limiter + '--') - 2]
                    self.handle_request()
            except KeyError or ValueError:
                self.send_error(400)
                return
        else:
            self.ibuffer = ''
            self.handle_request()

    def parse_headers(self):
        key_value_strings = self.ibuffer.split(self.default_terminator)
        for key_value in key_value_strings:
            if ':' not in key_value:
                continue
            else:
                key, value = key_value.split(':', 1)
                value.lstrip()
                self.headers[key.lower()] = value
        self.headers['method'] = self.method

    def handle_request(self):
        method_name = 'do_' + self.headers['method']
        if not hasattr(self, method_name):
            self.send_error(405)
            self.handle_close()
            return
        handler = getattr(self, method_name)
        handler()

    def add_header(self, keyword, value):
        self.response += f"{keyword}: {value}"
        self.end_headers()

    def send_error(self, code, message=None):
        try:
            short_msg, long_msg = AsyncHTTPRequestHandler.responses[code]
        except KeyError:
            short_msg, long_msg = '???', '???'
        if message is None:
            message = short_msg

        self.init_response(code, message)
        self.add_header("Content-Type", "text/plain")
        self.add_header("Connection", "close")
        self.end_headers()
        self.response += long_msg
        self.end_headers()
        self.send(self.response.encode('utf-8'))
        self.close()

    def send_response(self, code, message=None):
        pass

    def end_headers(self):
        self.response += self.default_terminator

    def date_time_string(self):
        return strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())

    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            path = os.path.join(path, "index.html")
            if not os.path.isfile(path):
                self.send_error(403)
                return None
            file_type, _ = mimetypes.guess_type(path)
            file = read_file(path)
        elif os.path.isfile(path):
            file_type, _ = mimetypes.guess_type(path)
            file = read_file(path)
        else:
            self.send_error(404)
            return None
        return file, file_type

    def translate_path(self, path):
        return os.getcwd() + url_normalize(path)

    def do_GET(self, include_content=True):
        file, file_type = self.send_head()
        self.init_response(200, "OK")
        self.add_header("Content-Type", file_type)
        self.add_header("Date", self.date_time_string())
        self.add_header("Server", '127.0.0.1')
        self.add_header("Content-Length", len(file))
        self.add_header("Connection", "close")
        self.end_headers()

        if include_content:
            try:
                # logging.debug(self.response.encode('utf-8') + file)
                self.send(self.response.encode('utf-8') + file)
            except OSError:
                pass
        else:
            self.send(self.response.encode('utf-8'))

        self.close()

    def do_HEAD(self):
        self.do_GET(include_content=False)


def parse_args():
    parser = argparse.ArgumentParser("Simple asynchronous web-server")
    parser.add_argument("--host", dest="host", default="127.0.0.1")
    parser.add_argument("--port", dest="port", type=int, default=9000)
    parser.add_argument("--log", dest="loglevel", default="debug")
    parser.add_argument("--logfile", dest="logfile", default='async_server.log')
    parser.add_argument("-w", dest="nworkers", type=int, default=1)
    parser.add_argument("-r", dest="document_root", default=".")
    return parser.parse_args()


def run(args):
    logging.debug(f'Starting async server on http://{args.host}:{args.port}/')
    server = AsyncServer(host=args.host, port=args.port, handler_class=AsyncHTTPRequestHandler)
    server.serve_forever()


if __name__ == '__main__':
    args = parse_args()

    logging.basicConfig(
        # filename=args.logfile,
        stream=sys.stdout,
        level=getattr(logging, args.loglevel.upper()),
        format="%(name)s: %(process)d %(message)s")
    log = logging.getLogger(__name__)

    DOCUMENT_ROOT = args.document_root
    run(args)
    # for _ in range(args.nworkers):
    #     p = multiprocessing.Process(target=run, args=(args,))
    #     p.start()
