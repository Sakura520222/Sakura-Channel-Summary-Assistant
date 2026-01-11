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

# 获取当前工作目录
current_dir = os.getcwd()
print(f"当前工作目录: {current_dir}")

# 1. 更精确地停止当前进程
try:
    import psutil
    current_pid = os.getpid()
    
    # 查找并停止当前目录下的main.py进程
    processes_to_stop = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
        try:
            # 检查是否是Python进程
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                pid = proc.info['pid']
                
                # 排除当前进程
                if pid == current_pid:
                    continue
                
                # 获取进程信息
                cmdline = proc.info.get('cmdline', [])
                cmdline_str = ' '.join(cmdline) if cmdline else ''
                cwd = proc.info.get('cwd', '')
                
                # 判断是否是我们需要停止的进程
                is_our_main_py = False
                
                # 方法1: 检查是否运行main.py
                if 'main.py' in cmdline_str:
                    # 方法2: 检查工作目录是否匹配
                    if cwd and os.path.exists(cwd):
                        # 标准化路径进行比较
                        norm_cwd = os.path.normpath(cwd)
                        norm_current = os.path.normpath(current_dir)
                        if norm_cwd == norm_current:
                            is_our_main_py = True
                        else:
                            # 检查命令行中的路径是否包含当前目录
                            abs_main_path = os.path.join(norm_current, 'main.py')
                            norm_abs_main = os.path.normpath(abs_main_path)
                            if norm_abs_main in cmdline_str:
                                is_our_main_py = True
                    else:
                        # 没有工作目录信息，检查命令行
                        # 如果命令行最后是main.py，可能是我们的进程
                        if cmdline and len(cmdline) > 1:
                            last_arg = cmdline[-1]
                            if last_arg.endswith('main.py'):
                                # 检查是否是相对路径
                                if last_arg == 'main.py':
                                    is_our_main_py = True
                                # 检查是否是绝对路径
                                elif os.path.exists(last_arg):
                                    abs_path = os.path.abspath(last_arg)
                                    current_main = os.path.join(current_dir, 'main.py')
                                    if os.path.normpath(abs_path) == os.path.normpath(current_main):
                                        is_our_main_py = True
                
                if is_our_main_py:
                    processes_to_stop.append((pid, cmdline_str[:80], cwd))
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    # 停止找到的进程
    if processes_to_stop:
        print(f"找到 {len(processes_to_stop)} 个需要停止的机器人进程:")
        for pid, cmdline, cwd in processes_to_stop:
            print(f"  - PID {pid}: {cmdline}...")
            print(f"    工作目录: {cwd}")
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                    print(f"    ✓ 进程 {pid} 已正常停止")
                except psutil.TimeoutExpired:
                    print(f"    ⚠ 进程 {pid} 未响应，强制终止")
                    proc.kill()
            except Exception as e:
                print(f"    ✗ 停止进程 {pid} 时出错: {e}")
    else:
        print("没有找到需要停止的机器人进程")
        
except ImportError:
    print("psutil未安装，使用taskkill...")
    # 使用更精确的taskkill命令
    # 只停止标题包含"main.py"的python进程
    os.system('taskkill /F /FI "WINDOWTITLE eq *main.py*" /FI "IMAGENAME eq python.exe"')
    time.sleep(2)
except Exception as e:
    print(f"停止进程时出错: {e}")

# 2. 等待端口释放
print("等待端口释放...")
time.sleep(3)

# 3. 启动新进程
print("启动新的机器人进程...")
try:
    # 使用绝对路径启动main.py
    main_script = os.path.join(current_dir, 'main.py')
    if not os.path.exists(main_script):
        print(f"错误: 找不到主脚本 {main_script}")
        sys.exit(1)
    
    # 在新控制台中启动进程
    subprocess.Popen([sys.executable, main_script], 
                    cwd=current_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE)
    print("✓ 重启完成！新进程已启动。")
    print(f"  主脚本: {main_script}")
    print(f"  工作目录: {current_dir}")
    
except Exception as e:
    print(f"✗ 启动新进程时出错: {e}")
    sys.exit(1)
