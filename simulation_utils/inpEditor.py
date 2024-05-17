import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei'] # 用来正常显示中文标签SimHei
plt.rcParams['axes.unicode_minus'] = False # 用来正常显示负号

IN718 = np.array([
   242180.,   138850.,   104200.,        0.,        0.,        0.,        0.,        0.,
        0.,        0.,        0.,        0.,        0.,        0.,        0.,        0.,
        0.,        0.,        0.,        0.,        0.,        0.,        0.,        0.,
        1.,        0.,        0.,        0.,        0.,        0.,        0.,        0.,
        1.,        1.,        1.,        1.,        1.,        0.,        0.,        0.,
        0.,        0.,        0.,        0.,        0.,        0.,        0.,        0.,
        0.,        0.,        0.,        0.,        0.,        0.,        0.,        0.,
        0.,        0.,        1.,        0.,        0.,        1.,        0.,        0.,
        1.,        0.,        0.,        1.,        0.,        0.,        0.,        0.,
       10.,   0.00001,        0.,        0.,        0.,        0.,        0.,        0.,
        0.,        0.,        0.,        0.,        0.,        0.,        0.,        0.,
        0.,        0.,        0.,        0.,        0.,        0.,        0.,        0.,
     5800.,      120.,      151.,        0.,        0.,        0.,        0.,        0.,
       1.9,       1.9,        0.,        0.,        0.,        0.,        0.,        0.,
        0.,        0.,        0.,        0.,        0.,        0.,        0.,        0.,
        0.,        0.,        0.,        0.,        0.,        0.,        0.,        0.,
        0.,        0.,        0.,        0.,        0.,        0.,        0.,        0.,
        0.,        0.,        0.,        0.,        0.,        0.,        0.,        0.,
       0.5,        1.,        0.,        0.,        0.,        0.,        0.,        0.,
        1.,       10.,     1e-05,        0.,        0.,        0.,        0.,        0.
        ]).reshape(-1,8)

# 旋转矩阵-绕x轴旋转
def rotX(original_mat, theta):
    """rotate the input matrix about x axis with theta."""
    # assert len(theta) == 1, f"Only 1 rotation angle is expected! Please check you input!"
    theta_rad = np.radians(theta)
    rotmat = np.array([[1,0,0],
                       [0,np.cos(theta_rad),-np.sin(theta_rad)],
                       [0,np.sin(theta_rad),np.cos(theta_rad)]])
    return np.dot(rotmat,original_mat.T).T

# 旋转矩阵-绕y轴旋转
def rotY(original_mat, theta):
    """rotate the input matrix about y axis with theta."""
    # assert len(theta) == 1, f"Only 1 rotation angle is expected! Please check you input!"
    theta_rad = np.radians(theta)
    rotmat = np.array([[np.cos(theta_rad),0,np.sin(theta_rad)],
                       [0,1,0],
                       [-np.sin(theta_rad),0,np.cos(theta_rad)]])
    return np.dot(rotmat,original_mat.T).T

# 旋转矩阵-绕z轴旋转
def rotZ(original_mat, theta):
    """rotate the input matrix about z axis with theta."""
    # assert len(theta) == 1, f"Only 1 rotation angle is expected! Please check you input!"
    theta_rad = np.radians(theta)
    rotmat = np.array([[np.cos(theta_rad),-np.sin(theta_rad),0],
                       [np.sin(theta_rad),np.cos(theta_rad),0],
                       [0,0,1]])
    return np.dot(rotmat,original_mat.T).T

# 旋转矩阵-绕zxz轴旋转
def eulerRot(original_mat, eulerAngles):
    assert len(eulerAngles) == 3, f"3 euler angles are expected! Please check you input."
    funcList = [rotZ, rotX, rotZ]
    rotated_mat = None
    for i in reversed(range(len(eulerAngles))):
        if rotated_mat is None:
            rotated_mat = funcList[i](original_mat, eulerAngles[i])
        else:
            rotated_mat = funcList[i](rotated_mat, eulerAngles[i])
    return rotated_mat

