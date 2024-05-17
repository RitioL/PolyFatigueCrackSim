import time
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from scipy import interpolate
import os
import cv2


def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Function '{func.__name__}' elapsed time: {elapsed_time:.4f} seconds")
        return result
    return wrapper

def setFigureSize(width, height):
    plt.rcParams['figure.figsize'] = (width, height)

@timeit
def drawEBSD(path, save_path=None, save_name=None, show=False):
    node_info_path = os.path.join(path, "node_info.csv")
    ele_info_path = os.path.join(path, "element_info.csv")    
    mat_info_path = os.path.join(path, "material_info.csv")

    if not (os.path.exists(node_info_path) and os.path.exists(ele_info_path) and os.path.exists(mat_info_path)):
        raise ValueError("Required files do not exist, please have a check!")

    # 一次性读取所有文件
    node_info = pd.read_csv(node_info_path, header=None, index_col=0)
    ele_info = pd.read_csv(ele_info_path, header=None, index_col=0)
    mat_info = pd.read_csv(mat_info_path, header=None, index_col=0)

    # 添加列名
    node_info.columns = ["X", "Y", "Z"]
    ele_info.columns = ["Node1", "Node2", "Node3", "Node4", "Material"]    
    mat_info.columns = ["EA1", "EA2", "EA3"]

    # 获取节点坐标数组
    node_coords = node_info[["X", "Y"]].to_numpy()

    # 获取单元节点坐标   
    ele_info_indices = ele_info.iloc[:, :-1].values - 1  # 减1是为了将节点编号转换成数组索引
    ele_coords = node_coords[ele_info_indices]

    # 获取材料角度信息
    ele_materials = ele_info.iloc[:, -1].values
    angles = mat_info.loc[ele_materials].values

    # 分别归一化每个角度
    angles_normalized = np.zeros_like(angles)
    angles_normalized[:, 0] = angles[:, 0] / 360
    angles_normalized[:, 1:] = angles[:, 1:] / 90  # 第二个和第三个角度除以90

    # 创建四边形数据
    polygon_data = [(ele_coords[i, :, 0], ele_coords[i, :, 1], angles[i, :]) for i in range(ele_coords.shape[0])]

    # 创建绘图对象
    plt.close()
    fig, ax = plt.subplots()

    # 创建一个包含所有四边形的列表
    patches = [Polygon(np.column_stack([x, y]), closed=True) for x, y, _ in polygon_data]

    # 创建 PatchCollection 对象
    p = PatchCollection(patches, cmap='viridis', edgecolor='black')

    # 设置四边形的颜色和值
    p.set_color(angles_normalized)  # 归一化角度信息

    # 添加 PatchCollection 到图中
    ax.add_collection(p)

    plt.gca().set_aspect('equal', adjustable='box')  # 保持纵横比例一致
    plt.xlim([0,1.5])
    plt.ylim([0,1.0])
    plt.axis('off')
    
    # 显示图像
    if show:
        plt.show()
    
    if save_path is not None:
        # 去掉坐标轴以及白边等
        plt.axis('off')
        plt.savefig(os.path.join(save_path, f'{save_name}.png'), bbox_inches='tight', pad_inches=0)
        plt.close()

@timeit
def drawCrack(path, save_path=None, save_name=None, show=False, threshold=0.0):
    
    philsm_path = os.path.join(path, 'philsm.csv')

    df = pd.read_csv(philsm_path)
    df = df[(df['PHILSM'] > -1e+20) & (df['PHILSM'] < 1e+20)]

    x = df['X']
    y = df['Y']
    PHILSM = df['PHILSM']

    # 生成新的x坐标
    x_new = np.linspace(0, 1.5, 750)
    y_new = np.linspace(0, 1.0, 500)
    x_new, y_new = np.meshgrid(x_new,y_new)

    # 计算插值结果
    philsm_new = interpolate.griddata((x,y), PHILSM, (x_new,y_new), method='linear')

    # 绘制等值线图
    plt.close()
    contours = plt.contour(x_new, y_new, philsm_new, levels=[0], colors='black')

    # 检查等值线是否穿过设置的阈值
    signal = False
    for path in contours.collections[0].get_paths():
        if np.any(path.vertices[:, 0] > threshold):
            # 若穿过则保存信号为真
            signal = True
            break

    plt.gca().set_aspect('equal', adjustable='box')  # 保持纵横比例一致
    plt.xlim([0,1.5])
    plt.ylim([0,1.0])
    plt.axis('off')

    # 显示图像
    if show:
        plt.show()
    
    if save_path is not None and signal:
        # 去掉坐标轴以及白边等
        plt.axis('off')
        plt.savefig(os.path.join(save_path, f'{save_name}.png'), bbox_inches='tight', pad_inches=0)
        plt.close()
        # 返回保存信号
        return signal

@timeit
def overlayImages(ebsd_image_path, crack_image_path, save_path):
    # 读取黑白图像
    crack_image = cv2.imread(crack_image_path, cv2.IMREAD_GRAYSCALE)

    # 二值化处理，将图像转换为仅包含黑色和白色的二值图像
    _, binary_image = cv2.threshold(crack_image, 127, 255, cv2.THRESH_BINARY)

    # 将白色部分去除，得到黑色部分的图像
    line_image = cv2.bitwise_not(binary_image)

    # 将黑色部分取反，得到白色部分的图像
    line_image = cv2.bitwise_not(line_image)

    # 读取彩色图像
    ebsd_image = cv2.imread(ebsd_image_path)

    # 确保两张图像的大小一致
    ebsd_image = cv2.resize(ebsd_image, (line_image.shape[1], line_image.shape[0]))

    # 将黑色部分的图像叠加到彩色图像上
    result_image = cv2.bitwise_and(ebsd_image, ebsd_image, mask=line_image)

    # 保存结果图像
    cv2.imwrite(save_path, result_image)