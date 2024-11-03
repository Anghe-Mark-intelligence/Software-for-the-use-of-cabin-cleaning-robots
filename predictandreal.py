import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt

# 创建主窗口
root = tk.Tk()
root.title("AGV导航 - 协方差和方差计算")

# 输入框标签和输入框
tk.Label(root, text="预测状态 (x, y)").grid(row=0, column=0)
pred_x_entry = tk.Entry(root)
pred_x_entry.grid(row=0, column=1)
pred_y_entry = tk.Entry(root)
pred_y_entry.grid(row=0, column=2)

tk.Label(root, text="实际状态 (x, y)").grid(row=1, column=0)
real_x_entry = tk.Entry(root)
real_x_entry.grid(row=1, column=1)
real_y_entry = tk.Entry(root)
real_y_entry.grid(row=1, column=2)

# 计算协方差和方差的函数
def calculate():
    try:
        # 获取输入的预测状态和实际状态
        pred_x = float(pred_x_entry.get())
        pred_y = float(pred_y_entry.get())
        real_x = float(real_x_entry.get())
        real_y = float(real_y_entry.get())

        # 创建数据矩阵
        pred_state = np.array([pred_x, pred_y])
        real_state = np.array([real_x, real_y])
        data = np.array([pred_state, real_state])

        # 计算协方差矩阵
        covariance_matrix = np.cov(data.T)

        # 计算方差
        variance_pred = np.var(pred_state)
        variance_real = np.var(real_state)

        # 显示结果
        result_text = f"协方差矩阵：\n{covariance_matrix}\n"
        result_text += f"预测状态方差：{variance_pred}\n"
        result_text += f"实际状态方差：{variance_real}\n"
        messagebox.showinfo("计算结果", result_text)

        # 画图
        plt.figure(figsize=(6,6))
        plt.scatter([pred_x], [pred_y], color='red', label='预测状态')
        plt.scatter([real_x], [real_y], color='blue', label='实际状态')
        plt.quiver(pred_x, pred_y, real_x - pred_x, real_y - pred_y, angles='xy', scale_units='xy', scale=1, color='green', label='差异')
        plt.xlim(min(pred_x, real_x)-1, max(pred_x, real_x)+1)
        plt.ylim(min(pred_y, real_y)-1, max(pred_y, real_y)+1)
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("预测状态与实际状态对比")
        plt.legend()
        plt.grid(True)
        plt.show()

    except ValueError:
        messagebox.showerror("输入错误", "请输入有效的数值")

# 计算按钮
calc_button = tk.Button(root, text="计算", command=calculate)
calc_button.grid(row=2, column=1, columnspan=2)

# 运行主窗口循环
root.mainloop()
