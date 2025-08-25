# 毒理学数据库系统 - 数据库设置指南（云端部署版）

## 数据库配置

云端数据库使用 aiven (https://console.aiven.io/) ,请按照以下步骤设置数据库：

1. 在本地安装MySQL数据库服务器（如果尚未安装），可以参考 README_DATABASE_LOCALHOST.md 文件

2. 注册账号（需要科学上网），选择服务器类型为 mysql，具体可参考教程：[使用aiven免费获取云端数据库并添加到SrpingBoot项目中](https://www.ergoutreegal.cn/posts/36378.html)

3. 点击左侧菜单栏 Overview ，点击右侧面板上的 Quick Connect， 复制指令如下：<br>
   mysql --user avnadmin --password=***** --host mysql-toxics-project-toxics.i.aivencloud.com --port 10159 defaultdb

   注意：最后的 defaultdb 可以选择你创建的其他数据库，这里需要提前创建一个名为 toxics_web 的数据库，在左侧菜单栏点击 Databases，再点击右侧的 Create database 即可

4. 将数据导出为 .sql 数据库文件，在 mysql 命令行中使用以下指令导入数据<br>
   ```sql
   source /path/to/your_data.sql;
   ```
    
 注意：路径不要带双引号，windows系统下需要使用"\\"或"/"

## 配置数据库连接

Flask后端的数据库连接参数 .env 文件中，您可以根据 Overview -> Connection Information 中的设置修改以下参数：

```env
DB_HOST=*****
DB_USER=avnadmin
DB_PASSWORD=*****
DB_NAME=toxics_web
DB_PORT=*****
```

## 测试连接

设置完成后，访问`search.html`页面并尝试搜索一些关键词来测试数据库连接是否正常工作。