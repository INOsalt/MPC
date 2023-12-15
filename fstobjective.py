import numpy as np
from Remodel import Remodel

def fstobjective(X, Y, Z, t): #X Tsp Y QtoEV Z Qto ESS

    # 计算新能源产电量
    Qre = Remodel(I, Tpv, )

    # 计算能源需求（HVAC 和照明）
    Qdemand = HVACmodel(Y, t) + lightmodel(Z, t)

    # 计算成本（假设示例：成本与需求量成正比，减去新能源产量）
    Cost = Qdemand - Qre

    # 计算能源消耗效率（假设示例：ECE 与需求和产量的比率成反比）
    ECE = Qre / Qdemand if Qdemand != 0 else float('inf')

    return Cost, ECE

# 使用示例
X_example = np.array([1, 2, 3])  # 示例参数数组 X
Y_example = np.array([2, 3, 4])  # 示例参数数组 Y
Z_example = np.array([3, 4, 5])  # 示例参数数组 Z
t_example = 1  # 示例时间

cost, ece = fstobjective(X_example, Y_example, Z_example, t_example)
print("Cost:", cost)
print("ECE:", ece)
