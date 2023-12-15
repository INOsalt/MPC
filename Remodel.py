def Remodel(I, Tpv, tend):
    """
    计算一段时间内的光伏产电量。

    参数:
    I (float): 实际辐照强度 (单位为 W/m^2)。
    Tpv (float): 光伏板实际温度 (单位为摄氏度)。
    tend (float): 积分结束时间 (单位为小时)。
    eta (float): 光伏板效率 (用小数表示)。
    P_rpv (float): 光伏电力生成设备的额定功率 (单位为 kW)。
    A (float): 光伏板面积 (单位为 m^2)。
    Tr (float): 光伏板的额定温度 (单位为摄氏度)。
    delta_p (float): 温度功率系数 (默认为 0.0047°C⁻¹)。
    Is (float): 标准辐照强度 (默认为 1000 W/m^2)。

    返回:
    float: 光伏板产生的总电能 (单位为 kWh)。
    """
    A = 10000
    delta_p = 0.0047
    Is = 1000
    Tr = 25
    eta = 0.25  # 效率
    P_r = 5  # 5 kW 额定功率
    # 计算产电量的表达式
    Qre = eta * P_r * (I / Is) * A * (1 + delta_p * (Tpv - Tr))

    # 由于所有参数均不随时间变化，直接乘以时间得到总产电量
    E = Qre * tend  # 单位为 kW*h

    return E


# 使用示例值进行计算



I_example = 800  # 800 W/m^2 实际辐照强度
Tpv_example = 30  # 30 摄氏度光伏板实际温度
tend_example = 5  # 5小时产电时间

# 计算产生的电能
energy_produced = Remodel(I_example, Tpv_example, tend_example)
print(f"光伏板产生的总电能: {energy_produced:.2f} kWh")
