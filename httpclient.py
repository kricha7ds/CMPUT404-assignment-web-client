#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    # https://docs.python.org/3.6/library/urllib.parse.html#url-parsing
    def get_host_port(self,url):
        host = url.hostname
        port = url.port
        scheme = url.scheme
        if scheme == "http" and port == None:
            return host, 80
        elif scheme == "https" and port == None:
            return host, 443
        else: # hostname and port are present in the request
            return host, port

    # https://docs.python.org/3/library/http.client.html#http.client.HTTPConnection.connect
    # apparently this can be called automatically 
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # print(data)
        return int(data.split()[1])

    def get_headers(self, data):
        return data.split('\r\n\r\n')[0]

    def get_request(self, parsed_url):
        path = '/' if not parsed_url.path else parsed_url.path # empty string if not present
        status = f'GET {path} HTTP/1.1\r\n'
        headers = f'Host: {parsed_url.hostname}\r\nAccept: */*\r\nAccept-Charset: UTF-8\r\nConnection: close\r\n'
        CRLF = f'\r\n'
        return status + headers + CRLF
    
    def get_post(self, parsed_url, query):
        path = '/' if not parsed_url.path else parsed_url.path # empty string if not present
        length = len(query.encode('utf-8')) 
        status = f'POST {path} HTTP/1.1\r\n'
        headers = f'Host: {parsed_url.hostname}\r\nAccept: */*\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {length}\r\nConnection: close\r\n'
        CRLF = f'\r\n'
        return status + headers + CRLF + f'{query}'

    def get_body(self, data):
        return data.split('\r\n\r\n')[1]

    # helper function to print results to stdout
    def print_response(self, code, headers, body):
        print(code)
        print(headers)
        print(body)
        return
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def parse_encoded_url(self, args):
        return urllib.parse.urlencode(args) if args != None else urllib.parse.urlencode('')
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part # what the heck is this
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500 # Internal server error :O
        body = ""
        # print("we're supposed to GET stuff here.")
        # parsed_url = urllib.parse.urlparse(url)

        # client_host = parsed_url.hostname
        client_host, client_port = self.get_host_port(urllib.parse.urlparse(url))
        self.connect(client_host, client_port)
        data = self.get_request(urllib.parse.urlparse(url))
        self.sendall(data) # send request to the server
        response = self.recvall(self.socket) # get the response
        
        # start constructing the response 
        code = self.get_code(response)
        headers = self.get_headers(response)
        body = self.get_body(response)
        self.print_response(code, headers, body) # send it!!

        self.close()
        return HTTPResponse(code, body) # User story: as dev, return HTTPResponse object

    def POST(self, url, args=None):
        code = 500 # Internal server error :O
        body = ""
        # print("POST stuff will go here.")
        # print(args)

        client_host, client_port = self.get_host_port(urllib.parse.urlparse(url))
        client_query = self.parse_encoded_url(args)
        self.connect(client_host, client_port)
        data = self.get_post(urllib.parse.urlparse(url), client_query)
        self.sendall(data)
        response = self.recvall(self.socket)
        
        # start constructing the response
        code = self.get_code(response)
        headers = self.get_headers(response)
        body = self.get_body(response)
        self.print_response(code, headers, body) # send it!!

        self.close()
        return HTTPResponse(code, body) # User story: as dev, return HTTPResponse object

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
