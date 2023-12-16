from Remodel import Remodel
from HVACmodel import HVACmodel
from Qsolarmodel import Qsolarmodel
from Lightingmodel import Lightingmodel
from Peoplemodel import Peoplemodel
from EVmodel import EVmodel

from Dataread import I #辐照强度
from Dataread import T  # 温度
from Dataread import Solar_azimuth  # 太阳方位角
from Dataread import Solar_zenith # 太阳天顶角
from Dataread import H  # 湿度
from Dataread import price  #24小时
from Dataread import fst_horizon # hour
from Dataread import fst_step # hour
from Dataread import fst_iter # 迭代次数

#========
class Objective_fst:
    def __init__(self, X,Y,Z):
        self.X = X #Tsp HVAC
        self.Y = Y#P TO ESS 大于0充电小于0放电
        self.Z = Z#P TO EV


    def systemmodel_fst(self, I_fst_step, T_fst_step, H_fst_step, Solar_zenith_fst_step, Solar_azimuth_fst_step, step_forc, time, x, y, z):
        # generation and demand
        Q_re = Remodel(I_fst_step, T_fst_step, step_forc)  # 新能源发电
        Q_solar = Qsolarmodel(I_fst_step, Solar_zenith_fst_step, Solar_azimuth_fst_step)
        Q_people, Nroom = Peoplemodel(time)
        Q_lighting_heat, Q_lighting = Lightingmodel(time, Nroom)
        Q_equipheat_Normallyopen = 10000  # 常开的设备
        Q_equipheat_classopen = 2000  # 有时开的
        Q_equip_Normallyopen = 10000  # 常开的设备
        Q_equip_classopen = 2000  # 有时开的
        Q_equipment_heat = Q_equipheat_Normallyopen + Q_equipheat_classopen * Nroom
        Q_equipment = Q_equip_Normallyopen + Q_equip_classopen * Nroom
        Q_HAVC = HVACmodel(x, T_fst_step, H_fst_step, Q_solar, Q_lighting_heat, Q_equipment_heat, Q_people)
        Q_demand = Q_lighting + Q_equipment + Q_HAVC
        Q_grid = Q_demand - y - z - Q_re #大于0买电小于0卖电， Y Z大于0充电小于0放电
        hour_of_day = int(time % 24) #现在对应几点
        pricesell = 0.453
        pricebuy = price[hour_of_day]
        cost = max(Q_grid,0) * pricebuy + min(Q_grid,0) * pricesell

        Cap_EV = EVmodel(time)

        return cost,Cap_EV


    def fst(self,step_forc,time):#预测步长 与TRNSYS一致
        fst_mpciter = 0 #第几个控制步长
        cost_sum = 0


        while fst_mpciter < fst_iter: #fst_iter迭代次数
            #预测天气数据
            fst_linenum = fst_step / step_forc
            fst_forciter = fst_mpciter * fst_linenum
            I_fst_step = I[fst_forciter:fst_forciter + fst_linenum]
            T_fst_step = T[fst_forciter:fst_forciter + fst_linenum]
            Solar_azimuth_fst_step = Solar_azimuth[fst_forciter:fst_forciter + fst_linenum]
            Solar_zenith_fst_step = Solar_zenith[fst_forciter:fst_forciter + fst_linenum]
            H_fst_step = H[fst_forciter:fst_forciter + fst_linenum]
            x = self.X[fst_mpciter]
            y = self.Y[fst_mpciter]
            z = self.Z[fst_mpciter]
            SOC = #!!这个值需要被约束，每个SOC都要检查。也许
            cost_temp = self.systemmodel_fst(I_fst_step, T_fst_step, H_fst_step, Solar_zenith_fst_step, Solar_azimuth_fst_step, step_forc, time, x, y, z)
            # 第一次MPC计算
            cost_sum += cost_temp
            fst_mpciter += 1

        return cost_sum




