import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi
from matplotlib.collections import PolyCollection
from utils import *


def main(seed=42):
    # 0. 初始化
    position = (0.4,1.0) # 出发位置
    np.random.seed(seed) # 随机种子
    early_stopping = False

    # 1. 生成随机种子点并生成 Voronoi 图
    points = np.random.uniform(0, 2, size=(150, 2)) # 生成200个种子点，坐标范围在[0, 2]之间
    vor = Voronoi(points)

    # debug
    # fig, ax = plt.subplots()
    # voronoi_plot_2d(vor, ax=ax)
    # ax.set_xlim(0.5, 1.5)
    # ax.set_ylim(0.5, 1.5)
    # ax.set_aspect('equal')
    # fig.savefig('test.png')

    # 2. cell 级别信息，包含晶界编号，晶粒取向
    cell_info = []
    for i, region_index in enumerate(vor.point_region):
        region = vor.regions[region_index]
        
        # 查找该 cell 相关的 ridge（晶界）编号
        cell_ridges = [idx for idx, ridge in enumerate(vor.ridge_points) if i in ridge]
        # 晶粒取向
        phi1_choice = np.arange(0, 361, 45)
        Phi_choice = np.arange(0, 51, 10)
        phi2_choice = np.arange(0, 91, 20)
        phi1 = np.random.choice(phi1_choice)
        Phi = np.random.choice(Phi_choice)
        phi2 = np.random.choice(phi2_choice)
        # phi1 = np.random.uniform(0, 360)
        # Phi = np.random.uniform(0, 55)
        # phi2 = np.random.uniform(0, 90)
        cell_info.append({
            'Cell Index': i,
            'Seed Coordinates': tuple(points[i]),
            'Ridge Indices': cell_ridges,
            'Orientation': tuple(round(angle, 2) for angle in [phi1, Phi, phi2])
        })

    cell_data = pd.DataFrame(cell_info)

    # 3. edge 级别信息
    edges = []
    for idx, ridge in enumerate(vor.ridge_vertices):
        # if -1 not in ridge:  # 排除无穷远晶界
        seed_indices = vor.ridge_points[idx]  # 组成晶界的两个种子点编号
        # else:
        #     seed_indices = None  # 对于无穷远晶界，设置为 None
        edges.append({
            'Edge Index': idx,
            'Node Indices': ridge,  # 晶界两端的节点编号
            'Seed Indices': seed_indices  # 晶界两边的种子点编号
        })

    edge_data = pd.DataFrame(edges)

    # 4. node 级别信息
    node_data = pd.DataFrame({
        'Node Index': range(len(vor.vertices)),
        'Node Coordinates': [tuple(v) for v in vor.vertices]
    })

    # 5. 更新edge_data，记录是否可以沿晶断裂、与x轴的夹角、沿晶所会到达的edge端点
    # 初始化列
    edge_data['Is Intergranular'] = False
    edge_data['Angle'] = None # 与x轴的夹角
    edge_data['Potential Node'] = None

    # 获取必要的数据，避免每次循环都查找
    seed_indices = edge_data['Seed Indices'].values
    node_indices = edge_data['Node Indices'].values
    cell_orientations = cell_data['Orientation'].values
    node_coordinates = node_data['Node Coordinates'].values

    # 使用一个mask标记满足条件的行，便于后续向量化处理
    mask = edge_data['Node Indices'].apply(lambda nodes: nodes[0] != -1 and nodes[1] != -1)

    # 遍历满足条件的行
    for i in np.where(mask)[0]:
        cell1, cell2 = seed_indices[i]
        node1, node2 = node_indices[i]

        cell1_ori = cell_orientations[cell1]
        cell2_ori = cell_orientations[cell2]
        node1_coor = node_coordinates[node1]
        node2_coor = node_coordinates[node2]
        
        # 判断条件1和条件2
        c1, angle = condition1(node1_coor, node2_coor)
        c2 = condition2(cell1_ori, cell2_ori)

        if c1 and c2:
            edge_data.loc[i, 'Is Intergranular'] = True
            edge_data.loc[i, 'Angle'] = angle

            # 选择 Potential Node
            edge_data.loc[i, 'Potential Node'] = node1 if node1_coor[0] > node2_coor[0] else node2

    # 6.裂纹按照既定规则进行扩展
    position_list = []
    position_list.append(position) # 记录扩展转折点坐标
    tri_point = False # 是否到达三叉晶界

    cur_cell = get_current_cell(position, cell_data)

    def is_within_window(position):
        return 0.25 <= position[0] <= 1.5 and 0.5 <= position[1] <= 1.5

    while is_within_window(position):
        
        cur_slip, _ = calculate_2D_slip(cell_data.loc[cur_cell, 'Orientation'])
        cur_edges = cell_data.loc[cur_cell, 'Ridge Indices']
        # print("angle:", _)
        # 穿晶到某晶界上
        position, intersection_edge = find_intersection_point(position, cur_slip, cur_edges, edge_data, node_data)
        if intersection_edge is None: # 此时裂纹扩展停止
            return not early_stopping
        position_list.append(position) # 记录与晶界的交点

        # 判断下一步沿晶还是穿晶
        if edge_data.loc[intersection_edge, 'Is Intergranular']: # 沿晶
            next_node = edge_data.loc[intersection_edge, 'Potential Node']
            position = node_data.loc[next_node, 'Node Coordinates'] # 更新position
            position_list.append(position) # 记录下一个坐标/晶界端点
            if not is_within_window(position): # 更新position后若超出观察窗口则退出
                break

            tri_point = True
            while tri_point: # 当扩展到三叉晶界时
                c3 = condition3(next_node, node_data, edge_data)
                if c3:
                    next_node = c3
                    position = node_data.loc[next_node, 'Node Coordinates'] # 更新position
                    position_list.append(position) # 记录下一个坐标/晶界端点
                    if not is_within_window(position): # 更新position后若超出观察窗口则退出
                        break
                else:
                    # trick：穿晶则向前扩展一小段距离
                    position = (position[0] + 0.005, position[1])
                    position_list.append(position) # 记录下一个坐标/晶界端点
                    tri_point = False
                    cur_cell = get_current_cell(position, cell_data)
                    if not is_within_window(position): # 更新position后若超出观察窗口则退出
                        break
        else:
            # 如果穿晶需要获取下一步晶粒的信息，即当前晶界另一边的晶粒信息
            seed_indices = edge_data['Seed Indices'][intersection_edge]
            cur_cell = seed_indices[0] if seed_indices[0] != cur_cell else seed_indices[1]

    # 7.绘图和保存结果
    # 为每个 cell 生成颜色
    cell_data['Color'] = cell_data['Orientation'].apply(orientation_to_rgb)

    # 创建一个颜色列表，顺序与 Voronoi regions 对应
    color_list = []
    polygons = []
    for point_idx, region_idx in enumerate(vor.point_region):
        region = vor.regions[region_idx]
        if not region or -1 in region:
            # 忽略无限区域
            continue
        # 获取多边形顶点
        polygon = [vor.vertices[i] for i in region]
        polygons.append(polygon)
        # 获取对应的颜色
        color = cell_data['Color'].iloc[point_idx]
        color_list.append(color)

    # 创建 PolyCollection
    collection = PolyCollection(polygons, facecolors=color_list, edgecolors='none', antialiaseds=True)

    # 绘制图形
    fig1, ax1 = plt.subplots(figsize=(6, 6), dpi=200)
    fig2, ax2 = plt.subplots(figsize=(6, 6), dpi=200)

    # 绘制第一个图形
    ax1.add_collection(collection)
    ax1.set_xlim(0.5, 1.5)
    ax1.set_ylim(0.5, 1.5)
    ax1.set_aspect('equal')
    ax1.axis('off')

    # 绘制第二个图形
    x_values = [pos[0] for pos in position_list]
    y_values = [pos[1] for pos in position_list]
    ax2.plot(x_values, y_values, color='black', linestyle='-', linewidth=2)
    ax2.set_xlim(0.5, 1.5)
    ax2.set_ylim(0.5, 1.5)
    ax2.set_aspect('equal')
    ax2.axis('off')

    # 分别保存图形为不同文件
    fig1.savefig(os.path.join('ebsd', f'{seed:03}.png'), bbox_inches='tight', pad_inches=0)
    fig2.savefig(os.path.join('crack', f'{seed:03}.png'), bbox_inches='tight', pad_inches=0)

    # 关闭图形窗口以节省内存
    plt.close(fig1)
    plt.close(fig2)
    # plt.show()

    return early_stopping


if __name__ == "__main__":
    count_ = 0
    for i in range(0,10000,1):
        early_stopping = main(seed=i)
        print(f"Seed {i} has done. Crack early stopped: {early_stopping}")
        if not early_stopping:
            count_ += 1
        if count_ == 10:
            break