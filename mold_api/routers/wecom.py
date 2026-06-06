# -*- coding: utf-8 -*-
import time
import xml.etree.ElementTree as ET
from fastapi import APIRouter, Request, Response
import hashlib
import base64
from Crypto.Cipher import AES
from utils.db_conn import SessionLocal
from models.external_task import ExternalTask


# ========== 请务必替换为您的真实配置 ==========
TOKEN = "mold"
ENCODING_AES_KEY = "r9XKQx3K5rhG5vltoGfArmYptAS7okHyNkr30Fgp6UW"  # 43位字符
CORP_ID = "wwe45d9591b9a6ca0d"
# ===========================================

router = APIRouter(prefix="/wxwork", tags=["wecom"])

class WXBizMsgCrypt:
    def __init__(self, token, encoding_aes_key, corp_id):
        self.token = token
        self.corp_id = corp_id
        self.aes_key = base64.b64decode(encoding_aes_key + "=")

    def get_signature(self, timestamp, nonce, encrypt):
        """计算签名，确保所有参数都是字符串且不为 None"""
        parts = [self.token,
                 timestamp if timestamp is not None else "",
                 nonce if nonce is not None else "",
                 encrypt if encrypt is not None else ""]
        parts.sort()
        sha = hashlib.sha1()
        sha.update("".join(parts).encode())
        return sha.hexdigest()

    def decrypt(self, encrypt):
        """解密消息"""
        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.aes_key[:16])
        plain_text = cipher.decrypt(base64.b64decode(encrypt))
        # 去除补位
        pad = plain_text[-1]
        if pad < 32:
            plain_text = plain_text[:-pad]
        # 解析消息长度和内容
        msg_len = int.from_bytes(plain_text[16:20], byteorder='big')
        msg = plain_text[20:20+msg_len].decode()
        return msg

    def encrypt(self, plain):
        """加密消息"""
        import random
        random_bytes = bytes([random.randint(0, 255) for _ in range(16)])
        msg_len = len(plain).to_bytes(4, byteorder='big')
        plain_bytes = plain.encode()
        # 计算补位长度
        pad_len = 32 - (len(random_bytes) + 4 + len(plain_bytes)) % 32
        pad_bytes = bytes([pad_len] * pad_len)
        to_encrypt = random_bytes + msg_len + plain_bytes + pad_bytes
        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.aes_key[:16])
        encrypted = cipher.encrypt(to_encrypt)
        return base64.b64encode(encrypted).decode()

    def verify_url(self, msg_signature, timestamp, nonce, echostr):
        """验证 URL 有效性"""
        signature = self.get_signature(timestamp, nonce, echostr)
        if signature != msg_signature:
            return -1, None
        decrypted = self.decrypt(echostr)
        return 0, decrypted

    def decrypt_msg(self, encrypt, msg_signature, timestamp, nonce):
        """解密接收到的消息"""
        signature = self.get_signature(timestamp, nonce, encrypt)
        if signature != msg_signature:
            return -1, None
        decrypted = self.decrypt(encrypt)
        return 0, decrypted

    def encrypt_msg(self, plain):
        """加密回复消息"""
        encrypt = self.encrypt(plain)
        timestamp = str(int(time.time()))
        nonce = str(int(time.time()))[-6:]
        signature = self.get_signature(timestamp, nonce, encrypt)
        xml = f"""<xml>
<Encrypt><![CDATA[{encrypt}]]></Encrypt>
<MsgSignature><![CDATA[{signature}]]></MsgSignature>
<TimeStamp>{timestamp}</TimeStamp>
<Nonce><![CDATA[{nonce}]]></Nonce>
</xml>"""
        return xml

crypto = WXBizMsgCrypt(TOKEN, ENCODING_AES_KEY, CORP_ID)

