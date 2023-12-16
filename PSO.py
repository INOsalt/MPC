import random
import numpy as np


# 粒子类
class Particle:
    def __init__(self, bounds, n_variables):
        self.position = [np.random.uniform(bound[0], bound[1], n_variables) for bound in bounds]
        self.velocity = [np.zeros(n_variables) for _ in bounds]
        self.best_position = [np.copy(pos) for pos in self.position]
        self.best_cost = float('inf')


# 粒子群优化算法
def particle_swarm_optimization(systemmodel, bounds, n_particles, n_iterations, SOC_0, n_variables):
    particles = [Particle(bounds, n_variables) for _ in range(n_particles)]
    global_best_position = None
    global_best_cost = float('inf')

    for iteration in range(n_iterations):
        for particle in particles:
            # 更新SOC
            SOC = SOC_0
            total_cost = 0
            for i in range(n_variables):
                x, y, z = particle.position[0][i], particle.position[1][i], particle.position[2][i]
                cost, new_SOC = systemmodel(x, y, z, SOC)
                if 0.1 <= new_SOC <= 0.9:
                    SOC = new_SOC
                    total_cost += cost
                else:
                    total_cost += float('inf')  # 约束违反的高惩罚

            if total_cost < particle.best_cost:
                particle.best_cost = total_cost
                particle.best_position = [np.copy(pos) for pos in particle.position]

            if total_cost < global_best_cost:
                global_best_cost = total_cost
                global_best_position = [np.copy(pos) for pos in particle.position]

            # 更新粒子速度和位置
            w = 0.5  # 惯性系数
            c1, c2 = 2.05, 2.05  # 自我和社会学习系数
            for j in range(len(bounds)):
                r1, r2 = random.random(), random.random()
                particle.velocity[j] = (w * particle.velocity[j] +
                                        c1 * r1 * (particle.best_position[j] - particle.position[j]) +
                                        c2 * r2 * (global_best_position[j] - particle.position[j]))
                particle.position[j] += particle.velocity[j]

    return global_best_position, global_best_cost


# 优化参数
n_particles = 30
n_iterations = 100
bounds = [(0, 1), (0, 1), (0, 1)]  # 假设X, Y, Z的范围都是从0到1
SOC_0 = 0.5
n_variables = 10  # X, Y, Z数组的长度

# 运行PSO
best_position, best_cost = particle_swarm_optimization(systemmodel, bounds, n_particles, n_iterations, SOC_0,
                                                       n_variables)
print("Best X:", best_position[0])
print("Best Y:", best_position[1])
print("Best Z:", best_position[2])
print("Best Cost:", best_cost)
