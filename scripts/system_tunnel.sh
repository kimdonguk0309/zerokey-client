#!/usr/bin/env bash
set -e
# colors
RED='\033[0;31m'; GREEN='\033[0;32m'; NC='\033[0m'
echo -e "${GREEN}[ZeroKey]${NC} 리눅스 전체 시스템 트래픽을 127.0.0.1:1080 SOCKS5로 터널링합니다."

# root 체크
[[ $EUID -eq 0 ]] || { echo -e "${RED}sudo로 실행하세요${NC}"; exit 1; }

# 패키지
apt-get update -qq && apt-get install -y iptables redsocks

# redsocks config
cat >/tmp/redsocks.conf <<EOF
base { log_debug=off; log_info=on; daemon=off; redirector=iptables; }
redsocks { local_ip=127.0.0.1; local_port=12345; ip=127.0.0.1; port=1080; type=socks5; }
EOF

# 기존 룰 제거 후 새 룰
iptables -t nat -F REDSOCKS 2>/dev/null || true
iptables -t nat -X REDSOCKS 2>/dev/null || true
iptables -t nat -N REDSOCKS
for net in 0.0.0.0/8 10.0.0.0/8 127.0.0.0/8 169.254.0.0/16 172.16.0.0/12 192.168.0.0/16 224.0.0.0/4 240.0.0.0/4; do
    iptables -t nat -A REDSOCKS -d $net -j RETURN
done
iptables -t nat -A REDSOCKS -p tcp -j REDIRECT --to-ports 12345
iptables -t nat -A OUTPUT -p tcp -j REDSOCKS

# redsocks 백그라운드
redsocks -c /tmp/redsocks.conf &
echo $! >/var/run/redsocks.pid

echo -e "${GREEN}[OK]${NC} 전체 TCP 트래픽이 ZeroKey SOCKS5로 향합니다."
echo "복구하려면:  sudo scripts/undo_tunnel.sh"
