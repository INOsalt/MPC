from Remodel import Remodel
from HVACmodel import HVACmodel
from Qsolarmodel import Qsolarmodel
from Lightingmodel import Lightingmodel
from Peoplemodel import Peoplemodel
#========
Class fst:
    def objective_fst(I_fst_step, T_fst_step, H_fst_step, Solar_zenith_fst_step, Solar_azimuth_fst_step, step, time):
        # generation and demand
        Q_re = Remodel(I_fst_step, T_fst_step, step)  # 新能源发电
        Q_solar = Qsolarmodel(I_fst_step, Solar_zenith_fst_step, Solar_azimuth_fst_step)
        Q_people, Nroom = Peoplemodel(time)
        Q_lighting_heat, Q_lighting = Lightingmodel(time, Nroom)
        Q_equipheat_Normallyopen = 10000  # 常开的设备
        Q_equipheat_classopen = 2000  # 有时开的
        Q_equip_Normallyopen = 10000  # 常开的设备
        Q_equip_classopen = 2000  # 有时开的
        Q_equipment_heat = Q_equipheat_Normallyopen + Q_equipheat_classopen * Nroom
        Q_equipment = Q_equip_Normallyopen + Q_equip_classopen * Nroom
        Q_HAVC = HVACmodel(T_fst_step, H_fst_step, Q_solar, Q_lighting_heat, Q_equipment_heat, Q_people)
        Q_demand = Q_lighting + Q_equipment + Q_HAVC