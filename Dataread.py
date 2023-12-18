import pandas as pd
#初始化
fst_horizon = 24 * 7  # hour
fst_step = 12  # hour
fst_iter = fst_horizon / fst_step  # 迭代次数

# wind = pd.read_csv("/data/wind.csv", skiprows=start_row, nrows=num_rows).value
I_year = pd.read_csv("/data/solar.csv").value  # 辐照强度
T_year = pd.read_csv("/data/T.csv").value  # 温度
Solar_azimuth_year = pd.read_csv("/data/Solar_azimuth.csv").value  # 太阳方位角
Solar_zenith_year = pd.read_csv("/data/Solar_zenith.csv").value  # 太阳天顶角
H_year = pd.read_csv("/data/H.csv").value  # 湿度
price = pd.read_csv("/data/price.csv").value  # 24小时



