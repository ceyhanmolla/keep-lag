#!/usr/bin/env python3
"""
Test server for KeepLag - simulates slow server
Listens forever responding slowly
"""
import socket
import threading
import time


class SlowHandler:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
    
    def handle(self):
        """Handle connection - wait forever"""
        try:
            while True:
                data = self.conn.recv(1024)
                if not data:
                    break
                # Never respond - keep connection open
                time.sleep(1)
        except:
            pass
        finally:
            try:
                self.conn.close()
            except:
                pass


def start_server(port=8888):
    """Start test server"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', port))
    server.listen(5)
    server.settimeout(1)
    
    print(f"Test server running on 127.0.0.1:{port}")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            try:
                conn, addr = server.accept()
                print(f"Connection from {addr}")
                handler = SlowHandler(conn, addr)
                thread = threading.Thread(target=handler.handle)
                thread.daemon = True
                thread.start()
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        print("\nStopping server")
    finally:
        server.close()


if __name__ == "__main__":
    start_server(8888)