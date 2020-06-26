#!/usr/bin/env python3
import sys
import os
import secrets

def main():
    rnd = secrets.token_hex(16)
    # 4 in third indicates random UUID
    # 8 in fourth indicates normal feed
    # 9 in fourth indicates noitalics feed
    print("urn:uuid:" + rnd[0:8] + "-" + rnd[8:12] + "-4" + rnd[13:16] + "-8" + rnd[17:20] + "-" + rnd[20:32])

if __name__ == "__main__":
    main()