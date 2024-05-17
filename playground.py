import numpy as np
import os

def getEdgeNodeId(path):
    """Return the node ID of top, bottom, left, and right edges of the model"""
    node_info_path = os.path.join(path, "node_info.csv")
    node_info = np.genfromtxt(node_info_path, delimiter=',')

    top_edge = []
    bottom_edge = []
    left_edge = []
    right_edge = []

    for row in node_info:
        if row[2] == 1.5:
            top_edge.append(int(row[0]))
        elif row[2] == 0.0:
            bottom_edge.append(int(row[0]))
        elif row[1] == 0.0:
            left_edge.append(int(row[0]))
        elif row[1] == 1.5:
            right_edge.append(int(row[0]))
        else:
            continue
        
    return top_edge, bottom_edge, left_edge, right_edge

root_path = r"D:\CrackImage\PolyFEM\neper\16-betterGB"
numbers = ["0_0" + str(i) for i in range(4,10,1)]
numbers.append("0_10")

for number in numbers:
    os.chdir(root_path)
        
    wp_name = "wp_" + number
    wp_path = os.path.join(root_path, wp_name)
    model_name = "poly_quad_" + number + "_modified"

    if not os.path.exists(wp_name):
        os.makedirs(wp_name)
    os.chdir(os.path.join(root_path, wp_name))
    top_edge, bottom_edge, left_edge, right_edge = getEdgeNodeId(wp_path)
    print(np.shape(top_edge))
    print(top_edge)

    break