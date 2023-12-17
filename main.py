import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fcnSetStageParam import fcnSetStageParam
from solveOptimalControlProblem import solveOptimalControlProblem

from mpc_fst import mpc_fst

import fcnChoose
from PSO import Particle
#======================================
# 选择优化算法和设置参数

# fst = fcnSetStageParam('fst')
# snd = fcnSetStageParam('snd')



# 非线性MPC算法的第二步
options = fcnChoose.fcnChooseOption(1, 1e-8, fst.u0)

#========================================
class MPC:
    def __init__(self, time, step, Tin, Tout,SOC_ESS_0,Cap):  #这些是初始，来自TRNSYS
        self.time = time
        self.step = step
        self.Tin = Tin
        self.Tout = Tout
        self.SOC_ESS_0 = SOC_ESS_0
        self.Cap = Cap

        # 初始化
        fst_output_data = []
        snd_output_data = []
        fst_horizon = 24 * 7  # hour
        fst_step = 12  # hour
        fst_iter = fst_horizon / fst_step  # 迭代次数
        self.snd_horizon = fst_step  # hour
        self.snd_step = self.step  # hour
        self.snd_iter = self.snd_horizon / self.snd_step  # 迭代次数

        # 导入数据集（预测数据）


        startline = self.time / self.step
        start_row = startline - 1
        num_rows = fst_horizon / self.step

        # 创建字典并读取数据
        weather_data = {
            'I': pd.read_csv("/data/solar.csv", skiprows=start_row, nrows=num_rows).value,  # 辐照强度
            'T': pd.read_csv("/data/T.csv", skiprows=start_row, nrows=num_rows).value,  # 温度
            'Solar_azimuth': pd.read_csv("/data/Solar_azimuth.csv", skiprows=start_row, nrows=num_rows).value,  # 太阳方位角
            'Solar_zenith': pd.read_csv("/data/Solar_zenith.csv", skiprows=start_row, nrows=num_rows).value,  # 太阳天顶角
            'H': pd.read_csv("/data/H.csv", skiprows=start_row, nrows=num_rows).value,  # 湿度
        }
        # 一层的预测数据
        chunk_size = len(weather_data['I']) // fst_iter

        # 创建新的字典，其中每个键对应一个包含切分后数据的列表
        self.forcast_weather_data = {
            key: [values[i:i + chunk_size] for i in range(0, len(values), chunk_size)]
            for key, values in weather_data.items()
        }
        self.price = pd.read_csv("/data/price.csv").value  # 24小时

        self.reset()

    #=======================================
    def reset(self):

    #=============================

    def mpccal(self):
        #===第一层MPC====
        #输出 X #Tsp HVAC  Y#P TO ESS 大于0充电小于0放电 Z#P TO EV
        fst = mpc_fst(self.forcast_weather_data, self.price, self.time, self.step, self.Tin, self.Tout, self.SOC_ESS_0, self.Cap)
        Tsp_ave, SOC_ESS_end, SOC_EV_end = mpc_fst.optimize_fst()







            # 第二层初始化
            snd.pv_all = []
            snd.load_all = []
            snd.price_all = []
            snd.u0_ref = []

            if snd.flag == 0:
                snd.xmeasure = np.concatenate([fst.x_dyn[0, :], [50]])
            else:
                snd.xmeasure = np.concatenate([fst.x_dyn[0, :], [snd.xmeasure[0, 2]]])

            for i in range(1, snd.from_fst + 1):
                snd.load_all = np.concatenate([snd.load_all, np.tile(mpcdata.load[fst.mpciter + i], (snd.iter, 1))])
                snd.price_all = np.concatenate([snd.price_all, np.tile(mpcdata.price[fst.mpciter + i], (snd.iter, 1))])
                snd.u0_ref = np.concatenate([snd.u0_ref, np.tile(np.concatenate([fst.u_dyn[:, i], [0]]), (1, snd.iter))], axis=1)

            snd.u0 = snd.u0_ref[:, :snd.horizon]

            # 开始迭代：第二层
            snd.mpciter = 0
            snd.option = options
            while snd.mpciter < snd.iter:
                # 数据每5分钟变化
                snd.PV = pv_5m_data_all[snd.mpciter + 12 * fst.mpciter + 1:snd.mpciter + 12 * fst.mpciter + 13, :].T
                snd.wind = wind_5m_data_all[snd.mpciter + 12 * fst.mpciter + 1:snd.mpciter + 12 * fst.mpciter + 13, :].T

                # 数据每5分钟不变
                snd.load = snd.load_all[snd.mpciter:snd.mpciter + snd.horizon, :]
                snd.price = snd.price_all[snd.mpciter:snd.mpciter + snd.horizon, :]

                # 第二次MPC计算
                snd.f_dyn, snd.x_dyn, snd.u_dyn = snd_mpc(snd, snd_output_data)

                # 下一次迭代
                snd.u0 = shiftHorizon(snd.u_dyn)
                snd.xmeasure = snd.x_dyn[1, :]
                snd.mpciter += 1

                snd.x = np.concatenate([snd.x, snd.x_dyn[0, :].reshape(1, -1)])
                snd.u = np.concatenate([snd.u, snd.u_dyn[:, 0]])

            snd.flag = 1  # 第二层结束

            # 第一层：下一次迭代
            fst.u0 = shiftHorizon(fst.u_dyn)
            fst.xmeasure = snd.xmeasure[:2]  # 如果第二层存在，则来自第二层
            fst.mpciter += 1

            fst.f = np.concatenate([fst.f, fst.f_dyn])
            fst.x = np.concatenate([fst.x, fst.x_dyn[0, :].reshape(1, -1)])
            fst.u = np.concatenate([fst.u, fst.u_dyn[:, 0]])

    # 获取结果
    esspower = fst.u
    esssoc = fst.x
    esspower1 = fst.u_dyn
    esssoc1 = fst.x_dyn
    miwind = fst.wind
    miPV = fst.PV
    miload = fst.load

