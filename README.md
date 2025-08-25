# TOXICS —— 化合物 / 毒理学数据库系统

这个系统允许用户将CSV数据导入到MySQL数据库，并通过Web界面根据不同字段查询化合物信息。

## 功能特点

- 将CSV数据导入MySQL数据库
- 支持通过多种字段查询化合物信息：
  - ID
  - Name（名称）
  - IUPAC Name（IUPAC名称）
  - PubChem CID
  - Canonical SMILES
  - InChIKey
- 美观的用户界面，与现有网站风格一致
- 响应式设计，适配不同设备

## 使用说明

### 1. 导入数据到数据库

在使用搜索功能前，需要先将CSV数据导入到MySQL数据库中：

1. 确保MySQL服务已启动
2. 修改`.env`文件中的数据库连接信息
3. 在浏览器中访问 http://192.168.0.100:5000/ 
4. 等待导入完成，页面会显示导入结果

### 2. 使用搜索功能

1. 在浏览器中访问`search.html`
2. 从下拉菜单中选择要搜索的字段（ID、Name、IUPAC Name等）
3. 在搜索框中输入关键词
4. 点击"搜索"按钮
5. 查看搜索结果

## 文件说明

- `search.html` - 搜索界面
- `search_result.php` - 处理搜索请求并显示结果
- `import_data.php` - 将CSV数据导入到MySQL数据库
- `total_compound_data.CSV` - 包含化合物数据的CSV文件
- `styles.css` - 样式表文件

## 技术要求

- MySQL 5.7+
- Aiven 云数据库

## 注意事项

- 请确保修改.env文件中的数据库连接信息（用户名和密码）
- 导入大型CSV文件可能需要较长时间，请耐心等待
- 对于SMILES和IUPAC名称等长文本，搜索时建议使用准确的关键词

## 联系方式

wanghaotian70094 [at] foxmail.com
