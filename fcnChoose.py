def fcnChooseAlgorithm(tol_opt, opt_option, iprint, print_closedloop_data):
    """
    选择优化算法和设置相应的参数

    Parameters:
    - tol_opt: 优化容差
    - opt_option: 优化选项
        0: active-set
        1: interior-point
        2: trust-region-reflective
    - iprint: 打印选项
    - print_closedloop_data: 打印闭环数据的函数

    Returns:
    - tol_opt_out: 输出的优化容差
    - opt_option_out: 输出的优化选项
    - iprint_out: 输出的打印选项
    - print_closedloop_data_out: 输出的打印闭环数据的函数
    """
    # 如果提供了 tol_opt 参数，则使用提供的值，否则使用默认值 1e-8
    tol_opt_out = tol_opt if tol_opt is not None else 1e-8

    # 如果提供了 opt_option 参数，则使用提供的值，否则使用默认值 1
    opt_option_out = opt_option if opt_option is not None else 1

    # 如果提供了 iprint 参数，则使用提供的值，否则使用默认值 0
    iprint_out = iprint if iprint is not None else 0

    # 如果提供了 print_closedloop_data 参数，则使用提供的值，否则使用默认的 @printBlack 函数
    print_closedloop_data_out = print_closedloop_data if print_closedloop_data is not None else print_black

    return tol_opt_out, opt_option_out, iprint_out, print_closedloop_data_out


def print_black(*args, **kwargs):
    """
    默认的打印闭环数据的函数，什么也不做
    """
    pass

#========================
def fcnChooseOption(opt_option, tol_opt, u0):
    """
    指定和配置优化方法

    Parameters:
    - opt_option: 优化选项
    - tol_opt: 优化容差
    - u0: 初始控制变量

    Returns:
    - opt_option_out: 输出的优化选项
    """
    import numpy as np

    # 关闭所有警告
    np.warnings.filterwarnings('ignore')

    if opt_option == 0:
        opt_option_out = {'Display': 'off',
                          'TolFun': tol_opt,
                          'MaxIter': 10000,
                          'Algorithm': 'active-set',
                          'FinDiffType': 'forward',
                          'RelLineSrchBnd': [],
                          'RelLineSrchBndDuration': 1,
                          'TolConSQP': 1e-6}
    elif opt_option == 1:
        opt_option_out = {'Display': 'off',
                          'TolFun': tol_opt,
                          'MaxIter': 2000,
                          'Algorithm': 'interior-point',
                          'AlwaysHonorConstraints': 'bounds',
                          'FinDiffType': 'forward',
                          'HessFcn': [],
                          'Hessian': 'bfgs',
                          'HessMult': [],
                          'InitBarrierParam': 0.1,
                          'InitTrustRegionRadius': np.sqrt(u0.size),
                          'MaxProjCGIter': 2 * u0.size,
                          'ObjectiveLimit': -1e20,
                          'ScaleProblem': 'obj-and-constr',
                          'SubproblemAlgorithm': 'cg',
                          'TolProjCG': 1e-2,
                          'TolProjCGAbs': 1e-10}
    elif opt_option == 2:
        opt_option_out = {'Display': 'off',
                          'TolFun': tol_opt,
                          'MaxIter': 2000,
                          'Algorithm': 'trust-region-reflective',
                          'Hessian': 'off',
                          'MaxPCGIter': max(1, np.floor(u0.size / 2)),
                          'PrecondBandWidth': 0,
                          'TolPCG': 1e-1}

    return opt_option_out

