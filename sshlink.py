# -*- coding: utf-8 -*-
import paramiko
import tkinter as tk
from tkinter import messagebox, scrolledtext

# 创建主窗口
root = tk.Tk()
root.title("SSH Terminal")

# 设置窗口大小
root.geometry("500x400")

# 定义全局变量保存 SSH 客户端
ssh = None

# 定义登录逻辑
def ssh_login():
    global ssh
    ip = entry_ip.get()
    username = entry_username.get()
    password = entry_password.get()
    
    try:
        # 创建 SSH 客户端对象
        ssh = paramiko.SSHClient()
        # 自动添加主机密钥
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # 连接到远程服务器
        ssh.connect(hostname=ip, username=username, password=password)
        
        # 显示成功消息
        messagebox.showinfo("Success", "SSH Login Successful")
        
        # 显示命令输入区域
        command_frame.pack(pady=10)
    except Exception as e:
        # 显示错误消息，确保错误信息以 UTF-8 编码显示
        messagebox.showerror("Error", f"SSH Login Failed: {str(e)}")

# 定义发送命令的逻辑
def send_command():
    command = entry_command.get()
    
    try:
        # 执行命令
        stdin, stdout, stderr = ssh.exec_command(command)
        
        # 读取命令输出
        output = stdout.read().decode('utf-8')
        error_output = stderr.read().decode('utf-8')
        
        # 显示命令结果在输出框中
        if output:
            output_text.insert(tk.END, f"$ {command}\n{output}\n")
        if error_output:
            output_text.insert(tk.END, f"$ {command}\n{error_output}\n")
        
        # 清空命令输入框
        entry_command.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Error", f"Command Failed: {str(e)}")

# 创建 GUI 界面组件
label_ip = tk.Label(root, text="IP Address", font=("Arial", 10))
label_ip.pack(pady=5)
entry_ip = tk.Entry(root)
entry_ip.pack(pady=5)

label_username = tk.Label(root, text="Username", font=("Arial", 10))
label_username.pack(pady=5)
entry_username = tk.Entry(root)
entry_username.pack(pady=5)

label_password = tk.Label(root, text="Password", font=("Arial", 10))
label_password.pack(pady=5)
entry_password = tk.Entry(root, show="*")
entry_password.pack(pady=5)

# 创建登录按钮
login_button = tk.Button(root, text="Login", font=("Arial", 10), command=ssh_login)
login_button.pack(pady=20)

# 创建命令输入和输出的 frame，初始隐藏
command_frame = tk.Frame(root)

label_command = tk.Label(command_frame, text="Enter Command:", font=("Arial", 10))
label_command.pack(pady=5)
entry_command = tk.Entry(command_frame, width=40)
entry_command.pack(pady=5)

send_button = tk.Button(command_frame, text="Send", font=("Arial", 10), command=send_command)
send_button.pack(pady=5)

# 创建一个滚动文本框用于显示命令输出
output_text = scrolledtext.ScrolledText(command_frame, width=60, height=10, font=("Arial", 10))
output_text.pack(pady=10)

# 启动主循环
root.mainloop()
