# 毒理学数据库系统 - 数据库设置指南

## 数据库配置

系统使用MySQL数据库直接连接，无需XAMPP。请按照以下步骤设置数据库：

1. 安装MySQL数据库服务器（如果尚未安装）
2. 创建名为`toxics_web`的数据库
3. 在该数据库中创建`total_compound_data`表，包含以下字段：
   - id
   - name
   - iupac_name
   - pubchem_cid
   - canonical_smiles
   - inchikey
   - 其他相关字段

4. 导入CSV数据：可以使用MySQL Workbench或命令行工具将`total_compound_data.CSV`导入到数据库表中

## 配置数据库连接

数据库连接参数存储在`db_config.php`文件中，您可以根据自己的MySQL设置修改以下参数：

```php
$servername = "localhost"; // MySQL服务器地址
$username = "root";        // MySQL用户名
$password = "";            // MySQL密码
$dbname = "toxics_web";    // 数据库名称
$table = "total_compound_data"; // 表名
```

## 导入数据

可以使用以下SQL命令创建表并导入数据：

```sql
CREATE TABLE total_compound_data (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255),
  iupac_name TEXT,
  pubchem_cid VARCHAR(50),
  canonical_smiles TEXT,
  inchikey VARCHAR(100),
  -- 添加其他必要字段
);

-- 使用LOAD DATA INFILE导入CSV数据
LOAD DATA INFILE 'path_to_csv/total_compound_data.CSV' 
INTO TABLE total_compound_data 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;
```

## 测试连接

设置完成后，访问`search.html`页面并尝试搜索一些关键词来测试数据库连接是否正常工作。