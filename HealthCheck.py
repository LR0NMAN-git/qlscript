import socket
import time
from notify import send
import os
import platform

content=""

def append(msg):
    global content
    content+=(msg+"\n")

# 连接函数
def connection(ip,port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)  # 设置超时
        try:
            s.connect((ip, port))
            print(f"成功连接 {ip}:{port}")
            return True
        except Exception as e:
            print(f"连接失败 {ip}:{port} - {e}")
            return False

# Ping 函数
def ping(ip):
    # 根据操作系统选择合适的 ping 命令
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip]  # 只 ping 1 次

    # 使用 os.system 来执行 ping 命令
    return os.system(' '.join(command)) == 0

# 主逻辑
def main(ip_ports, ips):
     # 检查 ping
    for ip in ips:
        if not ping(ip[1]):
            append(f"{ip[0]},失败")
        else:
            append(f"{ip[0]},成功")
    
    # 检查 IP:PORT 连接
    for ip_port in ip_ports:
        if not connection(ip_port[1],ip_port[2]):
            append(f"{ip_port[0]},失败")
        else:
            append(f"{ip_port[0]},成功")



if __name__ == "__main__":
    # 配置要检查的 IP 和端口列表
    ip_ports = [
        ("青龙","192.168.10.171", 5700),
        ("mysql","192.168.10.171", 3306),
        ("frpc","192.168.10.171", 7400),
        ("phpmyadmin","192.168.10.171", 8089),
        ("bark","192.168.10.171", 8080)
        # 添加更多的 IP:PORT 组合
    ]
    
    # 配置要 ping 的 IP
    ips = [
        ("PC","192.168.10.241")
    ]  # 例如，Google 的公共 DNS 服务器

    main(ip_ports, ips)

    send("Health Check",content)
