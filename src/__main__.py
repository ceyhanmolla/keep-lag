#!/usr/bin/env python3
"""
KeepLag CLI Entry Point
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from keeplag import main

if __name__ == "__main__":
    main()