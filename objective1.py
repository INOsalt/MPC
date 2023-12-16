import numpy as np
import copy
import matplotlib.pyplot as plt
import time
import pandas as pd
import os
from tqdm import tqdm
import math

from EVstate import Gamma_list
from EVstate import soc_ev_clr_list
from EVstate import fsoc_ev_0_list
from EVstate import fsoc_ev_final_list

from EVstate import print_time

from EVstate import TIMEALL
from EVstate import LOAD
from EVstate import P_PV_MODULE
from EVstate import P_BIPV
from EVstate import BUY_PRICE
from EVstate import SELL_PRICE
from EVstate import T
from EVstate import HOURS_DAY
from EVstate import P_WT_ONE

from Parameter import SIMULATION_PROGRESS_BAR

# ================================================================================================================================ #

# 初始数据
EFF_PV = 0.5  # PV效率
EFF_ESS = 0.9  # 电池效率
EFF_EV = 0.9  # EV效率

# v_cutin = 3
# v_r = 10
# v_cutout = 15
# P_WT_r = 500 #kW 风速vr时风机功率
# k_WT = 2 #风切变指数

from EVstate import EV_NUM

SOC_EV_CAP = 60  # kWh
SOC_ESS_CAP = 1  # kWh 1wh1元
PRICE_ESS = 800  # 元
PRICE_PV = 500  # 元 0.95/w
PRICE_WT = 18600000 #3000/kw
PRICE_REPLACE = 0.8  # 百分比


# ================================================================================================================================ #

