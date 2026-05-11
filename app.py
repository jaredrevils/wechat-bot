from flask import Flask, request
import requests
import hashlib
import xml.etree.ElementTree as ET
import time

app = Flask(__name__)

TOKEN = "wechat_gemini_bot"
API_KEY = "sk-2PXqz5UXVWRe2dv17UmHolh7nHGVZOucRg8skJQhJin0CMxP"
BASE_URL = "https://api.deepseek.com"

def call_gemini(user_msg):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-v4-flash",
        "messages": [{"role": "user", "content": user_msg}]
    }
    res = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=data)
    return res.json()["choices"][0]["message"]["content"]

@app.route('/wechat', methods=['GET'])
def verify():
    params = [TOKEN, request.args.get('timestamp'), request.args.get('nonce')]
    params.sort()
    sign = hashlib.sha1(''.join(params).encode()).hexdigest()
    if sign == request.args.get('signature'):
        return request.args.get('echostr')
    return 'error'

@app.route('/wechat', methods=['POST'])
def reply():
    xml = ET.fromstring(request.data)
    user = xml.find('FromUserName').text
    myid = xml.find('ToUserName').text
    msg_type = xml.find('MsgType').text
    if msg_type != 'text':
        return 'success'
    msg = xml.find('Content').text
    reply_text = call_gemini(msg)
    return f"""<xml>
<ToUserName><![CDATA[{user}]]></ToUserName>
<FromUserName><![CDATA[{myid}]]></FromUserName>
<CreateTime>{int(time.time())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{reply_text}]]></Content>
</xml>"""

if __name__ == '__main__':
    app.run()
