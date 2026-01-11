# Copyright 2026 Sakura-频道总结助手
# 
# 本项目采用 CC BY-NC-SA 4.0 许可证
# 您可以自由地共享、修改本作品，但必须遵守以下条件：
# - 署名：必须提供本项目的原始来源链接
# - 非商业：禁止任何商业用途和分发
# - 相同方式共享：衍生作品必须采用相同的许可证
# 
# 本项目源代码：https://github.com/Sakura520222/Sakura-Channel-Summary-Assistant
# 许可证全文：https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh

import subprocess
import time
import os
import sys

print("正在重启Sakura频道总结助手...")

# 1. 先停止当前进程（通过taskkill）
try:
    # 查找并停止所有python进程（除了当前进程）
    import psutil
    current_pid = os.getpid()
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                pid = proc.info['pid']
                if pid != current_pid:
                    # 检查是否在运行我们的脚本
                    try:
                        cmdline = proc.cmdline()
                        if 'main.py' in ' '.join(cmdline):
                            print(f"停止进程 {pid}: {cmdline}")
                            proc.terminate()
                            proc.wait(timeout=5)
                    except:
                        pass
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
except ImportError:
    # 如果没有psutil，使用taskkill
    os.system('taskkill /F /IM python.exe')
    time.sleep(2)

# 2. 等待端口释放
time.sleep(3)

# 3. 启动新进程
print("启动新的机器人进程...")
subprocess.Popen([sys.executable, 'main.py'])
print("重启完成！")
