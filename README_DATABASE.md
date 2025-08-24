# 毒理学数据库系统 - 数据库设置指南

## 数据库配置

系统使用MySQL数据库直接连接，无需XAMPP。请按照以下步骤设置数据库：

1. 安装MySQL数据库服务器（如果尚未安装），可以参考如下教程：<br>
   [2024 年 MySQL 8.0 安装 配置 教程 最简易（保姆级）](https://blog.csdn.net/m0_52559040/article/details/121843945)<br>
   [MySQL8.0版安装教程 + Workbench可视化配置教程（史上最细、一步一图解）](https://blog.csdn.net/m0_62881487/article/details/133202105)
2. 创建名为`toxics_web`的数据库
3. 在该数据库中创建`total_compound_data`表，包含以下字段：
   - id
   - name
   - iupac_name
   - pubchem_cid
   - canonical_smiles
   - inchikey
   - 其他相关字段

4. 导入CSV数据：可以使用MySQL Workbench或命令行工具将`total_compound_data_utf8_clean.csv`导入到数据库表中

## 配置数据库连接

Flask后端的数据库连接参数在 app.py 文件的DB_CONFIG字典中，您可以根据自己的MySQL设置修改以下参数：

```flask
DB_CONFIG = {
    'host': 'localhost', 
    'user': 'root',
    'password': 'your_pwd',
    'database': 'toxics_web'
}
```

## 导入数据

sql.txt 文件提供了创建表并导入数据的具体命令

## 测试连接

设置完成后，访问`search.html`页面并尝试搜索一些关键词来测试数据库连接是否正常工作。