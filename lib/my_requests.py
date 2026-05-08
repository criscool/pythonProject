""" 
============================================
Author:宋显宾 
Time:2025-01-09 20:44:00 
Project:封装requests 
Company:北京安帝科技有限公司 
===========================================
""" 

import requests 
import urllib3 

from conf.url_configs import  base_headers


class MyRequests: 
    def __init__(self): 
        # 请求头 
        self.headers = base_headers
    
    def __deal_header(self, headers): 
        """处理请求头""" 
        if headers: 
            self.headers.update(headers) 
        return self.headers 
    
    # 方法  post/put...   json=xxx,  get...  params=xxx 
    def send_requests(self, method, url, json, headers=None, verify=False): 
        # 处理请求头 
        #调用requests的方法去发起一个请求，并得到响应结果 
        request_headers = self.__deal_header(headers) 
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 
        
        if method.upper() == "GET": 
            resp = requests.request(method, url, params=json, headers=request_headers, verify=verify) 
        elif method.upper() == "POST": 
            resp = requests.request(method, url, json=json, headers=request_headers, verify=verify) 
        elif method.upper() == "PUT": 
            resp = requests.request(method, url, json=json, headers=request_headers, verify=verify) 
        elif method.upper() == "DELETE": 
            resp = requests.request(method, url, json=json, headers=request_headers, verify=verify) 
        else: 
            resp = requests.request(method, url, json=json, headers=request_headers, verify=verify) 
        return resp 
    
