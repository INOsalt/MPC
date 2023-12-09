import time
from scipy.optimize import minimize
from objective import Cost
#==========================
def solveOptimalControlProblem(initial_guess):
    def cost(params):
        x, y, z, n = params
        cost = Cost(x, y)
        return cost.get_cost()

    # 初始猜测
    initial_guess = [1.0, 2.0, 3.0, 4.0]
    result = minimize(cost, initial_guess, method='trust-constr')  # 使用 trust-constr 优化算法，适用于凸优化问题

    if result.success:
        optimal_x, optimal_y, optimal_z, optimal_n = result.x
        return optimal_x, optimal_y, optimal_z, optimal_n
    else:
        print("Optimization failed.")
        return None#如果优化没成功就不变

#============================

# def fst_mpc(fst):
#
#     # 计算电力平衡
#     fst.net_load = fst.load - fst.pv - fst.wind #和grid互动的
#
#     # 解决最优控制问题
#     t_Start = time.time()
#     fst.u0, V_current, exitflag, output = solveOptimalControlProblem(fst)
#     t_Elapsed = time.time() - t_Start
#
#     if fst.iprint >= 1:
#         printSolution(fst.printClosedloopData, fst.mpciter, fst.xmeasure, fst.u0, fst.iprint, exitflag, t_Elapsed, output_data)
#
#     # 保存当前信息
#     t = output
#     x = computeOpenloopSolution(fst, fst.u0)
#     u = fst.u0
#
#     return t, x, u
