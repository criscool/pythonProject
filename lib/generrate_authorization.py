"""
============================================
Author:宋显宾
Time:2025-01-09 20:44:00
Project:封装base64
Company:北京安帝科技有限公司
===========================================
"""
import base64
# print(data["username"])
# print(data["password"])

# print(newdata)
#编码函数
class MyAuthorization:
    def base64_encode(slef,msg):
        # 将字符串转换为字节格式
        msg_bytes = msg.encode('utf-8')
        # print(msg_bytes)
        # 执行Base64编码
        encoded_bytes = base64.b64encode(msg_bytes)
        # print("encode后的信息是：", encoded_bytes)
        # 将编码的字节形式转换为字符串并返回
        return "Basic " + encoded_bytes.decode('utf-8')

    # 解码函数
    def base64_decode(encoded_msg):
        # 将编码的字符串转换为字节格式
        encoded_bytes = encoded_msg.encode('utf-8')
        # 执行Base64解码
        decoded_bytes = base64.b16decode(encoded_bytes)
        return "Basic " + decoded_bytes.decode('utf-8')

if __name__ == '__main__':
        data = {"username": "superadmin", "password": "superadmin:Admin@123", "host": "172.16.8.7"}
        msg = data["password"]
        # print("msg信息是：", msg)
        MyAuth = MyAuthorization()
        MyAuth.base64_encode(msg)
