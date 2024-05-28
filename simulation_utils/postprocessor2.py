# 绘制EBSD和Crack图
import os
import json
from utils import *

with open('config.json', 'r') as f:
    config = json.load(f)
root_path = str(config.get('root_path'))
save_path = [root_path + str(i) for i in [r"\images-ebsd", r"\images-crack", r"\images-both"]]
    
# 检查保存路径是否存在
for path in save_path:
    if not os.path.exists(path):
        os.makedirs(path)
    
# setFigureSize(6, 4)

for wp_name in ["wp{:03d}".format(i) for i in range(1,2,1)]:
    path = os.path.join(root_path, wp_name)
    save_singal = drawCrack(path, save_path=save_path[1], save_name=wp_name)
    # 如果裂纹长度达到阈值则save_singal为真
    if save_singal:
        drawEBSD(path, save_path=save_path[0], save_name=wp_name)
        # 叠加EBSD和Crack
        input = [os.path.join(path, wp_name + ".png") for path in save_path]
        overlayImages(*input)
