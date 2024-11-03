# -*- coding: utf-8 -*-

import tkinter as tk
from math import sin, cos, radians

class CoordinateConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("坐标转换器")
        
        # 标签和输入框
        self.label1 = tk.Label(root, text="输入实际坐标 (X, Y, Z):")
        self.label1.grid(row=0, column=0, padx=10, pady=10)

        self.x_entry = tk.Entry(root)
        self.x_entry.grid(row=0, column=1, padx=10, pady=10)

        self.y_entry = tk.Entry(root)
        self.y_entry.grid(row=0, column=2, padx=10, pady=10)

        self.z_entry = tk.Entry(root)
        self.z_entry.grid(row=0, column=3, padx=10, pady=10)

        self.label2 = tk.Label(root, text="输入方位角（度）：")
        self.label2.grid(row=1, column=0, padx=10, pady=10)

        self.angle_entry = tk.Entry(root)
        self.angle_entry.grid(row=1, column=1, padx=10, pady=10)

        # 转换按钮
        self.convert_button = tk.Button(root, text="转换", command=self.convert_coordinates)
        self.convert_button.grid(row=2, column=1, padx=10, pady=10)

        # 结果显示
        self.result_label = tk.Label(root, text="ENU坐标 (East, North, Up):")
        self.result_label.grid(row=3, column=0, padx=10, pady=10)

        self.enu_label = tk.Label(root, text="")
        self.enu_label.grid(row=3, column=1, columnspan=3, padx=10, pady=10)

    def convert_coordinates(self):
        try:
            # 获取输入值
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            z = float(self.z_entry.get())
            angle_deg = float(self.angle_entry.get())

            # 将角度转换为弧度
            angle_rad = radians(angle_deg)

            # 计算ENU坐标 (East, North, Up)
            east = x * cos(angle_rad) - y * sin(angle_rad)
            north = x * sin(angle_rad) + y * cos(angle_rad)
            up = z  # Z坐标保持不变

            # 显示结果
            self.enu_label.config(text=f"East: {east:.2f}, North: {north:.2f}, Up: {up:.2f}")
        except ValueError:
            self.enu_label.config(text="输入无效，请检查输入的数字")

# 创建主窗口
root = tk.Tk()
app = CoordinateConverterApp(root)
root.mainloop()
