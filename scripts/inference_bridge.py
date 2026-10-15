#!/usr/bin/env python3
"""Narrow OpenAI inference bridge: host Unix socket -> loopback router.

The network-disabled container exposes a TCP adapter only inside its own network
namespace. No redirects, arbitrary destinations, model-management routes, client
credentials, or host files are forwarded. This is not a hostile-code VM boundary.
"""
import argparse
import http.client
import json
import os
from pathlib import Path
import socket
import socketserver
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit

MAX_BODY = 8 * 1024 * 1024
MAX_RESPONSE = 32 * 1024 * 1024
ALLOWED = {('GET', '/v1/models'), ('POST', '/v1/chat/completions')}


class UnixConnection(http.client.HTTPConnection):
    def __init__(self, path):
        super().__init__('localhost', timeout=600)
        self.path = str(path)

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.path)


class LimitedThreads(socketserver.ThreadingMixIn):
    daemon_threads = True

    def __init__(self, *args, **kwargs):
        self.worker_slots = threading.BoundedSemaphore(8)
        super().__init__(*args, **kwargs)

    def process_request(self, request, address):
        if not self.worker_slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        request.settimeout(30)  # includes header parsing, not just request bodies
        try:
            super().process_request(request, address)
        except Exception:
            self.worker_slots.release()
            raise

    def process_request_thread(self, request, address):
        try:
            super().process_request_thread(request, address)
        finally:
            self.worker_slots.release()


class UnixServer(LimitedThreads, socketserver.UnixStreamServer):
    pass


class ContainerServer(LimitedThreads, HTTPServer):
    pass


class Handler(BaseHTTPRequestHandler):
    # HTTP/1.0 closes the downstream stream, including buffered SSE responses.
    def log_message(self, *args):
        pass  # do not log prompts, credentials, or model output

    def handle(self):
        try:
            super().handle()
        except (ConnectionError, TimeoutError):
            pass  # rejected/disconnected clients must not dump host tracebacks

    def do_GET(self):
        self.forward()

    def do_POST(self):
        self.forward()

    def forward(self):
        if (self.command, self.path) not in ALLOWED:
            self.send_error(403, 'Only models and chat completions are allowed')
            return
        self.connection.settimeout(30)
        # Reject ambiguous framing before forwarding anything upstream.
        lengths = self.headers.get_all('Content-Length', [])
        if self.headers.get('Transfer-Encoding') or len(lengths) > 1:
            self.send_error(400, 'Unsupported request framing')
            return
        try:
            size = int(lengths[0]) if lengths else 0
        except ValueError:
            self.send_error(400, 'Invalid content length')
            return
        if not 0 <= size <= MAX_BODY or (self.command == 'GET' and size):
            self.send_error(413, 'Invalid request size')
            return
        if not self.server.slots.acquire(blocking=False):
            self.send_error(429, 'Inference bridge is busy')
            return
        connection = None
        started = False
        try:
            body = self.rfile.read(size)
            if len(body) != size:
                self.send_error(400, 'Incomplete body')
                return
            if self.command == 'POST':
                value = json.loads(body)
                if not isinstance(value, dict) or not isinstance(value.get('messages'), list):
                    self.send_error(400, 'A chat messages array is required')
                    return
                if not isinstance(value.get('model'), str):
                    self.send_error(400, 'A model name is required')
                    return
                budget = value.get('max_tokens', 16384)
                if type(budget) is not int or not 1 <= budget <= 16384:
                    self.send_error(400, 'max_tokens must be between 1 and 16384')
                    return
                value['max_tokens'] = budget
                # Disable server-side response caching, even if requested by a client.
                value['cache_prompt'] = False
                body = json.dumps(value).encode()
            connection = self.server.connection_factory()
            # Client Authorization/Cookie/Host/forwarding headers never leave the sandbox.
            connection.request(self.command, self.path, body=body or None,
                               headers={'Content-Type': 'application/json'})
            response = connection.getresponse()
            self.send_response(response.status)
            self.send_header('Content-Type', response.getheader('Content-Type', 'application/json'))
            self.send_header('Connection', 'close')
            self.end_headers()
            started = True
            total = 0
            while chunk := response.read1(65536):
                total += len(chunk)
                if total > MAX_RESPONSE:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
        except (OSError, ValueError, http.client.HTTPException):
            if not started:
                self.send_error(502, 'Inference bridge request failed')
        finally:
            self.close_connection = True
            if connection:
                connection.close()
            self.server.slots.release()


def host_server(path, upstream):
    url = urlsplit(upstream)
    if (url.scheme != 'http' or url.hostname not in ('127.0.0.1', '::1') or
            url.username or url.password or url.path not in ('', '/') or
            url.query or url.fragment or not url.port):
        raise ValueError('upstream must be an explicit HTTP loopback address and port')
    # A Unix socket must live on a native filesystem, not the NTFS workspace.
    server = UnixServer(str(path), Handler)
    os.chmod(path, 0o600)
    server.connection_factory = lambda: http.client.HTTPConnection(url.hostname, url.port, timeout=600)
    server.slots = threading.BoundedSemaphore(2)
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('host', 'container'))
    parser.add_argument('--socket', required=True, type=Path)
    parser.add_argument('--upstream', default='http://127.0.0.1:8081')
    args = parser.parse_args()
    if args.mode == 'host':
        server = host_server(args.socket, args.upstream)
    else:
        server = ContainerServer(('127.0.0.1', 8081), Handler)
        server.daemon_threads = True
        server.connection_factory = lambda: UnixConnection(args.socket)
        server.slots = threading.BoundedSemaphore(2)
    with server:
        server.serve_forever()


if __name__ == '__main__':
    main()
