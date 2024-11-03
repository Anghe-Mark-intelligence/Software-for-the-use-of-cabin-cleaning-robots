# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk
import subprocess
import heapq
import time

# 机器人默认状态
robot_status = {'电量': 80, '状态': '开'}

# 用于存储路径点和障碍物信息
path_points = []
obstacles = set()  # 障碍物集合

# A* 算法的节点类
class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # 起点到当前节点的代价
        self.h = 0  # 当前节点到终点的估计代价
        self.f = 0  # f = g + h

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f < other.f

# A*算法
def astar(start, end, grid):
    start_node = Node(start)
    end_node = Node(end)

    open_list = []
    closed_list = set()

    heapq.heappush(open_list, start_node)

    while open_list:
        current_node = heapq.heappop(open_list)
        closed_list.add(current_node.position)

        # 找到目标点
        if current_node == end_node:
            path = []
            while current_node is not None:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]  # 返回反向路径

        # 生成邻居节点
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # 上下左右
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # 确保新的位置在网格范围内
            if node_position[0] < 0 or node_position[0] >= len(grid) or node_position[1] < 0 or node_position[1] >= len(grid[0]):
                continue

            # 确保不是障碍物
            if grid[node_position[0]][node_position[1]] != 0:
                continue

            new_node = Node(node_position, current_node)

            if new_node.position in closed_list:
                continue

            new_node.g = current_node.g + 1
            new_node.h = abs(new_node.position[0] - end_node.position[0]) + abs(new_node.position[1] - end_node.position[1])
            new_node.f = new_node.g + new_node.h

            # 如果新节点在 open_list 中，且当前 f 值大于已存在的 f 值，则跳过
            if any(open_node.position == new_node.position and open_node.f <= new_node.f for open_node in open_list):
                continue

            heapq.heappush(open_list, new_node)

    return None  # 无路径

# 创建并显示每个路径点的速度和期望坐标
def add_path_point():
    point_num = point_number_entry.get()
    
    try:
        point_num = int(point_num)
        if point_num <= 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("输入错误", "请输入有效的路径点数量")
        return
    
    # 创建新窗口输入每个路径点的速度和期望坐标
    point_window = tk.Toplevel(root)
    point_window.title(f"输入路径点信息 (共{point_num}个点)")
    
    entries = []
    for i in range(point_num):
        tk.Label(point_window, text=f"路径点 {i+1}:").grid(row=i, column=0)
        
        tk.Label(point_window, text="X坐标:").grid(row=i, column=1)
        x_coord_entry = tk.Entry(point_window)
        x_coord_entry.grid(row=i, column=2)
        
        tk.Label(point_window, text="Y坐标:").grid(row=i, column=3)
        y_coord_entry = tk.Entry(point_window)
        y_coord_entry.grid(row=i, column=4)
        
        entries.append((x_coord_entry, y_coord_entry))
    
    def save_points():
        global path_points
        path_points.clear()
        for i, entry_tuple in enumerate(entries):
            try:
                x_coord = int(entry_tuple[0].get())
                y_coord = int(entry_tuple[1].get())
                path_points.append((x_coord, y_coord))
            except ValueError:
                messagebox.showwarning("输入错误", f"路径点 {i+1} 的数据无效，请输入有效的数值")
                return
        messagebox.showinfo("路径规划", f"共{len(path_points)}个路径点已成功添加")
        point_window.destroy()
    
    save_button = tk.Button(point_window, text="保存", command=save_points)
    save_button.grid(row=point_num, columnspan=5, pady=10)

# 添加障碍物功能
def add_obstacle_mode():
    messagebox.showinfo("添加障碍物", "点击画布来添加障碍物（红色方块）")
    canvas.bind("<Button-1>", add_obstacle)

# 在画布中添加障碍物
def add_obstacle(event):
    grid_x = event.x // 5  # 将点击的像素坐标转换为网格坐标
    grid_y = event.y // 5
    obstacles.add((grid_x, grid_y))  # 将障碍物加入集合
    canvas.create_rectangle(grid_x * 5, grid_y * 5, grid_x * 5 + 5, grid_y * 5 + 5, fill="red", outline="black")

