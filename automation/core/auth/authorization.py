"""
============================================
Author:宋显宾
Time:2025-01-09 20:44:00
Project:封装base64
Company:北京安帝科技有限公司
===========================================
"""
import base64

class MyAuthorization:
    def base64_encode(self, msg):
        msg_bytes = msg.encode('utf-8')
        encoded_bytes = base64.b64encode(msg_bytes)
        return "Basic " + encoded_bytes.decode('utf-8')

    def base64_decode(self, encoded_msg):
        encoded_bytes = encoded_msg.encode('utf-8')
        decoded_bytes = base64.b16decode(encoded_bytes)
        return "Basic " + decoded_bytes.decode('utf-8')

if __name__ == '__main__':
        data = {"username": "superadmin", "password": "superadmin:Admin@123", "host": "172.16.8.7"}
        msg = data["password"]
        MyAuth = MyAuthorization()
        MyAuth.base64_encode(msg)
