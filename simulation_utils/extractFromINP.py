# 计算单元平均特征长度以及还原取向图
# 仅适用于gmsh生成的inp文件
import os
import pandas as pd
import numpy as np


def extractFromINP(path, inp_name):
    src = os.path.join(path, inp_name)
    new_node = os.path.join(path, "node_info.csv")
    new_ele = os.path.join(path, "element_info.csv")
    new_mat = os.path.join(path, "material_info.csv")

    with open(src, 'r') as srcFile:
        content = srcFile.read()
    content_lines = content.split('\n')

    # 1. Extract node information
    start_index = None
    end_index = None
    num_list = ("1","2","3","4","5","6","7","8","9")

    for i, line in enumerate(content_lines):
        if line.startswith("*NODE"):
            start_index = i + 1
        elif start_index is not None and not line.startswith(num_list):
            end_index = i
            break

    node_content = content_lines[start_index:end_index]

    # 2. Extract element information
    surface_list = []
    element_content = []

    for line in content_lines[end_index+1:]:
        if line.startswith("*ELEMENT"):
            surface_list.append(line.split("ELSET=Surface")[1])
        elif line.startswith(num_list):
            element_content.append(line + "," + surface_list[-1])
        else:
            break

    # 3. Extract material information    
    material_id = None
    material_angles = None
    material_index = None
    material_content = []

    for line in content_lines[end_index+1+len(element_content):]:
        if line.startswith("*Material"):
            material_id = line.split("Material-")[1]
        elif line.startswith("*User Material"):
            material_index = 0
        elif material_index == 21:
            material_angles = line.replace(" ", "").split(",")[0:3]
            material_angles.insert(0, material_id)
            material_content.append(",".join(material_angles))
            material_index = None
        if material_index is not None:
            material_index += 1

    # sava three types of information        
    with open(new_node, 'w') as new_file:
        new_file.write("\n".join(node_content))

    with open(new_ele, 'w') as new_file:
        new_file.write("\n".join(element_content))

    with open(new_mat, 'w') as new_file:
        new_file.write("\n".join(material_content))    

def getAverageElementLength(path):
    def getAreaFromPoints(points):
        # 计算给定四个节点坐标的面积
        x1, y1 = points[0]
        x2, y2 = points[1]
        x3, y3 = points[2]
        x4, y4 = points[3]

        area = abs((x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2)) / 2.0) + abs((x1*(y3-y4) + x3*(y4-y1) + x4*(y1-y3)) / 2.0)
        return area

    node_info_path = os.path.join(path, "node_info.csv")
    ele_info_path = os.path.join(path, "element_info.csv")

    if not (os.path.exists(node_info_path) and os.path.exists(ele_info_path)):
        raise ValueError("Required files do not exist, please have a check!")

    # 读取节点信息和单元信息
    node_info = pd.read_csv(node_info_path, header=None, index_col=0)
    ele_info = pd.read_csv(ele_info_path, header=None, index_col=0)

    # 添加列名
    node_info.columns = ["X", "Y", "Z"]
    ele_info.columns = ["Node1", "Node2", "Node3", "Node4", "Material"]

    # 获取节点坐标数组
    node_coords = node_info[["X", "Y"]].to_numpy()

    # 计算每个单元的面积
    ele_info_indices = ele_info.iloc[:, :-1].values - 1  # 减1是为了将节点编号转换成数组索引
    ele_coords = node_coords[ele_info_indices]
    areas = np.zeros(len(ele_coords))

    for i, points in enumerate(ele_coords):
        areas[i] = np.sqrt(getAreaFromPoints(points))

    # 计算平均单元特征长度
    average_element_length = np.mean(areas)

    print(f"Average element length of current model is: {average_element_length}.")
    return average_element_length

def getAverageElementLengthWithinGrain(path):
    def getAreaFromPoints(points):
        # 计算给定四个节点坐标的面积
        x1, y1 = points[0]
        x2, y2 = points[1]
        x3, y3 = points[2]
        x4, y4 = points[3]

        area = abs((x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2)) / 2.0) + abs((x1*(y3-y4) + x3*(y4-y1) + x4*(y1-y3)) / 2.0)
        return area

    node_info_path = os.path.join(path, "node_info.csv")
    ele_info_path = os.path.join(path, "element_info.csv")

    if not (os.path.exists(node_info_path) and os.path.exists(ele_info_path)):
        raise ValueError("Required files do not exist, please have a check!")

    # 读取节点信息和单元信息
    node_info = pd.read_csv(node_info_path, header=None, index_col=0)
    ele_info = pd.read_csv(ele_info_path, header=None, index_col=0)

    # 添加列名
    node_info.columns = ["X", "Y", "Z"]
    ele_info.columns = ["Node1", "Node2", "Node3", "Node4", "Material"]

    # 获取节点坐标数组
    node_coords = node_info[["X", "Y"]].to_numpy()

    # 初始化材料字典
    material_lengths = {}

    # 计算每个单元的面积
    ele_info_indices = ele_info.iloc[:, :-1].values - 1  # 减1是为了将节点编号转换成数组索引
    ele_coords = node_coords[ele_info_indices]
    areas = np.zeros(len(ele_coords))

    for i, points in enumerate(ele_coords):
        areas[i] = np.sqrt(getAreaFromPoints(points))
        material = ele_info.iloc[i, -1]
        if material not in material_lengths:
            material_lengths[material] = []
        material_lengths[material].append(areas[i])

    # 计算每个材料的平均单元特征长度
    average_lengths_per_material = {}
    for material, lengths in material_lengths.items():
        average_lengths_per_material[material] = np.mean(lengths)

    # print("Average element length of each material:")
    # for material, length in average_lengths_per_material.items():
    #     print(f"Material {material}: {length}")
    print("Note: You've gotten average element length WITHIN EACH GRAIN.")

    return average_lengths_per_material