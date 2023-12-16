import pandas as pd

fst_horizon = 24 * 7  # hour
fst_step = 12  # hour
fst_iter = fst_horizon / fst_step  # 迭代次数

startline = self.time / self.step
start_row = startline - 1
num_rows = fst_horizon / self.step

# wind = pd.read_csv("/data/wind.csv", skiprows=start_row, nrows=num_rows).value
I = pd.read_csv("/data/solar.csv", skiprows=start_row, nrows=num_rows).value  # 辐照强度
T = pd.read_csv("/data/T.csv", skiprows=start_row, nrows=num_rows).value  # 温度
Solar_azimuth = pd.read_csv("/data/Solar_azimuth.csv", skiprows=start_row, nrows=num_rows).value  # 太阳方位角
Solar_zenith = pd.read_csv("/data/Solar_zenith.csv", skiprows=start_row, nrows=num_rows).value  # 太阳天顶角
H = pd.read_csv("/data/H.csv", skiprows=start_row, nrows=num_rows).value  # 湿度
price = pd.read_csv("/data/price.csv").value  # 24小时