# 规划路径并显示结果
def plan_path():
    if len(path_points) < 2:
        messagebox.showwarning("路径规划", "请先输入至少两个路径点")
        return
    
    # 清空输出框中的内容
    output_text.delete(1.0, tk.END)
    
    # 创建 100x100 的网格，0 表示可以通过，1 表示障碍物
    grid = [[0 for _ in range(100)] for _ in range(100)]
    
    # 设置障碍物
    for (x, y) in obstacles:
        grid[x][y] = 1
    
    total_path = []
    for i in range(len(path_points) - 1):
        start = path_points[i]
        end = path_points[i + 1]
        path = astar(start, end, grid)
        if path is None:
            messagebox.showerror("错误", f"无法从 {start} 到 {end} 规划路径")
            return
        total_path.extend(path)
    
    # 动态展示机器人路径
    canvas.delete("all")  # 清空之前的内容
    
    # 先绘制障碍物为红色
    for (x, y) in obstacles:
        canvas.create_rectangle(x*5, y*5, x*5 + 5, y*5 + 5, fill="red", outline="black")  # 障碍物为红色
    
    # 先绘制路径点为黄色
    for (x, y) in path_points:
        canvas.create_rectangle(x*5, y*5, x*5 + 5, y*5 + 5, fill="yellow", outline="black")  # 路径点为黄色
    
    # 然后绘制路径为蓝色，并在实时输出路径坐标
    for (x, y) in total_path:
        # 绘制蓝色路径
        canvas.create_rectangle(x*5, y*5, x*5 + 5, y*5 + 5, fill="blue", outline="white")
        canvas.update()
        
        # 输出坐标到文本框
        output_text.insert(tk.END, f"路径坐标: ({x}, {y})\n")
        output_text.see(tk.END)  # 自动滚动到最新行
        
        time.sleep(0.01)  # 模拟机器人行进的延迟
    
    messagebox.showinfo("路径规划完成", "机器人已成功规划并展示路径")

# 打开 enu（站心）转换器
def open_translate_enu():
    try:
        subprocess.Popen(["python", r"D:\anaconda\robotsystemheang\translateenu.py"])
    except Exception as e:
        messagebox.showerror("错误", f"无法打开 enu 转换器: {str(e)}")

# 打开 ssh 远程功能
def open_ssh_remote():
    try:
        subprocess.Popen(["python", r"D:\anaconda\robotsystemheang\sshlink.py"])
    except Exception as e:
        messagebox.showerror("错误", f"无法执行 SSH 远程功能: {str(e)}")

def open_predictandreal():
    try:
        subprocess.Popen(["python", r"D:\anaconda\robotsystemheang\predictandreal.py"])
    except Exception as e:
        messagebox.showerror("错误", f"无法执行预测和实际对比功能: {str(e)}")
        
# 创建主窗口
root = tk.Tk()
root.title("智航--船舶清舱机器人路径规划系统")
root.geometry("1000x700")  # 调整主窗口大小

# 背景颜色设置
root.configure(bg="#f2f2f2")

# 设置窗口图标
try:
    icon_img = Image.open(r"D:\anaconda\robotsystemheang\softwarelogo.jpg")
    icon_img_tk = ImageTk.PhotoImage(icon_img)
    root.iconphoto(True, icon_img_tk)
except Exception as e:
    messagebox.showerror("图标加载失败", f"无法加载图标: {str(e)}")

# 图片加载与展示
image_frame = tk.Frame(root, bg="#f2f2f2")  # 用于放置图片和文字的框架
image_frame.pack(side="left", padx=20, pady=20)

try:
    img = Image.open(r"D:\anaconda\robotsystemheang\robotimage.jpg")
    img = img.resize((250, 250))  # 调整图片大小
    img_tk = ImageTk.PhotoImage(img)
    image_label = tk.Label(image_frame, image=img_tk, bg="#f2f2f2")
    image_label.pack(pady=5)
    
    # 添加图片下方的说明文字
    caption_label = tk.Label(image_frame, text="清舱机器人", font=("Arial", 14, "bold"), bg="#f2f2f2")
    caption_label.pack(pady=5)
