from Remodel import Remodel
from HVACmodel import HVACmodel
from Qsolarmodel import Qsolarmodel
from Lightingmodel import Lightingmodel
from Peoplemodel import Peoplemodel
from EVmodel import EVmodel

#========
class mpc_fst:
    def __init__(self, forcast_weather_data, price, time, step, Tin, Tout, SOC_ESS_0, Cap):
        self.time = time
        self.step_forc = step
        self.forcast_weather_data = forcast_weather_data
        self.price = price


        # self.X = X #Tsp HVAC
        # self.Y = Y#P TO ESS 大于0充电小于0放电
        # self.Z = Z#P TO EV


    def systemmodel_fst(self, I_fst_step, T_fst_step, H_fst_step, Solar_zenith_fst_step, Solar_azimuth_fst_step, x, y, z):
        # generation and demand
        Q_re = Remodel(I_fst_step, T_fst_step, self.step_forc)  # 新能源发电
        Q_solar = Qsolarmodel(I_fst_step, Solar_zenith_fst_step, Solar_azimuth_fst_step)
        Q_people, Nroom = Peoplemodel(self.time)
        Q_lighting_heat, Q_lighting = Lightingmodel(self.time, Nroom)
        Q_equipheat_Normallyopen = 10000  # 常开的设备
        Q_equipheat_classopen = 2000  # 有时开的
        Q_equip_Normallyopen = 10000  # 常开的设备
        Q_equip_classopen = 2000  # 有时开的
        Q_equipment_heat = Q_equipheat_Normallyopen + Q_equipheat_classopen * Nroom
        Q_equipment = Q_equip_Normallyopen + Q_equip_classopen * Nroom
        Q_HAVC = HVACmodel(x, T_fst_step, H_fst_step, Q_solar, Q_lighting_heat, Q_equipment_heat, Q_people)
        Q_demand = Q_lighting + Q_equipment + Q_HAVC
        Q_grid = Q_demand - y - z - Q_re #大于0买电小于0卖电， Y Z大于0充电小于0放电
        hour_of_day = int(self.time % 24) #现在对应几点
        pricesell = 0.453
        pricebuy = price[hour_of_day]
        cost = max(Q_grid,0) * pricebuy + min(Q_grid,0) * pricesell
        Cap_EV = EVmodel(self.time)

        return cost,Cap_EV


    def fst(self):#预测步长 与TRNSYS一致
        fst_mpciter = 0 #第几个控制步长
        cost_sum = 0


        while fst_mpciter < fst_iter: #fst_iter迭代次数
            #预测天气数据
            I_fst_step = self.forcast_weather_data['I'][fst_mpciter]
            T_fst_step = self.forcast_weather_data['T'][fst_mpciter]
            Solar_azimuth_fst_step = self.forcast_weather_data['Solar_azimuth'][fst_mpciter]
            Solar_zenith_fst_step = self.forcast_weather_data['Solar_zenith'][fst_mpciter]
            H_fst_step = self.forcast_weather_data['H'][fst_mpciter]

            x = self.X[fst_mpciter]
            y = self.Y[fst_mpciter]
            z = self.Z[fst_mpciter]
            SOC = #!!这个值需要被约束，每个SOC都要检查。也许
            cost_temp = self.systemmodel_fst(I_fst_step, T_fst_step, H_fst_step, Solar_zenith_fst_step, Solar_azimuth_fst_step, x, y, z)
            # 第一次MPC计算
            cost_sum += cost_temp
            fst_mpciter += 1

        return cost_sum




