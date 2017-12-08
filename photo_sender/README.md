# Photo Sender
一定間隔でUSBカメラから画像を撮影し、指定したURLにPOSTする。
Raspberry Piで常時起動することを想定している。

## Requirement
* python2
* opencv2
* requests

## Installation
```bash
sudo apt install python-opencv
wget https://bootstrap.pypa.io/get-pip.py
sudo python2 get-pip.py
sudo python2 -m pip install requests
```

## Usage
```bash
export LOG_LEVEL=INFO
export PHOTO_SENDER_INTERVAL=60
export PHOTO_SENDER_API=https://example.com/api
export PHOTO_SENDER_CLIENT_ID=xxxxx
export PHOTO_SENDER_CLIENT_SECRET=xxxxx

python2 photo_sender.py
```
