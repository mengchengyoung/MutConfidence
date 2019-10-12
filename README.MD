# 突变可信度打分模型
一般步骤 1.生成训练数据 -> 2.训练模型 -> 3.输入突变位点vcf文件输出可信度  
默认模型为神经网络，也有逻辑回归模型可以选用，自定义训练模型文件放在lib/model/model/文件夹下，并继承_base.py文件。  
example：  
1.根据正负样本生成训练数据：  
python3 Mutconfidence.py Generate -p 正样本文件夹 -n 负样本文件夹 -o 训练数据输出路劲  

2.训练模型  
python Mutconfidence.py Train -i 训练数据，csv格式  -m 指定模型，默认为深度神经网络 -o 模型输出路径  

3.突变可信度打分  
python Mutconfidence.py Predict -i 突变vcf文件  


