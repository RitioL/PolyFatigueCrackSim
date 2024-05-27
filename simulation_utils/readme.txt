具体操作流程如下：

前处理：
1.运行scriptGenerator.py
    Note：此脚本生成多晶模型批量生成脚本neper.sh和abaqus运算起始脚本startup.bat
2.在Ubuntu命令行更改目录到neper.sh所在目录，然后输入以下命令：./neper.sh
    Note：不同系统的换行符不同，可能导致编写脚本运行出错。scriptGenerator.py已解决相关问题。若有需要可在Ubuntu命令行下转换：sed -i 's/\r$//' neper.sh
3.运行editInp1.py
    Note：为inp文件增加等材料信息
4.运行preprocessor.py
    Note：完成分析步、边界条件等各类仿真参数的设置
5.运行editInp2.py
    Note：批量修改部分参数

运行：
6.运行startup.bat
    Note：Abaqus批量提交脚本

后处理：
7.运行postprocessor1.py
    Note：提取节点上的philsm值用于绘制裂纹
8.运行postprocessor2.py
    Note：绘制EBSD和Crack图并保存
9.运行postprocessor3.py
    Note：逐个筛选，抽取不同帧的结果

UMAT说明:
subroutines.for是原版子程序
subroutines2.for在原版基础上增加了非局域方法（non-local method）
subroutines3.for在原版基础上增加了早停机制（early-stopping method）