# ---------- 回调接口 ----------
@router.api_route("/callback", methods=["GET", "POST"])
async def wecom_callback(request: Request):
    if request.method == "GET":
        params = request.query_params
        msg_signature = params.get("msg_signature")
        timestamp = params.get("timestamp")
        nonce = params.get("nonce")
        echostr = params.get("echostr")
        print(f"GET params: {params}")
        if not echostr:
            return Response(content="缺少 echostr 参数", status_code=400)
        ret, decrypted = crypto.verify_url(msg_signature, timestamp, nonce, echostr)
        if ret != 0:
            return Response(content="签名验证失败", status_code=403)
        return Response(content=decrypted, media_type="text/plain")

    else:
        # POST 接收消息
        body = await request.body()
        params = request.query_params
        msg_signature = params.get("msg_signature")
        timestamp = params.get("timestamp")
        nonce = params.get("nonce")

        print(f"=== POST 请求收到 ===")
        print(f"Body 前300字符: {body[:300]}")

        # 解析 XML 获取 Encrypt
        root = ET.fromstring(body)
        encrypt = root.find("Encrypt").text

        ret, decrypted_xml = crypto.decrypt_msg(encrypt, msg_signature, timestamp, nonce)
        if ret != 0:
            print("解密失败")
            return Response(content="解密失败", status_code=403)

        print(f"解密后的明文 XML: {decrypted_xml}")

        # 解析明文 XML
        msg_root = ET.fromstring(decrypted_xml)
        msg_type = msg_root.find("MsgType").text
        print(f"消息类型: {msg_type}")

        if msg_type == "text":
            from_user = msg_root.find("FromUserName").text
            content = msg_root.find("Content").text
            print(f"收到文本消息: 用户={from_user}, 内容={content}")

            reply_text = process_progress_message(content, from_user)
            print(f"处理结果回复内容: {reply_text}")

            if reply_text:
                reply_xml = build_reply_xml(from_user, reply_text)
                encrypted_reply = crypto.encrypt_msg(reply_xml)
                return Response(content=encrypted_reply, media_type="application/xml")
        else:
            print(f"消息类型不是 text，忽略")

        return Response(content="success", media_type="text/plain")

# ---------- 业务逻辑：解析进度并更新 ----------
def process_progress_message(content: str, from_user: str) -> str:
    import re
    # 匹配格式：任务名 进度数字（如 "模具A 60%" 或 "模具A 60"）
    pattern = r'([\u4e00-\u9fa5a-zA-Z0-9]+)\s*(\d{1,3})%?\s*'
    match = re.search(pattern, content)
    if not match:
        return f"未识别到进度信息，请发送如「任务名 60%」的格式。"

    task_name = match.group(1).strip()
    progress = int(match.group(2))
    if progress < 0 or progress > 100:
        return "进度值必须在0-100之间。"

    print(f"解析结果: 任务名={task_name}, 进度={progress}")

    db = SessionLocal()
    try:
        task = db.query(ExternalTask).filter(
            ExternalTask.task_name.contains(task_name)
        ).first()
        if not task:
            return f"未找到任务「{task_name}」，请检查任务名称是否正确。"
        print(f"找到任务: ID={task.id}, 原进度={task.progress_percent}")
        task.progress_percent = progress
        from datetime import datetime
        task.last_updated = datetime.now()
        db.commit()
        print(f"数据库更新成功，新进度={progress}")
        return f"✅ 已更新「{task_name}」进度为 {progress}%，感谢上报！"
    except Exception as e:
        db.rollback()
        print(f"数据库更新异常: {e}")
        return f"更新失败：{str(e)}"
    finally:
        db.close()

# ---------- 构造回复 XML ----------
def build_reply_xml(to_user: str, content: str) -> str:
    timestamp = str(int(time.time()))
    return f"""<xml>
<ToUserName><![CDATA[{to_user}]]></ToUserName>
<FromUserName><![CDATA[{CORP_ID}]]></FromUserName>
<CreateTime>{timestamp}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{content}]]></Content>
</xml>"""