# 从inp获取晶粒数量
def getGrainInfo(content, getGrainID=False):
    '''
    content: content of input file
    getGrainID: if true, also return grain ID
    '''
    grainN = -1
    lines = content.split('\n')

    if getGrainID:
        grainID = []
        for line in lines:
            if "*ELEMENT, type=CPS4, ELSET=Surface" in line:
                grainID.append(int(line.split("face")[1]))
        grainN = len(grainID)

        print(f"Num of Grains: {grainN}")
        return grainN, grainID
    
    else:
        for line in reversed(lines):
            if "*ELEMENT, type=CPS4, ELSET=Surface" in line:
                grainN = int(line.split("face")[1])
                break

        print(f"Num of Grains: {grainN}")    
        return grainN
    
# 从inp获取单元数量
def getElementN(content_lines):
    """A temporary function to get the total number of elements"""
    elementN = content_lines[-2].split(",")[0]
    return int(elementN)

# 获取随机晶体取向
def getRandomOrientation(grainN, seed=42):
    np.random.seed(seed)
    id = np.arange(1, grainN+1, 1).reshape((grainN, 1))
    phi1 = np.random.uniform(0, 360, size=(grainN, 1))
    Phi = np.random.uniform(0, 55, size=(grainN, 1))
    phi2 = np.random.uniform(0, 90, size=(grainN, 1))

    ori = pd.DataFrame(np.concatenate((id, phi1, Phi, phi2), axis=1), columns=['ID', 'Phi1', 'Phi', 'Phi2']).astype({'ID': int})

    return ori

# 修改part的名称
def addPartName(content, name):
    '''
    content: input file content
    name: name of part
    '''
    content_lines = content.split('\n')
    new_content = f"\n*Part, name={name}\n"
    for i, line in enumerate(content_lines):
        if line.strip().upper().startswith("*PART, NAME="):
            content_lines[i] = f"*Part, name={name}"
            break
        if line.strip().upper() == "*NODE":
            content_lines.insert(i, new_content)
            break
    return '\n'.join(content_lines)


def adjustElement(content):
    """删除T3D2单元以及调整单元节点编号和顺序"""
    start_line = "*ELEMENT, type=T3D2, ELSET=Line1"
    end_line = "*ELEMENT, type=CPS4, ELSET=Surface1"
    content_lines = content.split('\n')

    # 初始化开始和结束索引
    start_index = None
    end_index = None
    start_line2 = 0

    # 查找开始和结束行的索引
    for i, line in enumerate(content_lines):
        if start_line == line:
            start_index = i
        elif end_line == line:
            end_index = i
            break

    # 重新编号数字行的第一个数字，并交换每行的第二个和第四个数字
    def adjust_line(line, order):
        elements = line.split(',')
        elements[0] = str(int(order))  # 重新编号，假设编号从1开始
        elements[1], elements[3] = elements[3], elements[1]  # 交换第二个和第四个数字
        return ','.join(elements)
    
    order = 1

    for i in range(end_index, len(content_lines)):
        if content_lines[i].startswith("*ELEMENT, type=CPS4, ELSET="):
            continue
        else:
            if content_lines[i].strip():
                content_lines[i] = adjust_line(content_lines[i], order)
                order = order + 1

    # 如果找到了开始和结束行，删除这两行之间的内容
    if start_index is not None and end_index is not None:
        del content_lines[start_index:end_index]
    
    # 将修改后的内容重新组合成字符串并返回
    return '\n'.join(content_lines)


