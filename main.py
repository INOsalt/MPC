import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fcnSetStageParam import fcnSetStageParam
from solveOptimalControlProblem import solveOptimalControlProblem
import fcnChoose
#======================================
# 选择优化算法和设置参数
tol_opt, opt_option, iprint, printClosedloopDataFunc = fcnChooseAlgorithm(1e-8, 1, 5, printClosedloopData)

# 初始化
fst_output_data = []
snd_output_data = []
fst = fcnSetStageParam('fst')
snd = fcnSetStageParam('snd')

# 导入数据集（预测数据）
load = pd.read_csv("/data/load.csv").value
wind = pd.read_csv("/data/wind.csv").value
PV = pd.read_csv("/data/solar.csv").value
price = pd.read_csv("/data/price.csv").value

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
    def fst_mpc(fst):#第一层mpc计算-输出建议的ESS
        # 计算电力平衡
        fst.net_load = fst.load - fst.pv - fst.wind  # 和grid互动的

        # 解决最优控制问题
        fst.T_sp_ave, fst.SOC_ESS_end = solveOptimalControlProblem(fst)

        # 保存当前信息
        t = output
        x = computeOpenloopSolution(fst, fst.u0)
        u = fst.u0

        return t, x, u
        #=============================

    def mpccal(self, time):
        fst_mpciter = time
        while fst_mpciter < fst.iter: #fst.iter总时长在setpara中定义
            # 读取数据
            fst_load = load[fst_mpciter: fst_mpciter + fst.horizon]
            fst_PV = PV[fst_mpciter: fst_mpciter + fst.horizon]
            fst_wind = wind[fst_mpciter: fst_mpciter + fst.horizon]
            fst_price = price[fst_mpciter: fst_mpciter + fst.horizon]

            # 第一次MPC计算
            fst.f_dyn, fst.x_dyn, fst.u_dyn = fst_mpc(fst)

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

    # 绘制图形
    plt.figure(1)
    plt.bar(range(len(esssoc[:, 0])), esssoc[:, 0], linewidth=0.001)
    plt.xlabel('时间')
    plt.ylabel('储能功率')
    plt.twinx()
    plt.plot(esssoc[:, 1], '-g*', linewidth=1.25)
    plt.grid()
    plt.xlabel('时间')
    plt.ylabel('SOC值')
    plt.title('储能系统效果对比')
    plt.legend(['储能功率', 'SOC值'])

    plt.figure(2)
    plt.plot(esspower[:, 0], '-r*', linewidth=1.25)
    plt.grid()
    plt.xlabel('时间')
    plt.ylabel('发电功率')

    plt.figure(3)
    plt.plot(esspower[:, 1], '-r*', linewidth=1.25)
    plt.grid()
    plt.xlabel('时间')
    plt.ylabel('电池功率')

    plt.figure(4)
    plt.plot(miload, '-g*', linewidth=1.15)
    plt.plot(miPV, '-r*', linewidth=1.15)
    plt.plot(miwind, '-y*', linewidth=1.15)
    plt.xlabel('时间')
    plt.ylabel('功率/MW')
    plt.title('负荷、光伏、风力')
    plt.legend(['负荷', '
