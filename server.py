#!/usr/bin/env python
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import json
import argparse
import re
import os
import datetime
import socket
import struct

LOCALHOST = '127.0.0.1'
PARAM_SPECIFIER = ':'

class HostHandler():
    """
    Class that handles the addition of a host definition to the hosts file.
    This is useful to enable using a different URL than localhost to the mock
    server. Be aware though that, by default, any new host will be mapped to
    localhost, so the way to have multiple mock server instances serving different
    content is by specifying a different port.
    """
    def __init__(self, path_to_hosts=r"C:\Windows\System32\drivers\etc\hosts", address=LOCALHOST, hostname=None):
        self.default_path = path_to_hosts
        self.hostname = hostname
        self.address = address
        self.content = '{}\t{}'.format(self.address, self.hostname)

    def add_host(self, path=None):
        """
        Write the contents of this host definition to the provided path
        """
        if path is None:
            path = self.default_path
        with open(path, 'a') as hosts_file:
            hosts_file.write('\n' + self.content + '\n')

    def remove_host(self, path=None):
        """
        Remove this host from hosts file
        """
        if path is None:
            path = self.default_path
        content_with_removed_host = []
        remove_next = False
        with open(path, 'r') as hosts_file:
            for line in hosts_file.read().split('\n'):
                if line != self.content and not remove_next:
                    content_with_removed_host += [line]
                else:
                    content_with_removed_host[:-1] # previous line was a blank line
                    remove_next = not remove_next # next line is a blank line
        with open(path, 'w') as hosts_file:
            hosts_file.write('\n'.join(content_with_removed_host))


class SimpleServerHandler(BaseHTTPRequestHandler):
    """
    Class that handles HTTP Requests and Responses. 

    From the documentation of BaseHTTPRequestHandler:

    This server parses the request and the headers, and then calls a
    function specific to the request type (<command>).  Specifically,
    a request SPAM will be handled by a method do_SPAM().  If no
    such method exists the server sends an error response to the
    client.  If it exists, it is called with no arguments.
    """
    db = None # file from which to extract data and routing
    
    # Methods for internal use
    def _set_headers(self, status_code=200):
        """
        Set response headers. 
        """
        self.send_response(status_code)
        self.send_header('Content-type', 'text/json')
        self.end_headers()

    def _build_router(self):
        """
        Get the list of supported routes and its current data
        """
        # build route handler from datafile
        self.routes = []
        self.data = {}
        with open(self.db, "r") as f:
            self.data = json.load(f)
            self.routes = list(self.data.keys())

    def _get_route_and_params(self, route):
        """
        """
        path = None
        param = None
        try:
            path, param = route.split(PARAM_SPECIFIER)
        except:
            path = route
        return path.rstrip('/'), param

    def _get_data_key(self, path, param):
        """
        """
        if param is not None:
            return path + '/' + PARAM_SPECIFIER + param
        return path
        
    def _generate_next_id(self, current_data):
        """
        """
        return max([e['id'] for e in current_data]) + 1

    def _API_response(self, code):
        """
        Perpare the api response
        """
        resp = [status_code for status_code in HTTPStatus if status_code.value == code]
        if len(resp) == 1:
            resp = resp[0]
            return {
                'result': {
                    'code': resp.value,
                    'message': resp.phrase,
                    'description': resp.description
                }
            }

    # Handle HTTP requests         
    def do_GET(self):
        """
        Handle GET requests
        """
        self._build_router()
        for endpoint in self.routes:
            endpoint_path, param = self._get_route_and_params(endpoint)
            # if the endpoint being tested is not part of the request url
            # there's no need for further processing
            if endpoint_path not in self.path:
                continue
            # if there is no parameter return all the data
            if self.path.endswith("/" + endpoint_path): 
                    self._set_headers()
                    self.wfile.write(bytes(json.dumps(self.data[self._get_data_key(endpoint_path, param)]), "utf-8"))
                    return
            # else a parameter value has been included in the request
            _, param_val = self.path.rsplit('/', 1)
            # try to get value
            data_to_send = [i for i in self.data[self._get_data_key(endpoint_path, param)] if str(i[param]) == str(param_val)]
            if len(data_to_send) == 0:
                continue
            if len(data_to_send) == 1:
                data_to_send = data_to_send[0]
            self._set_headers()
            self.wfile.write(bytes(json.dumps(data_to_send), "utf-8"))
            return
        # Nothing matched the request
        self._set_headers(404)
        self.wfile.write(bytes(json.dumps(self._API_response(404)), "utf-8"))
        
    def do_POST(self):
        """
        Handle POST requests
        """
        self._build_router()
        valid_path = False
        for endpoint in self.routes:
            endpoint_path, _ = self._get_route_and_params(endpoint)
            if self.path.endswith("/" + endpoint_path):
                    valid_path = True
                    status_code = 200
                    # read post data
                    post_data = json.loads(self.rfile.read(int(self.headers.get('Content-Length'))).decode("UTF-8"))
                    try:
                        current_data = self.data[self._get_data_key(endpoint, None)]
                        if type(current_data) == list and type(post_data) == dict:
                            # Add object to list
                            post_data['id'] = self._generate_next_id(current_data)
                            self.data[endpoint] = current_data + [post_data]
                            with open(self.db, "w") as f:
                                f.write(json.dumps(self.data))
                        else:
                            status_code = 400
                    except:
                        status_code = 400
                    self._set_headers(status_code)
                    self.wfile.write(bytes(json.dumps(self._API_response(status_code)), "utf-8"))

        if not valid_path:
            self._set_headers(404)
            self.wfile.write(bytes(json.dumps(self._API_response(404)), "utf-8"))

class SimpleServer(HTTPServer):
    """
    Class used to set the data file from 
    which to extract the routing and data
    """
    def __init__(self, server_address, handler_class, dbfile):
        SimpleServerHandler.db = dbfile
        super(SimpleServer, self).__init__(server_address, handler_class)


def run(server_class=SimpleServer, handler_class=SimpleServerHandler, port=80, file="db.json", url=None):
    """
    Run the server forever listening at the specified port
    """
    log_url = url if url else 'localhost'
    log_port = ':{}/'.format(port) if port!=80 else '/' 
    log_msg = "\nRunning at http://{}{}".format(log_url, log_port)
    server_address = ('', int(port))
    httpd = server_class(server_address, handler_class, file)
    print('Starting Server...')
    print('Listening to connections on port: ' + str(port))
    print('Routing and data will be extracted from: ' + file)
    print(log_msg)
    httpd.serve_forever()

def parse_args():
    """
    Process command line arguments and return them as a dict
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', help='Specify the desired port')
    parser.add_argument('-f', '--file', help='File from which to extract routing and data')
    parser.add_argument('-u', '--url', help='Set a fake url for the server')
    return dict({k: v for k, v in vars(parser.parse_args()).items() if v is not None})

if __name__ == "__main__":
    args = parse_args()
    if args.get('url', ''):
        host = HostHandler(hostname=args.get('url'))
        host.add_host()
    try:
        if args:
            run(**args)
        else:
            run()
    except KeyboardInterrupt:
        # gracefully end program and removing entries from hosts files
        if args.get('url', ''):
            host.remove_host()

