#!/usr/bin/env bash
sudo iptables -t nat -F REDSOCKS 2>/dev/null
sudo iptables -t nat -X REDSOCKS 2>/dev/null
sudo pkill -F /var/run/redsocks.pid 2>/dev/null || true
echo "시스템 터널링 제거 완료"
