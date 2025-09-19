#!/usr/bin/env python3
"""
ZeroKey VPN-클라이언트
git clone https://github.com/yourid/zerokey-client.git
cd zerokey-client
python run.py
"""
import argparse, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "zerokey"))

from zerokey.daemon import start_daemon
from zerokey.cli import interactive_cli

def main():
    parser = argparse.ArgumentParser(description="ZeroKey – 서버가 키를 모르는 VPN")
    parser.add_argument("--daemon", "-d", action="store_true", help="백그라운드 데몬 모드")
    parser.add_argument("--server", "-s", default="zerokey.example.com:443", help="릴레이 서버 주소")
    parser.add_argument("--pwd", "-p", help="ZKP 비밀번호 (미입력 시 프롬프트)")
    args = parser.parse_args()

    if args.daemon:
        start_daemon(args.server, args.pwd)
    else:
        interactive_cli(args.server, args.pwd)

if __name__ == "__main__":
    main()
