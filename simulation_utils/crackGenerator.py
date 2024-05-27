import os
import numpy as np
import matplotlib.pyplot as plt
from inpEditor import rotX, rotY, rotZ, rotXYZ

# 归一化函数
def normalize(value, min_val, max_val):
    """
    Normalize a value to the range [0, 255] for RGB representation.
    """
    return int((value - min_val) / (max_val - min_val) * 255)

# 虚拟裂纹生成器
def img_generator(input, rotfun, thetas, path=''):
    """
    Generate two images:
    1. Scatter plot of the rotated matrix.
    2. Image with RGB values based on thetas.

    input: matrix
    rotfun: a rotation function (eg. rotX, rotY, rotZ, rotXYZ)
    thetas: a list of rotation angles [i, j, k]
    path: path where you save the generated imgs
    """
    rotmat = rotfun(input, thetas)

    # Define the figure size (in inches) to match the pixel size of the RGB image
    fig_width, fig_height = 6.4, 4.8  # This corresponds to 640x480 pixels with 100 dpi
    dpi = 100

    # Create the figure with the defined size
    fig1 = plt.figure(figsize=(fig_width, fig_height), dpi=dpi)
    ax1 = fig1.add_subplot(111)

    # Similar to crack figure
    ax1.scatter(rotmat[:, 0], rotmat[:, 1], c='k', marker='s')
    ax1.set_xlim(0, 9)
    ax1.set_ylim(-3, 3)
    ax1.set_xticks([])
    ax1.set_yticks([])
    plt.box(False)
    fig1.tight_layout(pad=0)

    # Create the RGB image based on thetas
    img_size = (int(fig_width * dpi), int(fig_height * dpi))  # Size in pixels
    rgb_image = np.zeros((img_size[1], img_size[0], 3), dtype=np.uint8)

    # Normalize theta values to [0, 255] range
    r_value = normalize(thetas[0], 0, 180) if len(thetas) > 0 else 0
    g_value = normalize(thetas[1], 0, 45) if len(thetas) > 1 else 0
    b_value = normalize(thetas[2], -12, 12) if len(thetas) > 2 else 0

    # Fill the image with the RGB values
    rgb_image[:, :] = [r_value, g_value, b_value]

    # Save images
    img_name = "crack"
    if callable(rotfun) and rotfun.__name__ == "rotXYZ":
        for i in thetas:
            img_name += f"_{i}"
    else:
        img_name += f"_{thetas}"
    img_name += ".jpg"
    save_path1 = os.path.join(path, "cracks")
    save_path2 = os.path.join(path, "ebsd")

    if not os.path.exists(save_path1):
        os.makedirs(save_path1, exist_ok=True)
    if not os.path.exists(save_path2):
        os.makedirs(save_path2, exist_ok=True)

    fig1.savefig(os.path.join(save_path1, img_name), format='jpg')
    plt.close(fig1)
    plt.imsave(os.path.join(save_path2, img_name), rgb_image)

if __name__ == "__main__":
    # 生成初始数据点和旋转180°的数据点
    k = 0.15  # 衰减常数
    x = np.linspace(0, 5 * np.pi, 500)
    y = 1.5 * np.sin(2 * x) * np.exp(-k * x)
    z = np.zeros(len(x))
    original_mat = np.vstack((x, y, z)).T

    # 输出不同旋转角得到的xoy面投影图，作为虚拟裂纹
    for i in range(0, 181, 20):
        for j in range(0, 46, 5):
            for k in range(-12, 13, 3):
                img_generator(original_mat, rotfun=rotXYZ, thetas=[i, j, k], path='data/images-unreal')
