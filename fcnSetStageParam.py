import numpy as np

class MPCModel:
    def __init__(self, name, from_fst=None):
        self.name = name
        self.from_fst = from_fst
        self.iter = None
        self.horizon = None
        self.u0 = None
        self.xmeasure = None
        self.option = None
        self.costfunction = None
        self.nonlinearconstraints = None
        self.runningcosts = None
        self.terminalcosts = None
        self.nl_constraints = None
        self.nl_terminalconstraints = None
        self.l_constraints = None
        self.system_model = None
        self.battery = None
        self.u = []
        self.x = []
        self.f = []
        self.iprint = 5
        self.printClosedloopData = None
        self.flag = 0

def fcnSetStageParam(input):
    if input == 'fst':
        mpcModel = MPCModel(name='fst')
        mpcModel.iter = 24 * 2  # 7天: 168
        mpcModel.horizon = 48  # 默认值为48
        mpcModel.u0 = np.tile([4.99999, 0.00001], (1, 48))  # 2个初始控制变量
        mpcModel.xmeasure = [0.000, 50]  # 2个初始状态
        # 设置优化算法选项
        tol_opt = 1e-8
        opt_option = 1
        iprint = 5
        mpcModel.option = fcnChooseOption(opt_option, tol_opt, mpcModel.u0)
        # 设置其他函数
        mpcModel.costfunction = costfunction
        mpcModel.nonlinearconstraints = nonlinearconstraints
        mpcModel.runningcosts = runningcosts
        mpcModel.terminalcosts = terminalcosts
        mpcModel.nl_constraints = nl_constraints
        mpcModel.nl_terminalconstraints = nl_terminalconstraints
        mpcModel.l_constraints = l_constraints
        mpcModel.system_model = system_model
        # 设置系统模型
        mpcModel.battery = batteryModel()

    elif input == 'snd':
        mpcModel = MPCModel(name='snd', from_fst=2)
        mpcModel.iter = 12
        mpcModel.horizon = 12
        # 设置其他函数
        mpcModel.costfunction = snd_costfunction
        mpcModel.nonlinearconstraints = snd_nonlinearconstraints
        mpcModel.runningcosts = snd_runningcosts
        mpcModel.terminalcosts = snd_terminalcosts
        mpcModel.nl_constraints = snd_nl_constraints
        mpcModel.nl_terminalconstraints = snd_nl_terminalconstraints
        mpcModel.l_constraints = snd_l_constraints
        mpcModel.system_model = snd_system_model
        # 设置系统模型
        mpcModel.battery = batteryModel()
        mpcModel.flag = 0

    else:
        raise ValueError('参数设置错误。请检查输入')

    return mpcModel

# 示例：调用函数并获取返回的结果
fst_mpcModel = fcnSetStageParam('fst')
snd_mpcModel = fcnSetStageParam('snd')
