def Remodel(I, Tpv, step):
    """
    计算一段时间内的光伏产电量总和。

    参数:
    I (list of float): 实际辐照强度数组 (单位为 W/m^2)。
    Tpv (list of float): 光伏板实际温度数组 (单位为摄氏度)。
    tend (float): 积分结束时间 (单位为小时)。

    返回:
    float: 光伏板产生的总电能 (单位为 kWh)。
    """
    A = 10000
    delta_p = 0.0047
    Is = 1000
    Tr = 25
    eta = 0.25  # 效率
    P_r = 5  # 5 kW 额定功率

    E_SUM = 0
    for i, tpv in zip(I, Tpv):
        # 计算每个元素对应的产电量
        Qre = eta * P_r * (i / Is) * A * (1 + delta_p * (tpv - Tr))
        E = Qre * step
        E_SUM += E  # 将计算出的电能加总

    return E_SUM
