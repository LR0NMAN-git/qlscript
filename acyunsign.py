# -*- coding: utf-8 -*-
'''new Env('傲晨云签到');'''
import os
import sys
import time
import json
import logging
from datetime import datetime

try:
    import requests
except Exception as e:
    print(str(e) + "\n缺少requests模块, 请执行命令：pip3 install requests\n")
    sys.exit(1)

# 禁用代理
os.environ['no_proxy'] = '*'
# 抑制SSL警告
requests.packages.urllib3.disable_warnings()

try:
    from notify import send
except Exception as err:
    print("无推送文件")

# 设置日志格式
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# 从环境变量获取Authorization令牌
AUTHORIZATION = os.environ.get('acyuncookie', '')
if not AUTHORIZATION:
    logger.error("未设置环境变量acyuncookie，请在青龙面板中添加该环境变量")
    sys.exit(1)

def send_notification(title, message):
    """发送通知"""
    try:
        send(title, message)
        logger.info("通知发送成功")
    except Exception as e:
        logger.info(f"通知发送失败: {str(e)}")

def get_cookies_from_options():
    """调用OPTIONS预签到接口获取cookie"""
    url = "https://www.acyun.cn/api/appUserWeeklySign/userSign"
    headers = {
        "Host": "www.acyun.cn",
        "Sec-Fetch-Site": "cross-site",
        "Accept-Encoding": "gzip, deflate, br",
        "Access-Control-Request-Method": "POST",
        "Sec-Fetch-Mode": "cors",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "Origin": "https://www.aochenyun.cn",
        "Access-Control-Request-Headers": "appdeviceld,appsource,authorization,channelcode,content-type",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "Referer": "https://www.aochenyun.cn/",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Accept": "*/*"
    }
    
    try:
        response = requests.options(url, headers=headers, verify=False)
        # 获取响应头中的Set-Cookie
        set_cookie = response.headers.get('Set-Cookie', '')
        # 解析cookie
        cookies = {}
        if set_cookie:
            for cookie in set_cookie.split(';'):
                cookie = cookie.strip()
                if '=' in cookie:
                    key, value = cookie.split('=', 1)
                    cookies[key] = value
        logger.info(f"预签到获取cookie成功: {cookies}")
        return cookies
    except Exception as e:
        logger.error(f"预签到失败: {str(e)}")
        send_notification("傲晨云签到失败", f"预签到失败: {str(e)}")
        return None

def get_sign_info(cookies):
    """调用签到信息接口获取数据"""
    url = "https://www.acyun.cn/api/appUserWeeklySign/getAppUserWeeklySignByUserId"
    headers = {
        "Host": "www.acyun.cn",
        "Accept": "application/json, text/plain, */*",
        "Authorization": AUTHORIZATION,
        "Sec-Fetch-Site": "cross-site",
        "appDeviceld": "2b76d1b1ab98960ef2b9dc4d1b3ef3dc",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "Sec-Fetch-Mode": "cors",
        "channelCode": "",
        "Origin": "https://www.aochenyun.cn",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "Referer": "https://www.aochenyun.cn/",
        "Accept-Encoding": "gzip, deflate, br",
        "appSource": "3",
        "Sec-Fetch-Dest": "empty",
        "Connection": "keep-alive"
    }
    
    try:
        response = requests.post(url, headers=headers, cookies=cookies, verify=False)
        response.raise_for_status()
        result = response.json()
        logger.info(f"签到信息接口返回结果: {json.dumps(result, ensure_ascii=False)}")
        
        if result.get("code") == 0:
            data = result.get("data")
            if data:
                logger.info("获取签到信息成功")
                return data
            else:
                logger.error("签到信息接口返回data为空")
                return None
        else:
            logger.error(f"签到信息接口返回错误: {result.get('msg')}")
            return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"签到信息接口HTTP错误: {str(e)}")
        logger.error(f"响应内容: {response.text if 'response' in locals() else '无响应'}")
        return None
    except Exception as e:
        logger.error(f"获取签到信息失败: {str(e)}")
        return None

def get_day_of_week():
    """获取当天是星期几，返回中文星期X"""
    today = datetime.now()
    day_of_week = today.weekday()  # 0=周一，1=周二，...，6=周日
    chinese_weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    return day_of_week, chinese_weekdays[day_of_week]

def build_request_body(sign_info):
    """构建请求体"""
    day_of_week_num, day_of_week_chinese = get_day_of_week()
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    # 使用签到信息接口返回的数据作为基础请求体
    body = sign_info.copy()
    
    # 设置当天的星期几参数为1
    current_day = days[day_of_week_num]
    body[current_day] = 1
    
    # 设置isSupplementarySignature为false
    body["isSupplementarySignature"] = False
    
    # 确保dayOfWeek为中文星期X格式
    body["dayOfWeek"] = day_of_week_chinese
    
    return body

def sign_in(cookies, sign_info):
    """调用POST签到接口"""
    url = "https://www.acyun.cn/api/appUserWeeklySign/userSign"
    headers = {
        "Host": "www.acyun.cn",
        "Accept": "application/json, text/plain, */*",
        "Authorization": AUTHORIZATION,
        "Sec-Fetch-Site": "cross-site",
        "appDeviceld": "2b76d1b1ab98960ef2b9dc4d1b3ef3dc",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "Sec-Fetch-Mode": "cors",
        "channelCode": "",
        "Origin": "https://www.aochenyun.cn",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "Referer": "https://www.aochenyun.cn/",
        "Accept-Encoding": "gzip, deflate, br",
        "appSource": "3",
        "Sec-Fetch-Dest": "empty",
        "Connection": "keep-alive",
        "Content-Type": "application/json"
    }
    
    # 构建请求体
    body = build_request_body(sign_info)
    logger.info(f"签到请求体: {json.dumps(body, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, headers=headers, cookies=cookies, json=body, verify=False)
        response.raise_for_status()
        result = response.json()
        logger.info(f"签到响应: {json.dumps(result, ensure_ascii=False)}")
        return result
    except requests.exceptions.HTTPError as e:
        logger.error(f"签到HTTP错误: {str(e)}")
        logger.error(f"响应内容: {response.text if 'response' in locals() else '无响应'}")
        send_notification("傲晨云签到失败", f"签到HTTP错误: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"签到失败: {str(e)}")
        send_notification("傲晨云签到失败", f"签到失败: {str(e)}")
        return None

def main():
    """主函数"""
    logger.info("开始执行傲晨云签到脚本")
    
    # 1. 调用OPTIONS预签到接口获取cookie
    cookies = get_cookies_from_options()
    if not cookies:
        logger.error("获取cookie失败，签到终止")
        return
    
    # 2. 调用签到信息接口获取数据
    sign_info = get_sign_info(cookies)
    if not sign_info:
        logger.error("获取签到信息失败，签到终止")
        return
    
    # 3. 调用POST签到接口
    result = sign_in(cookies, sign_info)
    if not result:
        logger.error("签到失败，签到终止")
        return
    
    # 4. 处理签到结果
    code = result.get("code", -1)
    msg = result.get("msg", "未知错误")
    
    if code == 0:
        logger.info("签到成功")
        send_notification("傲晨云签到成功", f"签到结果: {msg}")
    elif code == 401:
        logger.error("登录信息已过期，请重新登录")
        send_notification("傲晨云签到失败", "登录信息已过期，请重新登录")
    else:
        logger.error(f"签到失败，错误码: {code}，错误信息: {msg}")
        send_notification("傲晨云签到失败", f"错误码: {code}，错误信息: {msg}")
    
    logger.info("傲晨云签到脚本执行完成")

if __name__ == "__main__":
    main()
