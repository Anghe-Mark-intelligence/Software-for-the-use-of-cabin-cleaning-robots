# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import Scale, Label

class KalmanFilter:
    def __init__(self, A, B, H, Q, R, P, x):
        self.A = A  # 状态转移矩阵
        self.B = B  # 控制矩阵
        self.H = H  # 测量矩阵
        self.Q = Q  # 过程噪声
        self.R = R  # 测量噪声
        self.P = P  # 误差协方差矩阵
        self.x = x  # 状态估计

    def predict(self, u):
        self.x = self.A @ self.x + self.B @ u
        self.P = self.A @ self.P @ self.A.T + self.Q
        return self.x

    def update(self, z):
        y = z - self.H @ self.x  # 测量残差
        S = self.H @ self.P @ self.H.T + self.R  # 残差协方差
        K = self.P @ self.H.T @ np.linalg.inv(S)  # 卡尔曼增益
        self.x = self.x + K @ y
        self.P = (np.eye(len(self.P)) - K @ self.H) @ self.P
        return self.x

class AGVSimulator:
    def __init__(self, x0, y0, theta0, v, w):
        self.x = x0
        self.y = y0
        self.theta = theta0
        self.v = v  # 线速度
        self.w = w  # 角速度

    def move(self, dt):
        self.x += self.v * np.cos(self.theta) * dt
        self.y += self.v * np.sin(self.theta) * dt
        self.theta += self.w * dt
        return np.array([self.x, self.y, self.theta])

class AGVApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('AGV导航参数调优')

        # 卡尔曼滤波参数调优滑块
        Label(self.root, text="Q 参数").pack()
        self.q_scale = Scale(self.root, from_=0.001, to=1.0, resolution=0.001, orient='horizontal')
        self.q_scale.pack()

        Label(self.root, text="R 参数").pack()
        self.r_scale = Scale(self.root, from_=0.001, to=1.0, resolution=0.001, orient='horizontal')
        self.r_scale.pack()

        Label(self.root, text="P 参数").pack()
        self.p_scale = Scale(self.root, from_=0.001, to=1.0, resolution=0.001, orient='horizontal')
        self.p_scale.pack()

        self.fig, self.ax = plt.subplots()
        self.agv_sim = AGVSimulator(0, 0, 0, 1, 0.1)  # 初始位置和运动
        self.kalman_filter = KalmanFilter(np.eye(3), np.eye(3), np.eye(3), 0.01*np.eye(3), 0.1*np.eye(3), np.eye(3), np.array([0, 0, 0]))

        self.line, = self.ax.plot([], [], 'bo-', lw=2)

        self.ani = FuncAnimation(self.fig, self.update_plot, init_func=self.init_plot, interval=100)
        plt.show()

    def init_plot(self):
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        return self.line,

    def update_plot(self, frame):
        # 获取滑块参数
        Q_value = self.q_scale.get()
        R_value = self.r_scale.get()
        P_value = self.p_scale.get()

        # 更新卡尔曼滤波参数
        self.kalman_filter.Q = Q_value * np.eye(3)
        self.kalman_filter.R = R_value * np.eye(3)
        self.kalman_filter.P = P_value * np.eye(3)

        # AGV真实运动
        real_state = self.agv_sim.move(0.1)

        # 假设测量数据有一些噪声
        noisy_measurement = real_state + np.random.normal(0, 0.1, 3)

        # 卡尔曼滤波预测和更新
        self.kalman_filter.predict(np.zeros(3))
        estimated_state = self.kalman_filter.update(noisy_measurement)

        # 更新图像显示
        self.line.set_data([real_state[0], estimated_state[0]], [real_state[1], estimated_state[1]])
        return self.line,

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AGVApp()
    app.run()