except Exception as e:
    messagebox.showerror("图片加载失败", f"无法加载图片: {str(e)}")

# 创建上方按钮容器
button_frame = tk.Frame(root, bg="#f2f2f2")
button_frame.pack(side="top", fill="x", padx=20, pady=10)

# 输入路径点数量
tk.Label(button_frame, text="输入路径点数量:", font=("Arial", 12), bg="#f2f2f2").pack(side="left", padx=5)
point_number_entry = tk.Entry(button_frame, width=10)
point_number_entry.pack(side="left", padx=5)

# 添加路径点按钮
add_point_button = tk.Button(button_frame, text="输入路径点", command=add_path_point, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
add_point_button.pack(side="left", padx=10)

# 添加障碍物按钮
add_obstacle_button = tk.Button(button_frame, text="添加障碍物", command=add_obstacle_mode, bg="#e74c3c", fg="white", font=("Arial", 12, "bold"))
add_obstacle_button.pack(side="left", padx=10)

# 规划路径按钮
plan_button = tk.Button(button_frame, text="规划路径", command=plan_path, bg="#008CBA", fg="white", font=("Arial", 12, "bold"))
plan_button.pack(side="left", padx=10)

# 添加 enu（站心）转换器按钮
translate_enu_button = tk.Button(button_frame, text="enu（站心）转换器", command=open_translate_enu, bg="#f39c12", fg="white", font=("Arial", 12, "bold"))
translate_enu_button.pack(side="left", padx=10)

# 添加 ssh 远程功能按钮
ssh_button = tk.Button(button_frame, text="ssh远程功能", command=open_ssh_remote, bg="#e74c3c", fg="white", font=("Arial", 12, "bold"))
ssh_button.pack(side="left", padx=10)

# 添加记录与对比模式按钮
predict_button = tk.Button(button_frame, text="记录与对比模式", command=open_predictandreal, bg="#9b59b6", fg="white", font=("Arial", 12, "bold"))
predict_button.pack(side="left", padx=10)

# 在中间添加文本框用于实时输出坐标
output_frame = tk.Frame(root, bg="#f2f2f2")
output_frame.pack(side="left", fill="y", padx=20, pady=10)

output_label = tk.Label(output_frame, text="路径规划坐标输出", font=("Arial", 14, "bold"), bg="#f2f2f2")
output_label.pack()

output_text = scrolledtext.ScrolledText(output_frame, width=30, height=20, font=("Arial", 12), bg="white", wrap=tk.WORD)
output_text.pack()

# 创建画布用于展示路径，调整为适应 100x100 个 5x5 大小的方格
canvas_frame = tk.Frame(root, bg="#f2f2f2")
canvas_frame.pack(side="right", padx=20, pady=20)

canvas_label = tk.Label(canvas_frame, text="路径展示", font=("Arial", 14, "bold"), bg="#f2f2f2")
canvas_label.pack()

canvas = tk.Canvas(canvas_frame, width=500, height=500, bg="white", bd=2, relief="sunken")
canvas.pack(pady=10)

# 创建底部的版权标志和团队 logo
bottom_frame = tk.Frame(root, bg="#f2f2f2")
bottom_frame.pack(side="bottom", fill="x", pady=20)

# 版权标志文本
copyright_label = tk.Label(bottom_frame, text="MADE BY MARKTEAM-heang、huanghongwei，et.al", font=("Arial", 10), bg="#f2f2f2")
copyright_label.pack(side="left")

# 团队 logo 图片
try:
    team_logo_img = Image.open(r"D:\anaconda\robotsystemheang\teamlogo.jpg")
    team_logo_img = team_logo_img.resize((60, 35))  # 调整图片大小
    team_logo_img_tk = ImageTk.PhotoImage(team_logo_img)
    team_logo_label = tk.Label(bottom_frame, image=team_logo_img_tk, bg="#f2f2f2")
    team_logo_label.pack(side="right", padx=10)
except Exception as e:
    messagebox.showerror("图片加载失败", f"无法加载团队 logo 图片: {str(e)}")

# 运行主循环
root.mainloop()
