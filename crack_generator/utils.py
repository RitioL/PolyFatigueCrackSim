import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
from scipy.spatial import Voronoi, voronoi_plot_2d
from scipy.linalg import inv


# Slip systems of FCC crystals
#   #          Slip plane          Slip direction
#   1         (  1  1  1 )          [  0 -1  1 ]
#   2         (  1  1  1 )          [  1  0 -1 ]
#   3         (  1  1  1 )          [ -1  1  0 ]
#   4         ( -1  1  1 )          [  1  0  1 ]
#   5         ( -1  1  1 )          [  1  1  0 ]
#   6         ( -1  1  1 )          [  0 -1  1 ]
#   7         (  1 -1  1 )          [  0  1  1 ]
#   8         (  1 -1  1 )          [  1  1  0 ]
#   9         (  1 -1  1 )          [  1  0 -1 ]
#  10         (  1  1 -1 )          [  0  1  1 ]
#  11         (  1  1 -1 )          [  1  0  1 ]
#  12         (  1  1 -1 )          [ -1  1  0 ]

# Store slip systems as a list of dictionaries
slip_systems = [
    {"slip_plane": [1, 1, 1], "slip_directions": [[0, -1, 1], [1, 0, -1], [-1, 1, 0]]},
    {"slip_plane": [-1, 1, 1], "slip_directions": [[1, 0, 1], [1, 1, 0], [0, -1, 1]]},
    {"slip_plane": [1, -1, 1], "slip_directions": [[0, 1, 1], [1, 1, 0], [1, 0, -1]]},
    {"slip_plane": [1, 1, -1], "slip_directions": [[0, 1, 1], [1, 0, 1], [-1, 1, 0]]}
]

# 1.根据欧拉角计算假设的最可能滑移方向
def euler_to_rotation_matrix(phi1, Phi, phi2):
    """将欧拉角转换为旋转矩阵"""
    rotation = R.from_euler('zxz', [phi1, Phi, phi2], degrees=True)
    return rotation.as_matrix()

def calculate_2D_slip(euler_angles):
    """根据欧拉角计算2D法向和滑移方向"""
    # 提取欧拉角
    phi1, Phi, phi2 = euler_angles
    rotation_matrix = euler_to_rotation_matrix(phi1, Phi, phi2)
    
    slip_planes = [np.array(x["slip_plane"]) for x in slip_systems]

    # 找到晶面法向与x正方向夹角最大的滑移方向
    min_angle = float('inf')
    max_angle = 0
    best_plane = None
    best_direction = None
    
    for index, plane in enumerate(slip_planes):
        slip_plane_3D = plane / np.linalg.norm(plane)  # 单位化
        slip_plane_3D_rotated = rotation_matrix @ slip_plane_3D  # 进行旋转

        # 计算与x正方向的夹角
        angle = np.arccos(np.clip(np.dot(slip_plane_3D_rotated, [1, 0, 0]), -1.0, 1.0))  # 计算夹角

        # 如果夹角大于pi/2，取pi减去该角度
        if angle > np.pi / 2:
            angle = np.pi - angle

        if angle > max_angle:
            max_angle = angle
            best_plane = index

    # 找到选择的晶面其滑移方向与x正方向夹角最小的滑移方向
    slip_directions = [np.array(x) for x in slip_systems[best_plane]["slip_directions"]]

    for direction in slip_directions:
        slip_direction_3D = direction / np.linalg.norm(direction)  # 单位化
        slip_direction_3D_rotated = rotation_matrix @ slip_direction_3D  # 进行旋转

        # 计算与x正方向的夹角
        angle = np.arccos(np.clip(np.dot(slip_direction_3D_rotated, [1, 0, 0]), -1.0, 1.0))  # 计算夹角

        # 如果夹角大于pi/2，取pi减去该角度
        if angle > np.pi / 2:
            angle = np.pi - angle

        if angle < min_angle:
            min_angle = angle
            best_direction = slip_direction_3D_rotated[:2]  # 只取2D部分
        
    # 确保滑移方向指向特定的半空间
    if best_direction[0] < 0:
        best_direction = -best_direction

    return best_direction, min_angle*180/np.pi

