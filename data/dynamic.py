def computeOpenloopSolution(mpc_model, u):
    """
    计算开环方案的状态

    Parameters:
    - mpc_model: MPC 模型
    - u: 控制输入
    - args: 额外参数（可选）

    Returns:
    - x: 开环状态数组
    """
    # 初始化状态数组，第一个状态为初始状态 xmeasure
    x = [mpc_model.xmeasure]

    # 循环计算开环状态
    for k in range(mpc_model.horizon):
        # 使用系统模型 dynamic 计算下一个状态
        x.append(dynamic(mpc_model.system_model, x[k], u[:, k]))

    return x
