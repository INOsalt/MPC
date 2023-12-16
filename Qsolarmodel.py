import numpy as np

def calculate_solar_incidence_angle(sun_zenith_angle, sun_azimuth_angle, wall_azimuth_angle):
    # 将角度从度数转换为弧度
    sun_zenith_angle_rad = np.radians(sun_zenith_angle)  # 太阳天顶角转换为弧度
    sun_azimuth_angle_rad = np.radians(sun_azimuth_angle)  # 太阳方位角转换为弧度
    wall_azimuth_angle_rad = np.radians(wall_azimuth_angle)  # 墙面方位角转换为弧度 0表示正北

    # 计算太阳的高度角（天顶角的补角）
    sun_altitude_angle_rad = np.pi / 2 - sun_zenith_angle_rad  # 太阳高度角

    # 计算太阳方位角与墙面方位角之间的差
    delta_azimuth_rad = sun_azimuth_angle_rad - wall_azimuth_angle_rad  # 方位角差

    # 将方位角差规范化到范围 [-pi, pi] 内
    delta_azimuth_rad = (delta_azimuth_rad + np.pi) % (2 * np.pi) - np.pi  # 规范化方位角差

    # 使用球面余弦定理计算入射角
    cos_theta = (np.sin(sun_altitude_angle_rad) * np.cos(wall_azimuth_angle_rad) +
                 np.cos(sun_altitude_angle_rad) * np.sin(wall_azimuth_angle_rad) * np.cos(delta_azimuth_rad))

    # 确保计算出的余弦θ在合法范围 [-1, 1] 内
    cos_theta = np.clip(cos_theta, -1, 1)  # 限制余弦θ的范围

    # 以弧度计算入射角
    theta_rad = np.arccos(cos_theta)  # 计算入射角的弧度值

    # 对于数组，使用向量化操作来生成ifback数组
    ifback = (theta_rad <= (np.pi / 2)).astype(int)  # 防止为钝角

    print("theta_rad:", theta_rad)  # 打印入射角的弧度值
    print("ifback:", ifback)  # 打印是否为背光

    return theta_rad, ifback


def Qsolarmodel(I, Solar_zenith, Solar_azimuth):
    # 墙壁信息
    wall_azimuth_angle = 0  # 墙壁方位角
    wall_area = 100  # 墙壁面积

    # 计算每个时间点的入射角和是否为背光
    theta_rad, ifback = calculate_solar_incidence_angle(Solar_zenith, Solar_azimuth, wall_azimuth_angle)

    # 计算太阳光线与墙壁法线夹角的余弦值
    cos_theta = np.cos(theta_rad)

    # 计算每个时间点的墙壁接收的太阳热量
    heat_received = I * wall_area * cos_theta * ifback
    print("cos_theta:", cos_theta)  # 打印余弦值
    print("heat_received:", heat_received)  # 打印热量接收

    return heat_received

#示例调用
I = np.array([1000, 950, 900])  # 太阳辐射强度数组，单位：W/m²
Solar_zenith = np.array([30, 45, 60])  # 太阳天顶角数组，单位：度
Solar_azimuth = np.array([0, 10, 176])  # 太阳方位角数组，单位：度

heat_received = Qsolarmodel(I, Solar_zenith, Solar_azimuth)
print("每个时间点的墙壁接收的太阳热量：", heat_received)

#示例调用1
I = np.array([1000, 950, 900])  # 太阳辐射强度数组，单位：W/m²
Solar_zenith = np.array([30, 45, 60])  # 太阳天顶角数组，单位：度
Solar_azimuth = np.array([0, 10, 0])  # 太阳方位角数组，单位：度

heat_received = Qsolarmodel(I, Solar_zenith, Solar_azimuth)
print("每个时间点的墙壁接收的太阳热量：", heat_received)







