#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
东风日产签到脚本
基于抓包数据创建
"""

import os
import sys
import json
import time
import random
import logging
import requests
from datetime import datetime

# 设置日志格式
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# 从环境变量获取配置，或使用默认值（从抓包数据提取）
SESSION_ID = os.environ.get('NISSAN_SESSION_ID', 'f8f09428256aa1c6cea74519b8a98e63d2219fc3')
DEVICE_DID = os.environ.get('NISSAN_DEVICE_DID', '3D800F80F3064298BBE834FB59B102841707056758604271')
DISTINCT_ID = os.environ.get('NISSAN_DISTINCT_ID', '31E17EB31DBD47B9B31DD4EEA8330E07')

if not all([SESSION_ID, DEVICE_DID, DISTINCT_ID]):
    logger.error("请设置环境变量:")
    logger.error("NISSAN_SESSION_ID: 会话ID")
    logger.error("NISSAN_DEVICE_DID: 设备ID")
    logger.error("NISSAN_DISTINCT_ID: 唯一标识ID")
    sys.exit(1)

# API地址
API_URL = "https://nvitapp.venucia.com/gw/api"

# 生成随机字符串
def generate_nonce():
    """生成随机nonce字符串"""
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join(random.choice(chars) for _ in range(32))

# 生成时间戳
def get_timestamp():
    """生成时间戳"""
    return str(int(time.time() * 1000))

# 构建请求头
def build_headers():
    """构建请求头"""
    timestamp = get_timestamp()
    nonce = generate_nonce()
    
    headers = {
        "Host": "nvitapp.venucia.com",
        "Accept": "*/*",
        "timestamp": timestamp,
        "noncestr": nonce,
        "api_request_time": timestamp,
        "Accept-Encoding": "gzip, deflate, br",
        "apiversion": "1",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "Content-Type": "application/json;charset=utf-8",
        "User-Agent": "%E4%B8%9C%E9%A3%8E%E6%97%A5%E4%BA%A7/6 CFNetwork/3860.300.31 Darwin/25.2.0",
        "Connection": "keep-alive",
        "api": "ly.dfv.app.behaviour.send",
        "Cookie": f"session_id={SESSION_ID}; distinct_id={DISTINCT_ID}"
    }
    return headers

# 构建请求体
def build_payload():
    """构建请求体"""
    device_id = generate_nonce()[:32]
    event_time_ms = get_timestamp()
    
    payload = {
        "content": [
            {
                "sdk_version": "2.0.7.32",
                "session_id": SESSION_ID,
                "app_key": "trloce588tm6gmsi",
                "event_detail": {
                    "page_title": ""
                },
                "browser_code": "5580b6a3c970ac69ef0e53540d3bdcf6",
                "event_type": "pageview",
                "app_version": "3.4.8",
                "device_did": DEVICE_DID,
                "app_channel": "App Store",
                "device_id": device_id,
                "method": "precode",
                "distinct_id": DISTINCT_ID,
                "url_path": "LYMyPageViewController",
                "is_encode": "1",
                "utm_source": "",
                "environment_type": "business",
                "lan_ip": "error",
                "referrer": "LYMyPageViewController",
                "platform": "iOS",
                "event_id": "pageview",
                "event_time_ms": event_time_ms,
                "user_info": {
                    "carBind_status": "1",
                    "appSkin": "NISSANAPP",
                    "dcmType": "l21bccs2plus",
                    "model": "1",
                    "uuid": DISTINCT_ID,
                    "userVerify_status": "1",
                    "oneID": DISTINCT_ID
                },
                "data_type": "app",
                "device_type": "phone",
                "user_ip": "",
                "platform_detail": {
                    "manufacture": "Apple",
                    "device_brand": "iPhone",
                    "network_type": "5G",
                    "app_code": "东风日产",
                    "os": "iOS",
                    "lat": "",
                    "screen_height": "852",
                    "brand_code": "UBA_RC",
                    "initial_time": str(int(time.time())),
                    "lng": "",
                    "os_version": "26.2",
                    "screen_width": "393",
                    "device_model": "iPhone16,1",
                    "carrier": "65535"
                }
            },
            {
                "sdk_version": "2.0.7.32",
                "session_id": SESSION_ID,
                "app_key": "trloce588tm6gmsi",
                "browser_code": "5580b6a3c970ac69ef0e53540d3bdcf6",
                "event_detail": {
                    "btn_name": "签到",
                    "page_title": "我的页",
                    "btn_title": "签到",
                    "user_type": "网联车主,油车",
                    "res_url": "",
                    "content_type": "个人信息栏"
                },
                "event_type": "click",
                "app_version": "3.4.8",
                "device_did": DEVICE_DID,
                "app_channel": "App Store",
                "device_id": device_id,
                "method": "code",
                "distinct_id": DISTINCT_ID,
                "url_path": "LYMyPageViewController",
                "is_encode": "1",
                "utm_source": "",
                "environment_type": "business",
                "lan_ip": "error",
                "referrer": "LYMyPageViewController",
                "platform": "iOS",
                "event_time_ms": str(int(event_time_ms) + 100),
                "event_id": "c_my_entr",
                "user_info": {
                    "carBind_status": "1",
                    "appSkin": "NISSANAPP",
                    "dcmType": "l21bccs2plus",
                    "model": "1",
                    "uuid": DISTINCT_ID,
                    "userVerify_status": "1",
                    "oneID": DISTINCT_ID
                },
                "data_type": "app",
                "device_type": "phone",
                "user_ip": "",
                "platform_detail": {
                    "manufacture": "Apple",
                    "device_brand": "iPhone",
                    "network_type": "5G",
                    "app_code": "东风日产",
                    "os": "iOS",
                    "lat": "",
                    "screen_height": "852",
                    "brand_code": "UBA_RC",
                    "initial_time": str(int(time.time())),
                    "lng": "",
                    "os_version": "26.2",
                    "screen_width": "393",
                    "device_model": "iPhone16,1",
                    "carrier": "65535"
                }
            },
            {
                "sdk_version": "2.0.7.32",
                "session_id": SESSION_ID,
                "app_key": "trloce588tm6gmsi",
                "event_detail": {
                    "page_title": "",
                    "controller_type": "UIImageView",
                    "btn_title": " 签到"
                },
                "browser_code": "5580b6a3c970ac69ef0e53540d3bdcf6",
                "event_type": "click",
                "app_version": "3.4.8",
                "device_did": DEVICE_DID,
                "app_channel": "App Store",
                "device_id": device_id,
                "method": "precode",
                "distinct_id": DISTINCT_ID,
                "url_path": "LYMyPageViewController",
                "is_encode": "1",
                "utm_source": "",
                "environment_type": "business",
                "lan_ip": "error",
                "referrer": "LYMyPageViewController",
                "platform": "iOS",
                "event_id": "btn_click",
                "event_time_ms": str(int(event_time_ms) + 200),
                "user_info": {
                    "carBind_status": "1",
                    "appSkin": "NISSANAPP",
                    "dcmType": "l21bccs2plus",
                    "model": "1",
                    "uuid": DISTINCT_ID,
                    "userVerify_status": "1",
                    "oneID": DISTINCT_ID
                },
                "data_type": "app",
                "device_type": "phone",
                "user_ip": "",
                "platform_detail": {
                    "manufacture": "Apple",
                    "device_brand": "iPhone",
                    "network_type": "5G",
                    "app_code": "东风日产",
                    "os": "iOS",
                    "lat": "",
                    "screen_height": "852",
                    "brand_code": "UBA_RC",
                    "initial_time": str(int(time.time())),
                    "lng": "",
                    "os_version": "26.2",
                    "screen_width": "393",
                    "device_model": "iPhone16,1",
                    "carrier": "65535"
                }
            }
        ]
    }
    return payload

# 发送签到请求
def send_sign_request():
    """发送签到请求"""
    try:
        headers = build_headers()
        payload = build_payload()
        
        logger.info("开始执行东风日产签到")
        logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 手动处理JSON编码，确保UTF-8格式
        import json
        json_payload = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        headers['Content-Length'] = str(len(json_payload))
        
        # 发送请求
        response = requests.post(API_URL, headers=headers, data=json_payload, verify=False)
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        logger.info(f"签到响应: {json.dumps(result, ensure_ascii=False)}")
        
        if result.get("result") == "1" and result.get("msg") == "success":
            logger.info("签到成功!")
            return True
        else:
            logger.error(f"签到失败: {result.get('msg', '未知错误')}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"网络错误: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"未知错误: {str(e)}")
        return False

# 主函数
def main():
    """主函数"""
    # 禁用代理
    os.environ['no_proxy'] = '*'
    # 抑制SSL警告
    requests.packages.urllib3.disable_warnings()
    
    success = send_sign_request()
    
    if success:
        logger.info("东风日产签到脚本执行完成")
        sys.exit(0)
    else:
        logger.error("东风日产签到脚本执行失败")
        sys.exit(1)

if __name__ == "__main__":
    main()