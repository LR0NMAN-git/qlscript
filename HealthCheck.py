'''
new Env('系统检查');
'''
import os
import platform
import socket
from datetime import datetime, timedelta

from git import Repo, GitCommandError
from notify import send

content = ""
isNotify = False


def append(msg):
    global content
    content += (msg + "\n")


# 连接函数
def connection(ip, port):
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


def check_git_commits():
    REPO_PATH = "/HealthCheck/repo/jdpro"  # 青龙面板建议用绝对路径
    REMOTE_URL = "https://github.com/6dylan6/jdpro.git"
    TARGET_FILE = "jd_wskey.py"
    # 初始化/拉取仓库
    try:
        if not os.path.exists(REPO_PATH):
            Repo.clone_from(REMOTE_URL, REPO_PATH)
            print(f"✅ 仓库克隆成功至 {REPO_PATH}")
        repo = Repo(REPO_PATH)
        print(f"✅ 强制更新远程内容 {REPO_PATH}")
        repo.remotes.origin.pull()
    except GitCommandError as e:
        print(f"❌ 仓库操作失败: {str(e)}")
        return

    # 获取今日时间范围（UTC时间）
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    print(today_start)
    print(today_end)
    # 检查目标文件提交记录
    try:
        commits = list(repo.iter_commits('origin/main', paths=TARGET_FILE))
        today_commits = [
            commit for commit in commits
            if today_start.timestamp() <= commit.committed_date <= today_end.timestamp()
        ]
    except Exception as e:
        print(f"❌ 提交记录解析失败: {str(e)}")
        return

    # 输出结果（青龙面板需标准输出）
    if today_commits:
        latest = today_commits[0]
        time_str = datetime.fromtimestamp(latest.committed_date).strftime('%Y-%m-%d %H:%M:%S')
        print(f"📌 文件 {TARGET_FILE} 今日有提交\n最新提交哈希: {latest.hexsha[:7]}\n提交时间: {time_str}")
        append(f"文件 {TARGET_FILE} 今日有提交\n最新提交哈希: {latest.hexsha[:7]}\n提交时间: {time_str}")
    else:
        print(f"⏳ 文件 {TARGET_FILE} 今日无新提交")


# 主逻辑
def main(ip_ports, ips):
    global isNotify
    # 检查 ping
    for ip in ips:
        if not ping(ip[1]):
            isNotify = True
            append(f"{ip[0]}-offline")

    # 检查 IP:PORT 连接
    for ip_port in ip_ports:
        if not connection(ip_port[1], int(ip_port[2])):
            isNotify = True
            append(f"{ip_port[0]}-offline")

    check_git_commits()


if __name__ == "__main__":
    # 配置要检查的 IP 和端口列表
    ip_ports = []
    # 配置要 ping 的 IP
    ips = []

    if "HealthCheck_Service" in os.environ:
        lines = os.environ['HealthCheck_Service'].splitlines()
        ip_ports = [tuple(line.split(',')) for line in lines if line.strip()]
    if "HealthCheck_Server" in os.environ:
        lines = os.environ['HealthCheck_Server'].splitlines()
        ips = [tuple(line.split(',')) for line in lines if line.strip()]

    main(ip_ports, ips)

    if isNotify:
        send("Health Check", content)