def calculate_2D_slip_simplified(euler_angles):
    """根据欧拉角计算2D法向和滑移方向"""
    # 提取欧拉角
    # print(euler_angles)
    phi1, Phi, phi2 = euler_angles
    rotation_matrix = euler_to_rotation_matrix(phi1, Phi, phi2)
    
    slip_directions = [
        np.array([0, -1, 1]),
        np.array([1, 0, -1]),
        np.array([-1, 1, 0]),
        np.array([1, 0, 1]),
        np.array([1, 1, 0]),
        np.array([0, -1, 1]),
        np.array([0, 1, 1]),
    ]
    # slip_directions = [
    #     np.array([1, 1, 0]),   
    #     np.array([1, -1, 0]),
    #     np.array([-1, 1, 0]),  
    #     np.array([0, 1, 1]),   
    #     np.array([0, -1, 1]),  
    #     np.array([1, 0, 1]),  
    #     np.array([-1, 0, 1]),  
    # ]

    # 找到与x正方向夹角最小的滑移方向
    min_angle = float('inf')
    best_direction = None
    
    for direction in slip_directions:
        slip_direction_3D = direction / np.linalg.norm(direction)  # 单位化
        slip_direction_3D_rotated = rotation_matrix @ slip_direction_3D  # 进行旋转

        # 计算与x正方向的夹角
        angle = np.arccos(np.clip(np.dot(slip_direction_3D_rotated, [1, 0, 0]), -1.0, 1.0))  # 计算夹角

        # 如果夹角大于pi/2，取pi减去该角度
        if angle > np.pi / 2:
            angle = np.pi - angle

        if angle < min_angle:
            min_angle = angle
            best_direction = slip_direction_3D_rotated[:2]  # 只取2D部分
        elif np.abs(angle-min_angle) < 1e-5 and np.random.choice([0, 1]): # 若角度相同则随机选择
            min_angle = angle
            best_direction = slip_direction_3D_rotated[:2]  # 只取2D部分
        
        print(angle*180/np.pi, slip_direction_3D_rotated[:2]) # debug

    # 确保滑移方向指向特定的半空间
    if best_direction[0] < 0:
        best_direction = -best_direction
    
    # 允许的最大角度是45°
    # if min_angle > np.pi / 4:
    #     min_angle = np.pi / 4
    #     best_direction[1] = best_direction[0] * best_direction[1] / np.abs(best_direction[1])

    return best_direction, min_angle*180/np.pi

# 3.遍历所有的晶界，记录哪些晶界是可以沿着扩展的，以及沿晶扩展结束的结点是哪个
def decode_euler_angles(img):
    '''将欧拉角表示的EBSD图像还原为欧拉角矩阵'''
    # 创建一个与图像相同大小的浮点数矩阵
    euler_angles = img.astype(float)
    # 反归一化
    euler_angles[:, :, 0] = img[:, :, 0] / 255.0 * 360.0 # 反归一化第一个通道
    euler_angles[:, :, 1] = img[:, :, 1] / 255.0 * 90.0 # 反归一化第一个通道
    euler_angles[:, :, 2] = img[:, :, 2] / 255.0 * 90.0 # 反归一化第一个通道
    return euler_angles

def euler_to_rotation_matrix(phi1, Phi, phi2):
    phi1 = np.radians(phi1)
    Phi = np.radians(Phi)
    phi2 = np.radians(phi2)

    R1 = np.array([
        [np.cos(phi1), -np.sin(phi1), 0],
        [np.sin(phi1), np.cos(phi1), 0],
        [0, 0, 1]
    ])
    
    R2 = np.array([
        [1, 0, 0],
        [0, np.cos(Phi), np.sin(Phi)],
        [0, -np.sin(Phi), np.cos(Phi)]
    ])
    
    R3 = np.array([
        [np.cos(phi2), -np.sin(phi2), 0],
        [np.sin(phi2), np.cos(phi2), 0],
        [0, 0, 1]
    ])

    return R3 @ R2 @ R1

