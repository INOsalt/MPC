import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fcnSetStageParam import fcnSetStageParam
from solveOptimalControlProblem import solveOptimalControlProblem

import fcnChoose
from Remodel import Remodel
from HAVCmodel import HAVCmodel
#======================================
# 选择优化算法和设置参数

# fst = fcnSetStageParam('fst')
# snd = fcnSetStageParam('snd')



# 非线性MPC算法的第二步
options = fcnChoose.fcnChooseOption(1, 1e-8, fst.u0)

#========================================
class MPC:
    def __init__(self, T_room, SOC_ESS_0):  #

        self.reset()
    # 开始迭代：第一层
    #=======================================
    def reset(self):
        self.
        #=============================

    def mpccal(self, time, step):
        # 初始化
        fst_output_data = []
        snd_output_data = []
        fst_horizon = 24 * 7  # hour
        fst_step = 24  # hour
        fst_iter = fst_horizon / fst_step  # 迭代次数
        snd_horizon = 24  # hour
        snd_step = step  # hour
        snd_iter = snd_horizon / snd_step  # 迭代次数

        # 导入数据集（预测数据）
        startline =  time/step
        start_row = startline - 1
        num_rows = fst_horizon/step

        # wind = pd.read_csv("/data/wind.csv", skiprows=start_row, nrows=num_rows).value
        I = pd.read_csv("/data/solar.csv", skiprows=start_row, nrows=num_rows).value #辐照强度
        T = pd.read_csv("/data/T.csv", skiprows=start_row, nrows=num_rows).value  # 温度
        H = pd.read_csv("/data/H.csv", skiprows=start_row, nrows=num_rows).value  # 湿度
        price = pd.read_csv("/data/price.csv").value #24小时

        #===第一层MPC====

        fst_mpciter = time

        while fst_mpciter < fst_iter: #fst_iter迭代次数
            I_fst_step = I[fst_mpciter:fst_mpciter + fst_step]
            T_fst_step = T[fst_mpciter:fst_mpciter + fst_step]
            H_fst_step = H[fst_mpciter:fst_mpciter + fst_step]
            # 第一次MPC计算
            Q_re = Remodel(I_fst_step, T_fst_step, step) #新能源发电
            Q_HAVC = HAVCmodel(T_fst_step, H_fst_step, Q_solar, Q_lighting, Q_equipment, Q_internal)

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

