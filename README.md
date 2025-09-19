# ZeroKey Client – 서버가 키를 모르는 VPN  
![build](https://github.com/yourid/zerokey-client/workflows/build/badge.svg)
![License](https://img.shields.io/badge/license-AGPL--3.0-blue)

## 5초 설치
```bash
git clone https://github.com/yourid/zerokey-client.git
cd zerokey-client
bash scripts/install.sh
python run.py -s zerokey.example.com:443

## 🚀 한방에 전체 시스템 터널링 (Linux)
```bash
curl -sSL https://raw.githubusercontent.com/YOUR_ID/zerokey-client/main/scripts/system_tunnel.sh | sudo bash

## 복구
'''bash
sudo bash <(curl -sSL https://raw.githubusercontent.com/YOUR_ID/zerokey-client/main/scripts/undo_tunnel.sh)
