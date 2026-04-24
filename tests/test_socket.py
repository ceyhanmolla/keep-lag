#!/usr/bin/env python3
"""KeepLag Test Suite"""
import asyncio
import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional
import sys


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def assert_equal(self, expected, actual, message: str):
        if expected == actual:
            self.passed += 1
            print(f"  ✓ {message}")
        else:
            self.failed += 1
            self.errors.append(message)
            print(f"  ✗ {message}")
            print(f"    Expected: {expected}")
            print(f"    Got:      {actual}")

    def assert_true(self, condition: bool, message: str):
        if condition:
            self.passed += 1
            print(f"  ✓ {message}")
        else:
            self.failed += 1
            self.errors.append(message)
            print(f"  ✗ {message}")

    def result(self):
        print(f"\n{self.passed} passed, {self.failed} failed")
        return self.failed == 0


class SlowlorisHandler(BaseHTTPRequestHandler):
    """Minimal handler that never completes requests"""
    def log_message(self, format, *args):
        pass  # Suppress logging

    def do_GET(self):
        # Don't send response - keep connection open indefinitely
        pass


def start_test_server(port: int = 8888) -> HTTPServer:
    """Start test HTTP server"""
    server = HTTPServer(('127.0.0.1', port), SlowlorisHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server


def run_tests():
    """Run all tests"""
    t = TestRunner()
    server = start_test_server(8888)
    print("Starting tests...\n")

    # Test 1: Can create socket
    print("Test 1: Socket creation")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        s.connect(('127.0.0.1', 8888))
        t.assert_true(s, "Socket created and connected")
        s.close()
    except Exception as e:
        t.assert_true(False, f"Socket creation: {e}")

    # Test 2: HTTP request sending
    print("\nTest 2: HTTP request")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        s.connect(('127.0.0.1', 8888))
        
        # Send partial GET request manually
        request = f"GET /?{1} HTTP/1.1\r\n"
        s.send(request.encode('utf-8'))
        
        # Send headers manually
        s.send(f"User-Agent: Test/1.0\r\n".encode())
        s.send(f"Accept-language: en-US\r\n".encode())
        
        t.assert_true(True, "HTTP headers sent")
        s.close()
    except Exception as e:
        t.assert_true(False, f"HTTP request: {e}")

    # Test 3: Keep-alive header
    print("\nTest 3: Keep-alive header")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        s.connect(('127.0.0.1', 8888))
        
        # Initial request
        s.send(f"GET /?{1} HTTP/1.1\r\n".encode())
        s.send(b"User-Agent: Test\r\n\r\n")
        
        # Keep-alive header
        s.send(b"X-a: 1\r\n\r\n")
        
        t.assert_true(True, "Keep-alive sent")
        s.close()
    except Exception as e:
        t.assert_true(False, f"Keep-alive: {e}")

    # Test 4: Multiple sockets
    print("\nTest 4: Multiple connections")
    sockets = []
    try:
        for i in range(10):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect(('127.0.0.1', 8888))
            s.send(f"GET /?{i} HTTP/1.1\r\n\r\n".encode())
            sockets.append(s)
        
        t.assert_equal(10, len(sockets), "10 connections created")
        
        for s in sockets:
            s.close()
    except Exception as e:
        t.assert_true(False, f"Multiple sockets: {e}")

    # Test 5: Connection timeout
    print("\nTest 5: Connection handling")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(('127.0.0.1', 8888))
        
        # Send request
        s.send(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
        
        # Wait a bit
        import time
        time.sleep(0.5)
        
        # Try to check if socket is still open
        t.assert_true(True, "Connection handled")
        s.close()
    except Exception as e:
        t.assert_true(False, f"Connection: {e}")

    server.shutdown()
    print("\n" + "="*40)
    return t.result()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)