def define_symmetry_matrices():
    T = np.zeros((3, 3, 24))
    T[:, :, 0] = np.eye(3)
    T[:, :, 1] = np.array([[0, 0, -1], [0, -1, 0], [-1, 0, 0]])
    T[:, :, 2] = np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]])
    T[:, :, 3] = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, -1]])
    T[:, :, 4] = np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]])
    T[:, :, 5] = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
    T[:, :, 6] = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])
    T[:, :, 7] = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
    T[:, :, 8] = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
    T[:, :, 9] = np.array([[-1, 0, 0], [0, -1, 0], [0, 0, 1]])
    T[:, :, 10] = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]])
    T[:, :, 11] = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]])
    T[:, :, 12] = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]])
    T[:, :, 13] = np.array([[0, 0, -1], [-1, 0, 0], [0, 1, 0]])
    T[:, :, 14] = np.array([[0, -1, 0], [0, 0, 1], [-1, 0, 0]])
    T[:, :, 15] = np.array([[0, 1, 0], [0, 0, -1], [-1, 0, 0]])
    T[:, :, 16] = np.array([[0, 0, -1], [1, 0, 0], [0, -1, 0]])
    T[:, :, 17] = np.array([[0, 0, 1], [-1, 0, 0], [0, -1, 0]])
    T[:, :, 18] = np.array([[0, -1, 0], [0, 0, -1], [1, 0, 0]])
    T[:, :, 19] = np.array([[0, 1, 0], [1, 0, 0], [0, 0, -1]])
    T[:, :, 20] = np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]])
    T[:, :, 21] = np.array([[0, 0, 1], [0, -1, 0], [1, 0, 0]])
    T[:, :, 22] = np.array([[0, -1, 0], [-1, 0, 0], [0, 0, -1]])
    T[:, :, 23] = np.array([[-1, 0, 0], [0, 0, -1], [0, -1, 0]])
    return T

def calculate_misorientation(euler_angles1, euler_angles2):
    phi1, Phi, phi2 = euler_angles1[0:3]
    q1, Q, q2 = euler_angles2[0:3]
    g1 = euler_to_rotation_matrix(phi1, Phi, phi2)
    g2 = euler_to_rotation_matrix(q1, Q, q2)
    T = define_symmetry_matrices()
    
    theta = np.zeros(24)
    for i in range(24):
        m = inv(T[:, :, i] @ g1) @ g2
        trace_m = np.trace(m)
        trace_m = min(max(trace_m, -1.0), 3.0)
        theta[i] = np.arccos(0.5 * (trace_m - 1))
    
    min_theta = np.min(theta)
    min_theta_deg = np.degrees(min_theta)
    
    return min_theta_deg

# 条件1.晶界与x方向的夹角在45°以内
def condition1(point1, point2):
    x1, y1 = point1
    x2, y2 = point2

    # 计算斜率
    if x2 - x1 == 0:  # 处理垂直情况
        return (False, 90)  # 与x轴夹角为90度，直接返回钝角的互补角

    slope = (y2 - y1) / (x2 - x1)

    # 计算与x轴的夹角（弧度）
    angle_radians = np.arctan(slope)
    angle_degrees = np.degrees(angle_radians)

    # 确保夹角在[0, 180]范围内
    if angle_degrees < 0:
        angle_degrees += 180

    # 如果夹角是钝角，则取互补角
    if angle_degrees > 90:
        angle_degrees = 180 - angle_degrees

    return (angle_degrees <= 45, angle_degrees)

# 条件2.晶界两侧晶粒的取向差在15°以上
def condition2(ori1, ori2):
    misorientation_angle = calculate_misorientation(ori1, ori2)
    # print(misorientation_angle)
    return misorientation_angle > 15.0 # 判断是否大于15度

# 4.获得当前位置位于哪个cell
# 获得当前cell的id，需要传入cell信息，当前坐标
# 只需要查询当前坐标离哪一个cell的种子点比较近

def get_current_cell(position, cell_data):
    # 1. 提取所有种子点坐标
    coordinates = np.array(cell_data['Seed Coordinates'].tolist())
    # 2. 计算 position 和每个种子点的欧式距离
    distances = np.linalg.norm(coordinates - position, axis=1)
    # 3. 找到最短距离的行索引
    min_distance_index = distances.argmin()

    return cell_data.iloc[min_distance_index, 0]

