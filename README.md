# TOXICS Webserver 项目总文档

## 项目概述
TOXICS Webserver 是一个药物毒理学性质数据库构建与挖掘系统，提供化合物毒性信息查询、毒性特征搜索和毒性预测等功能。该系统集成了数据库技术、机器学习和 cheminformatics 方法，为药物研发和毒理学研究提供支持。

## 技术栈

### 后端技术
- **Python 3.7+**: 主要编程语言
- **Flask**: 轻量级 Web 框架，处理 HTTP 请求和响应
- **MySQL**: 关系型数据库，存储化合物和毒性数据
- **mysql.connector**: Python 连接 MySQL 数据库的驱动
- **RDKit**: 开源 cheminformatics 工具包，用于分子描述符计算和分子指纹生成
- **scikit-learn**: 机器学习库，用于构建和训练毒性预测模型
- **joblib/pickle**: 模型序列化工具，用于保存和加载训练好的模型
- **python-dotenv**: 环境变量管理工具

### 前端技术
- **HTML5/CSS3**: 网页结构和样式
- **JavaScript**: 前端交互逻辑

## 文件结构与说明

### 根目录文件
- **.env**: 环境变量配置文件，包含数据库连接信息（DB_HOST, DB_USER, DB_PASSWORD 等）
- **README_DATABASE_CLOUD.md**: 云数据库配置说明
- **README_DATABASE_LOCALHOST.md**: 本地数据库配置说明
- **README.md**: 项目总文档
- **app.py**: Web 应用主入口文件，包含路由定义和业务逻辑
- **requirements.txt**: 项目依赖包列表
- **styles.css**: 全局 CSS 样式文件
- **sql.txt**: 数据库 SQL 脚本
- **toxicity_prediction.py**: 毒性预测模块，包含分子描述符计算和模型预测功能
- **total_compound_data.CSV**: 化合物数据 CSV 文件（原始数据）
- **total_compound_data.xlsx**: 化合物数据 Excel 文件（原始数据）
- **total_compound_data_utf8_clean.csv**: 清洗后的 UTF-8 编码化合物数据 CSV 文件

### 文件夹结构

#### eToxPred/
- **etoxpred_best_model.joblib**: 预训练的 eToxPred 毒性预测模型
- **etoxpred_predict.py**: eToxPred 模型预测脚本
- **fpscores.pkl.gz**: 分子指纹分数数据
- **sascore.py**: 合成可访问性评分计算脚本

#### models/
各种预训练的毒性预测模型
- **cardiotoxicity_model.pkl**: 心脏毒性预测模型
- **cardiotoxicity_scaler.pkl**: 心脏毒性特征标准化器
- **feature_names.pkl**: 特征名称列表
- **general_toxicity_model.pkl**: 一般毒性预测模型
- **general_toxicity_scaler.pkl**: 一般毒性特征标准化器
- **hepatotoxicity_model.pkl**: 肝毒性预测模型
- **hepatotoxicity_scaler.pkl**: 肝毒性特征标准化器
- **mutagenicity_model.pkl**: 致突变性预测模型
- **mutagenicity_scaler.pkl**: 致突变性特征标准化器

#### templates/
HTML 模板文件
- **data_collection.html**: 数据收集页面
- **search.html**: 搜索页面
- **search_result.html**: 搜索结果页面
- **toxicity_prediction.html**: 毒性预测页面
- **toxicity_result.html**: 毒性结果页面
- **toxicity_search.html**: 毒性搜索页面
- **toxics.html**: 主页模板

## 核心功能模块

### 1. 数据库查询模块 (app.py)
- **首页路由** (`/`): 渲染主页
- **搜索路由** (`/search`): 渲染搜索页面
- **毒性搜索路由** (`/toxicity_search`): 渲染毒性搜索页面
- **搜索结果路由** (`/search_result`): 处理搜索请求并返回结果
- **毒性结果路由** (`/toxicity_result`): 处理毒性特征搜索并返回结果
- **下载路由** (`/download_toxicity_results`): 下载搜索结果

### 2. 毒性预测模块 (toxicity_prediction.py)
- **分子描述符计算** (`calculate_molecular_descriptors`): 计算化合物的各种分子描述符
- **模型训练** (`train_toxicity_models`): 训练多种毒性预测模型（随机森林）
- **毒性预测** (`predict_toxicity`): 调用 eToxPred 模型进行毒性预测
- **eToxPred 预测** (`predict_etoxpred`): 使用预训练的 eToxPred 模型进行毒性预测
- **SMI 文件处理** (`process_smi_file`): 批量处理 SMI 文件中的化合物并预测毒性

## 环境配置
1. 安装依赖包: `pip install -r requirements.txt`
2. 配置 .env 文件，设置数据库连接信息
3. 初始化数据库: 运行 sql.txt 中的 SQL 脚本
4. 启动应用: `python app.py`

## 数据流程
1. 用户通过网页界面输入搜索条件或化合物结构
2. 后端接收请求，查询数据库或进行毒性预测
3. 返回结果给前端，用户在网页上查看或下载结果

## 注意事项
- 确保 .env 文件中的数据库配置正确
- 首次运行需初始化数据库
- 毒性预测模型可能需要根据实际数据进行重新训练以提高准确性
- 处理大量数据时可能需要优化数据库查询性能