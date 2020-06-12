import async_server as server
import sys


class AsyncWSGIServer(server.AsyncServer):
    def set_app(self, application):
        self.application = application

    def get_app(self):
        return self.application
    
    def handle_accepted(self, sock, addr):
        print(f"Incoming connection from {addr}")
        server.AsyncWSGIRequestHandler(sock, self.application)
        

class AsyncWSGIRequestHandler(server.AsyncHTTPRequestHandler):
    def __init__(self, sock, application):
        server.AsyncHTTPRequestHandler.__init__(self, sock)
        self.application = application
        
        
    def get_environ(self):
        variables = {
            'wsgi.version':      (1, 0),
            'wsgi.url_scheme':   'http',
            'wsgi.input':        sys.stdin,
            'wsgi.errors':       sys.stderr,
            'wsgi.multithread':  False,
            'wsgi.multiprocess': False,
            'wsgi.run_once':     False,
            'REQUEST_METHOD':    self.method,
            'PATH_INFO':         self.path,
            'SERVER_NAME':       self.server_name,
            'SERVER_PORT':       str(self.server_port)
        }
        return variables
    
    def found_terminator(self):
        self.parse_headers()
        self.parse_request()
        self.handle_request()
    
    def start_response(self, status, response_headers, exc_info=None):
        code, message = status.split(" ")
        self.init_response(code, message)
        for key, value in response_headers:
            self.headers[key] = value

    def handle_request(self):
        env = self.get_environ()
        app = server.get_app()
        result = app(env, self.start_response)
        self.finish_response(result)

    def finish_response(self, result):
        self.add_header("Content-Type", 'text/html')
        self.add_header("Date", self.date_time_string())
        self.add_header("Server", '127.0.0.1')
        self.add_header("Content-Length", len(result[0]))
        self.add_header("Connection", "close")
        self.end_headers()
        self.response += result[0].decode('utf-8')
        self.send(self.response.encode('utf-8'))
        self.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    server = AsyncWSGIServer(handler_class=AsyncWSGIRequestHandler)
    server.set_app(application)
    server.serve_forever()