# 5.计算裂纹会碰到哪条晶界
# 定义函数来计算射线与线段的交点
def line_intersection(ray_origin, ray_direction, point1, point2):
    # Ray: P + t * v
    # Line segment: A + u * (B - A)
    
    x1, y1 = ray_origin
    x2, y2 = ray_origin + ray_direction
    x3, y3 = point1
    x4, y4 = point2
    
    # 计算交点
    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    
    if denominator == 0:
        return None  # 平行，没有交点
    
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
    u = ((x1 - x3) * (y1 - y2) - (y1 - y3) * (x1 - x2)) / denominator
    
    if t >= 0 and 0 <= u <= 1:
        # 计算交点坐标
        intersection = (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        return intersection
    else:
        return None
    
# 找到相交的边和交点
def find_intersection_point(position, direction, cell_edges, edge_data, node_data, threshold=1e-6):
    for edge in cell_edges:
        point1_id, point2_id = edge_data.iloc[edge, 1]  # 获取边界的两个点ID
        point1 = node_data.iloc[point1_id, 1]
        point2 = node_data.iloc[point2_id, 1]
        
        # 计算交点
        intersection = line_intersection(position, direction, point1, point2)
        
        # 注意：intersection_edge is None 这个情况是因为扩展方向夹角已经大于晶界的夹角了，
        # 导致扩展方向指向目标晶粒的紧邻晶粒。此时认为扩展停止

        if intersection is not None:
            # 计算position与intersection之间的距离，排除position就是交点的情况
            distance = np.linalg.norm(np.array(position) - np.array(intersection))
            
            if distance > threshold:  # 如果距离大于阈值，说明交点有效
                return intersection, edge
    # print(intersection)
    return None, None

# 6.到达三叉晶界之后如何扩展
# 找到与当前结点相连的、包含x值比当前结点大的结点的晶界，确定它们是否可开裂。
# 如果可开裂，则沿着角度最小的那个开裂，这个晶界的另一个端点作为下一个要记录的position
# 如果不可开裂，返回False
def condition3(cur_node, node_data, edge_data):
    # 找到符合条件的、与当前结点相连的晶界和结点
    neighbor_nodes = []
    neighbor_edges = []
    for i in range(len(edge_data)):
        # 判断晶界是否可开裂
        if not edge_data.loc[i, 'Is Intergranular']:
            continue

        # 记录晶界两个端点
        node1, node2 = edge_data.loc[i, 'Node Indices']

        # 看看是否有邻近结点，若有还需判断是否为当前结点前方的结点
        if cur_node == node1 and node_data.loc[cur_node, 'Node Coordinates'][0] < node_data.loc[node2, 'Node Coordinates'][0]:
            neighbor_nodes.append(node2)
            neighbor_edges.append(i)
        elif cur_node == node2 and node_data.loc[cur_node, 'Node Coordinates'][0] < node_data.loc[node1, 'Node Coordinates'][0]:
            neighbor_nodes.append(node1)
            neighbor_edges.append(i)
        else:
            continue
    
    if len(neighbor_nodes) > 0: # 有符合条件的则会沿晶
        potential_node = neighbor_nodes[0]
        potential_edge = neighbor_edges[0]
        for node, edge in zip(neighbor_nodes, neighbor_edges):
            if edge_data.loc[edge, 'Angle'] < edge_data.loc[potential_edge, 'Angle']:
                potential_node = node
                potential_edge = edge

        return potential_node
    
    else: # 否则穿晶
        return False

# 7.绘图相关
# 归一化欧拉角并映射到 RGB
def orientation_to_rgb(orientation):
    phi1, Phi, phi2 = orientation
    r = phi1 / 360.0  # 归一化到 [0,1]
    g = Phi / 90.0
    b = phi2 / 90.0
    # 确保颜色值在 [0,1]
    r = min(max(r, 0), 1)
    g = min(max(g, 0), 1)
    b = min(max(b, 0), 1)
    return (r, g, b)

if __name__ == '__main__':
    euler_angles = [200,40,65]
    # print(calculate_2D_slip(euler_angles))
    print(calculate_2D_slip_simplified(euler_angles))