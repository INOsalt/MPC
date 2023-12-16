import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# 初始温度（单位：K）
Tout_initial = 300.0  # 室外初始温度
Tin_initial = 295.0  # 室内初始温度

# 固定热流（单位：W）
Qsolar = 500.0  # 太阳辐射热流
Qinter = 200.0  # 内部热流

# 时间范围为0到t，这里假设t为24小时，转换为秒
t_end = 24 * 3600
time_points = np.linspace(0, t_end, 1000)  # 生成1000个时间点


# 方程组
def thermal_model(Y, t, Tout, Qsolar, Qinter): #RC model
    # 热阻值（单位：K/W）
    R_ex = 2.0  # 外部热阻
    R_win = 1.5  # 窗户热阻
    R_wi = 0.5  # 内墙热阻
    R_ew = 1.0  # 外墙热阻

    # 热容值（单位：J/K）
    C_w1 = 10e3  # 墙体1热容
    C_w2 = 15e3  # 墙体2热容
    C_im = 20e3  # 内部质量热容

    T_ex, T_win, T_im, T_i = Y

    dT_ex_dt = (Tout - T_ex) / (R_ex * C_w1) + (T_win - T_ex) / (R_win * C_w1)
    dT_win_dt = (T_ex - T_win) / (R_win * C_w2) + (T_i - T_win) / (R_wi * C_w2) + Qsolar / C_w2
    dT_im_dt = (T_i - T_im) / (R_ew * C_im) + Qinter / C_im
    dT_i_dt = (T_im - T_i) / (R_ew * C_w1) + (Tout - T_i) / (R_ex * C_w1) + Qinter / C_w1

    return [dT_ex_dt, dT_win_dt, dT_im_dt, dT_i_dt]

def HVACmodel(initial_conditions, t, Tout, Qsolar, Qinter): #RC model
    # 初始状态
    initial_conditions = [Tout_initial, Tout_initial, Tin_initial, Tin_initial]

    # 解方程组
    solution = odeint(thermal_model, initial_conditions, time_points,
                      args=(Tout_initial, Qsolar, Qinter))

    # 解包解决方案
    T_ex_solution, T_win_solution, T_im_solution, T_i_solution = solution.T

    # 计算Qchiller
    # 根据室内温度和室内外温差计算冷却器的热流量（这里假设冷却器的热阻为1 K/W）
    Qchiller_solution = (T_i_solution - Tout_initial)  # 这里简化了计算，实际情况可能更复杂

# 绘制结果
plt.figure(figsize=(12, 6))
plt.plot(time_points / 3600, T_ex_solution, label='T_ex (Exterior)')
plt.plot(time_points / 3600, T_win_solution, label='T_win (Window)')
plt.plot(time_points / 3600, T_im_solution, label='T_im (Internal Mass)')
plt.plot(time_points / 3600, T_i_solution, label='T_i (Interior)')
plt.legend()
plt.xlabel('Time (hours)')
plt.ylabel('Temperature (K)')
plt.title('Temperature Evolution in the RC Grey-Box Model')
plt.grid(True)
plt.show()

# 输出最终计算的Qchiller值
Qchiller_final = Qchiller_solution[-1]  # 取