def addSectionMaterial(content, depvar, material, orientations):
    '''
    content: input file content
    depvar: number of dependent variables
    material: material property matrix
    orientations: a pandas table of euler angles
    '''
    # Remove "*End Part" line if exists
    content_lines = content.split('\n')
    if "*End Part" in content_lines[-2]:
        content = '\n'.join(content_lines[:-2])

    # Set index for orientations DataFrame
    orientations.set_index('ID', inplace=True)

    # Get valid grain ID
    _, grainID = getGrainInfo(content, getGrainID=True)

    # Get number of element
    elementN = getElementN(content_lines)

    # Create a list to store section contents
    section_contents = [
        # f"\n** Section: Section-{i}\n*Solid Section, elset=face{i}, material=Material-{i}\n,"
        f"\n** Section: Section-{i}\n*Solid Section, elset=Surface{i}, material=Material-{i}\n,"
        for i in grainID
    ]

    # Concatenate section contents
    content += ''.join(section_contents)

    # Add "*End Part" line
    content += "\n*End Part\n"

    # Create a list to store material contents
    material_contents = ["\n**\n** MATERIALS\n**"]

    for i in grainID:
        # Prepare material content
        material_content = [
            f"*Material, name=Material-{i}",
            f"*Damage Initiation, criterion=MAXPS",
            f"{1000}.,",
            f"*Damage Evolution, type=ENERGY",
            f"{0.29745},",
            f"*Damage Stabilization",
            f"{1e-05}",
            f"*Depvar",
            f"    {depvar},"
        ]
    
        # Modify orientation
        eulers = orientations.loc[i, ['Phi1', 'Phi', 'Phi2']].values
        mat = np.copy(material)
        for index in [7,8]:
            mat[index,3:6] = np.round(eulerRot(mat[index,0:3], eulers),6)

        # Create a new row with euler angles and other information
        new_row = np.concatenate((eulers, [elementN, 0., 0., 0., 0.]))
        new_row[:3] = np.round(new_row[:3], 2)
        
        # Add the new row to the material matrix
        mat = np.vstack([mat, new_row])

        material_content.append("*User Material, constants=" + str(np.size(mat)))
        material_content.extend([",".join(f"{el:>10}" for el in row) for row in mat])
        material_contents.extend(material_content)

    # Join material contents
    content += '\n'.join(material_contents)

    return content

# 向inp添加solid section和材料信息
def inpModifier(src, new, material=IN718, part_name="Tess", ori=None, random_ori=True, depvar=150):
    '''
    src: inp path
    new: save path
    material: material property matrix
    part_name: name of part
    ori: a pandas table of euler angles
    random_ori: if take random orientations or not
    depvar: number of dependent variables
    '''
    with open(src, 'r') as srcFile:
        content = srcFile.read()
    
    if random_ori:
        grainN = getGrainInfo(content)
        ori = getRandomOrientation(grainN)
    else:
        if ori is None:
            raise ValueError("Grain orientations are not provided!")
            
    # 修改inp文件
    modified_content = adjustElement(content)
    modified_content = addPartName(modified_content, part_name)
    modified_content = addSectionMaterial(modified_content, depvar, material, ori)

    # 保存修改后的inp文件
    with open(new, 'w') as new_file:
        new_file.write(modified_content)


# -------------------------------------------------------------------
# 执行preprocessing.py后再执行以下部分
def modifyDamage(src, new, cl, n_properties=1, properties=[1e-10]):
    """统一修改损伤判据"""
    with open(src, 'r', encoding='latin-1') as srcFile:
        content = srcFile.readlines()

    modified_content = []
    skip_next_line = False
    index = 1 # index for cl when cl is a dict

    if isinstance(cl, dict):
        for line in content:
            if "*Damage Initiation" in line:
                modified_content.append(
                    f"*Damage Initiation, criterion=USER, failure mechanisms=1, properties={n_properties}\n{','.join(str(x) for x in properties)},\n")
                skip_next_line = True
            elif "*Damage Evolution" in line:
                modified_content.append(
                    f"*Damage Evolution, type=ENERGY, failure index=1\n {59.49 * cl[index]:.4f},\n")
                skip_next_line = True
                index += 1
            elif skip_next_line:
                skip_next_line = False
            else:
                modified_content.append(line)
    else:
        for line in content:
            if "*Damage Initiation" in line:
                modified_content.append(
                    f"*Damage Initiation, criterion=USER, failure mechanisms=1, properties={n_properties}\n{','.join(str(x) for x in properties)},\n")
                skip_next_line = True
            elif "*Damage Evolution" in line:
                modified_content.append(
                    f"*Damage Evolution, type=ENERGY, failure index=1\n {59.49 * cl:.4f},\n")
                skip_next_line = True
            elif skip_next_line:
                skip_next_line = False
            else:
                modified_content.append(line)

    with open(new, 'w', encoding='utf-8') as newFile:
        newFile.writelines(modified_content)

