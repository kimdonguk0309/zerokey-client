#!/usr/bin/env bash
set -e
echo "ZeroKey 설치 중..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
chmod +x run.py
echo "설치 완료!  ./run.py  또는  python run.py"
