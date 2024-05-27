# -*- coding: utf-8 -*-
# 2024/5/8 本脚本用于批量处理光滑晶界模型

from abaqus import *
from abaqusConstants import *
from caeModules import *
from driverUtils import executeOnCaeStartup
import numpy as np

executeOnCaeStartup()

def getEdgeNodeId(path, height, width):
    """Return the node ID of top, bottom, left, and right edges of the model"""
    node_info_path = os.path.join(path, "node_info.csv")
    node_info = np.genfromtxt(node_info_path, delimiter=',')

    top_edge = []
    bottom_edge = []
    left_edge = []
    right_edge = []

    for row in node_info:
        if row[2] == height:
            top_edge.append(int(row[0]))
        elif row[2] == 0.0:
            bottom_edge.append(int(row[0]))
        elif row[1] == 0.0:
            left_edge.append(int(row[0]))
        elif row[1] == width:
            right_edge.append(int(row[0]))
        else:
            continue
        
    return top_edge, bottom_edge, left_edge, right_edge

def main(rootPath, modelName):
    inputFileName = os.path.join(rootPath, modelName + ".inp")   
    mdb.ModelFromInputFile(name=modelName, inputFileName=inputFileName)
    model = mdb.models[modelName]
    height, width = 1.0, 1.5 # 模型尺寸

    # 创建裂纹部件
    s = model.ConstrainedSketch(name='__profile__', sheetSize=1.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.Line(point1=(0.0, height/2.0), point2=(0.2, height/2.0))
    s.HorizontalConstraint(entity=g[2], addUndoState=False)
    p = model.Part(name='Crack', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
    p = model.parts['Crack']
    p.BaseWire(sketch=s)
    s.unsetPrimaryObject()
    del model.sketches['__profile__']

    # 实例化部件
    a = model.rootAssembly
    a.Instance(name='Crack-1', part=p, dependent=ON)
    p = model.parts['NOTCHED']
    a.Instance(name='NOTCHED-1', part=p, dependent=ON)
    # a.translate(instanceList=('Crack-1', ), vector=(0, 0.5, 0.0))

    # 创建接触属性
    model.ContactProperty('IntProp-1')
    model.interactionProperties['IntProp-1'].NormalBehavior(
        pressureOverclosure=LINEAR, contactStiffness=1.0, 
        constraintEnforcementMethod=DEFAULT)

    # 创建XFEM裂纹
    e1 = a.instances['NOTCHED-1'].elements
    elements1 = e1[:]
    crackDomain = regionToolset.Region(elements=elements1)
    e1 = a.instances['Crack-1'].edges
    # edges1 = e1.findAt(((0.05, 0.5125, 0.0), ))
    # crackLocation = regionToolset.Region(edges=edges1)
    crackLocation = regionToolset.Region(edges=e1)
    a.engineeringFeatures.XFEMCrack(name='Crack-1', crackDomain=crackDomain, 
        interactionProperty='IntProp-1', crackLocation=crackLocation)

    # 创建XFEM裂纹相互作用
    model.XFEMCrackGrowth(name='Int-1', createStepName='Initial', crackName='Crack-1')

    # 创建分析步
    model.StaticStep(name='Step-1', 
        previous='Initial', timePeriod=10.0, maxNumInc=10000, initialInc=0.0001, 
        minInc=1e-08, maxInc=1.0, nlgeom=ON)

    # 编辑分析步
    model.steps['Step-1'].control.setValues(
        allowPropagation=OFF, resetDefaultValues=OFF, discontinuous=ON, 
        timeIncrementation=(8.0, 10.0, 9.0, 16.0, 10.0, 4.0, 12.0, 25.0, 6.0, 3.0, 
        50.0))

    # 编辑场输出和历程输出
    model.fieldOutputRequests['F-Output-1'].setValues(
        variables=('S', 'U', 'RF', 'CF', 'CSTRESS', 'CDISP', 'PHILSM', 
        'STATUSXFEM'), frequency=20)
    model.historyOutputRequests['H-Output-1'].setValues(
        frequency=20)

    # 设置载荷幅值
    model.TabularAmplitude(name='Amp-1', 
        timeSpan=TOTAL, smooth=SOLVER_DEFAULT, data=((0.0, 0.0), (0.5, 1.0), (1.0, 
        0.0)))

    # 获取模型各边节点ID
    n1 = a.instances['NOTCHED-1'].nodes
    top_edge, bottom_edge, left_edge, right_edge = getEdgeNodeId(rootPath, height, width)
    
    # 设置边界条件1-右边x方向固定
    nodes1 = None
    for i in right_edge:
        if nodes1 is None:
            nodes1 = n1[i-1:i]
        else:
            nodes1 = nodes1 + n1[i-1:i]
    region = regionToolset.Region(nodes=nodes1)
    model.DisplacementBC(name='BC-1', 
        createStepName='Initial', region=region, u1=SET, u2=UNSET, ur3=UNSET, 
        amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)

    # 设置边界条件2-上边循环载荷
    nodes1 = None
    for i in top_edge:
        if nodes1 is None:
            nodes1 = n1[i-1:i]
        else:
            nodes1 = nodes1 + n1[i-1:i]
    region = regionToolset.Region(nodes=nodes1)
    model.DisplacementBC(name='BC-2', 
        createStepName='Step-1', region=region, u1=UNSET, u2=0.00025, ur3=UNSET, 
        amplitude='Amp-1', fixed=OFF, distributionType=UNIFORM, fieldName='', 
        localCsys=None)

    # 设置边界条件3-下边循环载荷
    nodes1 = None
    for i in bottom_edge:
        if nodes1 is None:
            nodes1 = n1[i-1:i]
        else:
            nodes1 = nodes1 + n1[i-1:i]
    region = regionToolset.Region(nodes=nodes1)
    model.DisplacementBC(name='BC-3', 
        createStepName='Step-1', region=region, u1=UNSET, u2=-0.00025, ur3=UNSET, 
        amplitude='Amp-1', fixed=OFF, distributionType=UNIFORM, fieldName='', 
        localCsys=None)

    # 创建Job
    mdb.Job(name='Job-1', model=modelName, description='', 
        type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, 
        memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, numThreadsPerMpiProcess=1, 
        multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)

    # 输出inp文件
    mdb.jobs['Job-1'].writeInput(consistencyChecking=OFF)

    # 保存cae
    # mdb.saveAs(pathName='D:/CrackImage/PolyFEM/neper/12-GIV/getAutoScript/origin')

if __name__ == '__main__':
    import os
    import json

    with open('config.json', 'r') as f:
        config = json.load(f)
    root_path = str(config.get('root_path'))

    # For multiple cases:
    for wp_name in ["wp{:03d}".format(i) for i in range(11,21,1)]:
        os.chdir(root_path)
            
        wp_path = os.path.join(root_path, wp_name)
        model_name = "poly_quad_modified"

        if not os.path.exists(wp_name):
            os.makedirs(wp_name)
        os.chdir(os.path.join(root_path, wp_name))

        main(wp_path, model_name)