def modifyDepvar(src, new, depvar=150):
    """统一修改依赖解的状态变量"""
    with open(src, 'r', encoding='latin-1') as srcFile:
        content = srcFile.readlines()
    
    modified_content = []
    skip_next_line = False

    for line in content:
        if "*Depvar" in line:
            modified_content.append(f"*Depvar\n    {depvar},\n")
            skip_next_line = True
        elif skip_next_line:
            # Skip the next line as it has already been added in the modified content
            skip_next_line = False
        else:
            modified_content.append(line)

    with open(new, 'w', encoding='utf-8') as newFile:
        newFile.writelines(modified_content)

def modifyStep(src, new, initial_increment=0.0001, step_time=1, min_increment=1e-08, max_increment=1):
    '''统一修改分析步'''
    with open(src, 'r') as file:
        lines = file.readlines()

    modified_content = []
    skip_next_line = False

    for line in lines:
        if "*Static" in line:
            modified_content.append(f"*Static\n{initial_increment},{step_time},{min_increment},{max_increment}\n")
            skip_next_line = True
        elif skip_next_line:
            skip_next_line = False
        else:
            modified_content.append(line)

    with open(new, 'w', encoding='utf-8') as newFile:
        newFile.writelines(modified_content)

def addAmplitude(bottom, top, width, cycN, print=True):
    '''生成幅值'''
    ampContent = f"*Amplitude, name=Amp-1, time=TOTAL TIME\n"

    ampTable = np.zeros((2*(cycN+1),2))
    t0 = width*bottom/(2*(1-bottom))
    for i in range(2*cycN+1):
        ampTable[i+1,0] = t0 + 1/2 * width * i
        if i%2 == 0:
            ampTable[i+1,1] = bottom
        else:
            ampTable[i+1,1] = top

    if print:
        plt.plot(ampTable[:,0], ampTable[:,1])

    ampTable = ampTable.reshape((ampTable.size))
    flag = 0
    for i in ampTable:
        if flag==8:
            ampContent = ampContent.rstrip(',')
            ampContent += f"\n"
            flag=0
        ampContent += f"{round(i,4)},"
        flag += 1
    ampContent += f"\n"
    # content += ampContent
    return ampContent

def modifyAmplitude(src, new, ampContent):
    '''统一修改幅值'''
    # 打开原始文件
    with open(src, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 创建一个新的列表来存储修改后的内容
    amplitude_index = None
    section_end_index = None

    # 遍历每一行，检查是否包含"*Amplitude"
    for i, line in enumerate(lines):
        if '*Amplitude' in line:
            amplitude_index = i  # 记录含有"*Amplitude"的行的索引
        if '**' in line and amplitude_index is not None:
            section_end_index = i  # 记录下一个"**"的行的索引
            break  # 找到后即退出循环

    # 如果找到了含有"*Amplitude"的行
    if amplitude_index is not None and section_end_index is not None:
        # 删除从"*Amplitude"到下一个"**"的内容
        del lines[amplitude_index:section_end_index]
        # 在"*Amplitude"的位置插入新内容
        lines.insert(amplitude_index, ampContent)

    # 将修改后的内容写回到文件中
    with open(new, 'w', encoding='utf-8') as file:
        file.writelines(lines)