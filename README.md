# KeepLag - HTTP Stress Test Tool

A terminal-based HTTP stress testing tool inspired by Slowloris.

## What is KeepLag?

KeepLag is a low-bandwidth HTTP stress testing tool that tests server resilience against connection exhaustion. It works by:

1. Opening multiple TCP connections
2. Sending partial HTTP requests (headers only)
3. Keeping connections alive with periodic keep-alive headers
4. Never completing requests - server waits indefinitely

**Purpose:** Security research, stress testing, and load testing of web servers.

## Features

- Multiple socket connections
- Keep-alive header sending
- Configurable parameters (sockets, sleep time, port)
- Verbose logging
- Random user-agents
- HTTPS/SSL support
- Terminal-based interface

## Quick Start

```bash
# Clone and run
git clone https://github.com/cekhanmolla/keep-lag.git
cd keep-lag

# Basic usage
python3 src/keeplag.py target.com

# With options
python3 src/keeplag.py target.com -s 100 --sleeptime 10 -v
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `host` | Target host (required) | - |
| `-p, --port` | Target port | 80 |
| `-s, --sockets` | Number of sockets | 150 |
| `-v, --verbose` | Enable verbose logging | False |
| `-ua, --randuseragents` | Random user agents | False |
| `--https` | Use HTTPS | False |
| `--sleeptime` | Sleep between headers (sec) | 15 |

## How It Works

```
TCP Connection → HTTP GET (partial) → Keep-Alive headers every X sec
                                                    ↓
                                          Server connection pool exhausted
                                          ← Cannot serve others
```

## Usage Examples

```bash
# Test local server
python3 src/keeplag.py localhost -p 8888 -s 10

# Test with 100 sockets
python3 src/keeplag.py example.com -s 100 -v

# HTTPS test
python3 src/keeplag.py example.com --https -s 50

# Custom sleep time (faster)
python3 src/keeplag.py example.com --sleeptime 5 -s 200
```

## Requirements

- Python 3.8+
- No external dependencies (uses built-in socket, ssl)

## Testing

```bash
# Run test server first
python3 src/test_server.py &

# Run tests
python3 tests/test_socket.py
```

## Disclaimer

KeepLag is designed for authorized security testing only. Always get written permission before testing any system you don't own.

## License

MIT License

## Author

cekhanmolla