class Cost:
    # 初始化
    def __init__(self, x, y, z):  # x PV个数 y ESS数 z wt数
        self.x = x
        self.y = y
        self.z = z

        self.p_pv = (P_PV_MODULE * self.x) / 1000
        self.p_wt = (P_WT_ONE * self.z)

        # self.P_PV = EFF_PV * x * np.array(I)  # Kw list
        # P_WT = []
        # for v_t in V:
        #     if v_t < v_cutin or v_t > v_cutout:
        #         P_WT.append(0)
        #     elif v_cutin <= v_t < v_r:
        #         P_WT.append(P_WT_r * ((v_t**k_WT - v_cutin**k_WT)/(v_r**k_WT - v_cutin**k_WT)))
        #     else:
        #         P_WT.append(P_WT_r)
        # P_WT = y * np.array(P_WT)  # Kwh list
        self.month_day = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        self.reset()

    # 重置每次计算的临时变量
    def reset(self):
        self.soc_ev = [0] * EV_NUM
        self.soc_ev_pre = [0] * EV_NUM
        self.charge_ev_loss = 0
        self.discharge_ev_loss = 0

        self.soc_ess = 0
        self.charge_ess_loss = 0
        self.discharge_ess_loss = 0

        self.soc_ev_depature = [0] * EV_NUM
        self.charge_ev_final = [0] * EV_NUM
        self.Shortage = []
        self.Surplus = []
        self.EV_Soctime = []
        self.ESS_Soctime = []
        self.EV_charge = []
        self.EV_Finalsoc = []
        for i in range(EV_NUM):
            self.EV_charge.append([])
            self.EV_Finalsoc.append([])

    ############################################################################

    # 按月份取天数
    def get_month_start_end(self, month):
        start = sum(self.month_day[0: month])
        end = start + self.month_day[month]
        return start, end - 1

    # 定义电费计算函数
    def calculate_monthly_cost(self, month, monthly_consumption):
        final_monthly_consumption = 0
        if 5 <= month <= 10:
            if monthly_consumption > 600:
                final_monthly_consumption += (monthly_consumption - 600) * 0.3
                monthly_consumption = 600
            if monthly_consumption > 260:
                final_monthly_consumption += (monthly_consumption - 260) * 0.05
        else:
            if monthly_consumption > 400:
                final_monthly_consumption += (monthly_consumption - 400) * 0.3
                monthly_consumption = 400
            if monthly_consumption > 200:
                final_monthly_consumption += (monthly_consumption - 200) * 0.05
        return final_monthly_consumption

    # def cal_CFR(self, inflation_rate, years):

    ############################################################################

    # 充电
    def get_surplus(self, k, total, load):
        surplus = total - load
        if surplus <= 0:
            return 0, 0
        surplus_noenough = 0
        # EV充电
        for i in range(EV_NUM):
            # EVstate里的函数
            Gamma = Gamma_list[i][k]
            soc_ev_clr = soc_ev_clr_list[i][k]
            fsoc_ev_0 = fsoc_ev_0_list[i][k]
            fsoc_ev_final = fsoc_ev_final_list[i][k]
            # 上一时刻soc
            if k == 0:
                self.soc_ev_pre = self.soc_ev_pre
            else:
                self.soc_ev_pre = self.EV_Soctime[k - 1]
            soc_ev_0 = fsoc_ev_0 * SOC_EV_CAP + self.soc_ev_pre[i]
            # 最多能充
            charge_ev_temp = max(0, Gamma * (SOC_EV_CAP * 0.95 - soc_ev_0))  # 能容纳的
            if math.isclose(fsoc_ev_final, 0, abs_tol=1e-5):
                if (surplus * EFF_EV) < charge_ev_temp:
                    charge_ev_temp = max(0, surplus) * EFF_EV
                    surplus = 0
                    surplus_noenough += min(surplus, 0)
                else:
                    surplus -= charge_ev_temp / EFF_EV
                self.soc_ev_depature[i] = 0
                self.charge_ev_final[i] = 0
            else:  # ev离开
                if soc_ev_0 >= fsoc_ev_final * SOC_EV_CAP:
                    charge_ev_temp = 0
                else:
                    charge_ev_temp = fsoc_ev_final * SOC_EV_CAP - soc_ev_0
                    surplus -= charge_ev_temp / EFF_EV
                self.soc_ev_depature[i] = soc_ev_0 + charge_ev_temp
                self.charge_ev_final[i] = self.soc_ev_depature[i] - fsoc_ev_final * SOC_EV_CAP

            # 更新soc
            self.soc_ev[i] = (soc_ev_0 + charge_ev_temp) * soc_ev_clr  # soc记录到list
            self.charge_ev_loss += abs(charge_ev_temp * (1 - EFF_EV))

        # ESS充电
        charge_ess_temp = max(0, SOC_ESS_CAP * self.y * 0.95 - self.soc_ess)  # 最多能充
        if (k % 24) != 7:
            if surplus < 0:
                surplus_noenough += surplus
                return 0, surplus_noenough
            # 充电surplus
            if surplus < (charge_ess_temp / EFF_ESS):
                charge_ess_temp = surplus * EFF_ESS
                surplus = 0
            else:
                surplus -= charge_ess_temp / EFF_ESS
        else:
            surplus -= charge_ess_temp / EFF_ESS  # 电价bug
        if surplus < 0:
            surplus_noenough += surplus
            return 0, surplus_noenough

        self.soc_ess += charge_ess_temp  # 更新soc
        self.charge_ess_loss += abs(charge_ess_temp * (1 - EFF_ESS))
        return surplus, 0

    # 放电
    def get_shortage(self, k, total, load,
                     surplus_noenough):  # 如果有surplus_noenough传入，说明此时shortage < 0 surplus_noenough<=0
        shortage = load - total
        if shortage < 0 and math.isclose(surplus_noenough, 0, abs_tol=1e-5):  # surplus且surplus足够
            return 0

        if (k % 24) > 7:
            # ESS放电 谷期不放电
            discharge_ess_temp = max(0, self.soc_ess - SOC_ESS_CAP * self.y * 0.1)  # 最多能放
            # 放电供给shortage
            if (max(0, shortage) - surplus_noenough) < discharge_ess_temp * EFF_ESS:
                discharge_ess_temp = (max(0, shortage) - surplus_noenough) / EFF_ESS
                shortage = 0
            else:
                shortage = shortage - min(0, shortage) - discharge_ess_temp * EFF_ESS - surplus_noenough
        elif (k % 24) == 7:
            discharge_ess_temp = (min(0, self.soc_ess - SOC_ESS_CAP * self.y * 0.95))  # 充满电,此时为负
            shortage = - surplus_noenough  # 充电,surplusenough<0 = 缺电
        else:
            discharge_ess_temp = 0
            # 更新soc
        self.soc_ess -= discharge_ess_temp
        self.discharge_ess_loss += abs(discharge_ess_temp * (1 - EFF_ESS))
        if not math.isclose(surplus_noenough, 0, abs_tol=1e-5):
            return shortage
        # EV放电
        for i in range(EV_NUM):
            # EVstate里的函数
            Gamma = Gamma_list[i][k]
            soc_ev_clr = soc_ev_clr_list[i][k]
            fsoc_ev_0 = fsoc_ev_0_list[i][k]
            fsoc_ev_final = fsoc_ev_final_list[i][k]
            # 上一时刻soc
            if k == 0:
                self.soc_ev_pre = self.soc_ev_pre
            else:
                self.soc_ev_pre = self.EV_Soctime[k - 1]
            soc_ev_0 = fsoc_ev_0 * SOC_EV_CAP + self.soc_ev_pre[i]
            # 最多能放
            discharge_ev_temp = max(0, Gamma * (soc_ev_0 - SOC_EV_CAP * 0.3))
            if math.isclose(fsoc_ev_final, 0, abs_tol=1e-5):
                # 放电供给shortage
                if shortage < discharge_ev_temp * EFF_EV:
                    discharge_ev_temp = shortage / EFF_EV
                    shortage = 0
                else:
                    shortage -= discharge_ev_temp * EFF_EV
                self.soc_ev_depature[i] = 0
                self.charge_ev_final[i] = 0
            else:  # ev离开
                if soc_ev_0 >= fsoc_ev_final * SOC_EV_CAP:
                    discharge_ev_temp = 0
                else:
                    discharge_ev_temp = min(0, (
                                soc_ev_0 - fsoc_ev_final * SOC_EV_CAP))  # 实际上是充电，为了保持变量一致为discharge,此时这里是负数
                    shortage -= discharge_ev_temp / EFF_EV
                self.soc_ev_depature[i] = soc_ev_0 - discharge_ev_temp
                self.charge_ev_final[i] = self.soc_ev_depature[i] - (
                            fsoc_ev_final * SOC_EV_CAP)  # fsoc0更新过 fsoc_ev_final * SOC_EV_CAP=初始
            # 更新soc
            self.soc_ev[i] = (soc_ev_0 - discharge_ev_temp) * soc_ev_clr  # soc记录到list
            self.discharge_ev_loss += abs(discharge_ev_temp * (1 - EFF_EV))
        return shortage

    ############################################################################

    def get_cost(self, df=None):
        self.reset()

        simulation_progress_bar = tqdm(total=T, desc="Running simulation", unit="time step")
        for k in range(T):
            total = self.p_pv[k] + P_BIPV[k] + self.p_wt[k]
            load = LOAD[k]

            surplus, surplus_noenough = self.get_surplus(k, total, load)
            shortage = self.get_shortage(k, total, load, surplus_noenough)

            # 累计k时刻的数据
            self.Shortage.append(shortage)
            self.Surplus.append(surplus)
            self.EV_Soctime.append(copy.deepcopy(self.soc_ev))
            self.ESS_Soctime.append(copy.deepcopy(self.soc_ess))

            for i in range(EV_NUM):
                if not math.isclose(self.soc_ev_depature[i], -1, abs_tol=1e-5):
                    self.EV_charge[i].append(self.charge_ev_final[i])
                if not math.isclose(self.charge_ev_final[i], -1, abs_tol=1e-5):
                    self.EV_Finalsoc[i].append(self.soc_ev_depature[i])

            # 更新UI
            if SIMULATION_PROGRESS_BAR == 0:
                simulation_progress_bar.update(1)
        if SIMULATION_PROGRESS_BAR != 0:
            simulation_progress_bar.update(T)
        simulation_progress_bar.close()

        P_imp = np.array(self.Shortage)
        reshaped_P_imp = P_imp.reshape(-1, HOURS_DAY)
        Price_imp = np.array(BUY_PRICE)
        P_exp = np.array(self.Surplus)
        reshaped_P_exp = P_exp.reshape(-1, HOURS_DAY)
        Price_exp = np.array(BUY_PRICE)
        ESS_FSoctime = np.array(self.ESS_Soctime) * 100 / (SOC_ESS_CAP * self.y)
        EV_FSoctime = [np.array(arr) / SOC_EV_CAP for arr in self.EV_Soctime]
        time_column = list(range(1, len(P_imp) + 1))

        #======energy balance if P_pv + Pimp - Pexp - Σ(SOC_departure-SOC_arrive) - load= 0?

        Qin = np.sum(self.p_pv) + np.sum(P_imp) + np.sum(P_BIPV) + np.sum(self.p_wt)
        Qout = np.sum(P_exp) + np.sum(LOAD) + np.sum(self.EV_charge)
        LOSS = self.charge_ess_loss + self.discharge_ess_loss + self.charge_ev_loss + self.discharge_ev_loss
        check = Qin - Qout - LOSS
        print(self.x)
        print(self.y)
        print(self.z)
        print(check / Qin)
        print(check / Qout)

        #==== # cost
        # 使用 NumPy 的点乘函数计算每行和 price 的点乘，然后对所有行求和
        cost_imp_sum = np.sum(reshaped_P_imp * Price_imp, axis=1).sum()  # 分时电价
        cost_exp_sum = np.sum(reshaped_P_exp * Price_exp, axis=1).sum()
        # 计算每个月的
        yearly_consumption = P_imp

        # 遍历12个月的电力消耗
        cost_imp_ex = 0
        for index in range(12):
            month = index + 1
            # 获取当前月的电力消耗数据
            start, end = self.get_month_start_end(month)
            monthly_consumption = sum(yearly_consumption[start * HOURS_DAY: end * HOURS_DAY])
            # 计算当前月的电费并累加到总电费
            cost_imp_ex += self.calculate_monthly_cost(month, monthly_consumption)

        year = 20
        cost_ini_PV = self.x * PRICE_PV
        cost_om_PV = cost_ini_PV * 0.05 * year
        lcc_PV = cost_ini_PV * (1 + 0.1) ** year + cost_om_PV
        cost_ini_WT = self.z * PRICE_WT
        cost_om_WT = cost_ini_WT * 0.05 * year
        lcc_WT = cost_ini_WT * (1 + 0.1) ** year + cost_om_WT
        cost_ini_ess = self.y * SOC_ESS_CAP * PRICE_ESS
        cost_om_ess = cost_ini_ess * 0.05 * year
        lcc_ess = cost_ini_ess * (1 + 0.1) ** year + cost_om_ess
        cost_rep = PRICE_REPLACE * cost_ini_ess
        cost = (cost_imp_sum + cost_imp_ex - cost_exp_sum) * year + lcc_PV + lcc_ess + lcc_WT + cost_rep

        # ================================================================================================================================ #
        # data = pd.DataFrame({'Time': time_column,
        #     'P_imp': P_imp,
        #     'P_exp': P_exp,
        #     'ESS_FSoctime': ESS_FSoctime
        # })
        # data.to_excel('ESS_var/data_energyWT1.xlsx', index=False)
        # #
        # # EV输出数据到Excel文件
        # # ev charge
        # data_ev = {'Time': range(1, len(self.EV_charge[0]) + 1)}
        # for i in range(EV_NUM):
        #     data_ev[f'EV_charge_{i + 1}'] = self.EV_charge[i]
        # df_ev = pd.DataFrame(data_ev)
        # # 输出数据到 Excel 文件
        # df_ev.to_excel('data_ev_chargeWT1.xlsx', index=False)
        # #
        # # 每时刻FSOC
        # # 其中每个数组代表一个 EV 的 FSoctime 数据
        # df_ev_fsoc = pd.DataFrame(EV_FSoctime)
        # # 输出数据到 Excel 文件
        # df_ev_fsoc.to_excel('data_ev_fsocWT1.xlsx', index=False)
        #
        # #grid 图
        # x_axis = range(1, 8761)  # 从1到8760
        # plt.plot(x_axis, P_imp, label='P_imp')
        # plt.plot(x_axis, P_exp, label='P_exp')
        # # 添加标签和标题
        # plt.xlabel('Time/h')
        # plt.ylabel('Power/kWh')
        # plt.title('P_imp and P_exp ')
        # # 显示图例
        # plt.legend()
        # plt.show()
        # # #
        # # ESS图
        # x_axis = range(1, 8761)  # 从1到8760
        # plt.plot(x_axis, ESS_FSoctime, label='ESS_FSoctime')
        # # 添加标签和标题
        # plt.xlabel('Time/h')
        # plt.ylabel('FSOC/%')
        # plt.title('ESS_FSoc ')
        # plt.legend()
        # plt.show()
        # #
        # # 绘制前 10 个EV的折线图
        # n = 5  # 前5个元素
        # fig, axes = plt.subplots(n, 1, figsize=(10, 2 * n), sharex=True)
        # df_ev_fsoc = pd.DataFrame(EV_FSoctime)
        # for i in range(n):
        #     ax = axes[i]
        #     ax.plot(df_ev_fsoc.index, df_ev_fsoc[i], label=f'EV_FSoctime_{i + 1}')
        #     ax.legend()
        # plt.xlabel('Time')
        # plt.ylabel('FSOC/%')
        # plt.title('10 EV')
        # # 调整子图之间的间距
        # plt.tight_layout()
        # # 显示图形
        # plt.show()


#===============
        return cost

# ================================================================================================================================ #
cost1 = Cost(11800, 1000, 1)
print(cost1.get_cost())


