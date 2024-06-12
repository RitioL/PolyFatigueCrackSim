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

def calculateCrackLength(philsm_path):
    '''根据philsm结果计算每一帧的裂纹长度'''
    # 读取CSV文件
    df = pd.read_csv(philsm_path)

    # 筛选有效数据
    df = df[(df['PHILSM'] > -1e+20) & (df['PHILSM'] < 1e+20)]

    # 按照帧号分组
    grouped = df.groupby('Frame')

    # 生成新的x坐标
    x_new = np.linspace(0, 1.5, 750)
    y_new = np.linspace(0, 1.0, 500)
    x_new, y_new = np.meshgrid(x_new, y_new)

    # 记录每一帧的裂纹长度
    crack_lengths = {}

    # 计算各帧裂纹沿x方向的长度
    for frame, group in grouped:
        x = group['X']
        y = group['Y']
        PHILSM = group['PHILSM']

        # 计算插值结果
        philsm_new = interpolate.griddata((x, y), PHILSM, (x_new, y_new), method='linear')

        # 查找裂纹路径中PHILSM=0的最大x坐标
        max_x_coordinate = None
        contours = plt.contour(x_new, y_new, philsm_new, levels=[0], colors='black')
        for path in contours.collections[0].get_paths():
            max_x = np.max(path.vertices[:, 0])
            if max_x_coordinate is None or max_x > max_x_coordinate:
                max_x_coordinate = max_x

        # 记录裂纹长度
        crack_lengths[frame] = max_x_coordinate

    return crack_lengths

def isInvalidCrack(path, threshold=0.4):
    '''返回当前裂纹是否达标的信号'''
    if not os.path.exists(path):
        return f"Warning: {path} is not existed!"
    philsm_path = os.path.join(path, 'philsm.csv')
    crack_lengths = calculateCrackLength(philsm_path)
    for frame, length in crack_lengths.items():
        crack_length = length
    if crack_length >= threshold:
        print(f"Valid: Crack length ({round(crack_length, 4)} mm) of frame {frame} >= {threshold} mm.")
        return True
    else:
        print(f"Invalid: Crack length ({round(crack_length, 4)} mm) of frame {frame} < {threshold} mm.")
        return False

def analyzeCrack(path):
    '''返回裂纹沿x方向的长度不再增长的帧和对应的裂纹长度,以及最后一帧及其裂纹长度'''
    if not os.path.exists(path):
        return f"Warning: {path} is not existed!"
    philsm_path = os.path.join(path, 'philsm_selected_frames.csv')
    crack_lengths = calculateCrackLength(philsm_path)

    # 裂纹扩展结果中的最后一帧
    last_frame = max(crack_lengths.keys())
    last_length = round(crack_lengths[last_frame], 4)

    # 裂纹沿x方向的长度不再增长的帧
    stop_frame = None
    stop_length = None
    singal = True

    for frame, length in sorted(crack_lengths.items(), reverse=True):
        if (stop_length is not None) and (length-stop_length < -0.02):
            stop_length = round(stop_length, 4)
            print(f"Crack length along x-direction stops increasing at frame {stop_frame}/{last_frame},")
            print(f"    and reaches {stop_length} mm (total {last_length} mm) when it stops.")
            singal = False
            break 
        else:
            stop_frame = frame
            stop_length = length

    if singal:
        print(f"Crack length along x-direction stops increasing at frame {stop_frame}/{last_frame},")
        print(f"    and reaches {stop_length} mm (total {last_length} mm) when it stops.")

    # 返回裂纹沿x方向的长度不再增长的帧和对应的裂纹长度,以及最后一帧及其裂纹长度
    return stop_frame, stop_length, last_frame, last_length

# @timeit
def drawCrack(path, csv_name, frame_idx, save_path=None, save_name=None, show=False):
    
    philsm_path = os.path.join(path, csv_name)
    df = pd.read_csv(philsm_path)
    df = df[df['Frame'] == frame_idx]
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
    plt.contour(x_new, y_new, philsm_new, levels=[0], colors='black')
    plt.gca().set_aspect('equal', adjustable='box')  # 保持纵横比例一致
    plt.xlim([0,1.5])
    plt.ylim([0,1.0])
    plt.axis('off')

    # 显示图像
    if show:
        plt.show()
    
    if save_path is not None and save_name is not None:
        # 去掉坐标轴以及白边等
        plt.axis('off')
        plt.savefig(os.path.join(save_path, f'{save_name}.png'), bbox_inches='tight', pad_inches=0)
        plt.close()
    
# @timeit
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
    
    if save_path is not None and save_name is not None:
        # 去掉坐标轴以及白边等
        plt.axis('off')
        plt.savefig(os.path.join(save_path, f'{save_name}.png'), bbox_inches='tight', pad_inches=0)
        plt.close()
    
# @timeit
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