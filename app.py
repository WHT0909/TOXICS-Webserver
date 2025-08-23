from flask import Flask, render_template, request, send_file, make_response
from flask import Flask, request, render_template, jsonify
import mysql.connector
import re
import csv
import io
import os
import tempfile
from werkzeug.utils import secure_filename
from toxicity_prediction import predict_toxicity, process_smi_file

app = Flask(__name__, static_folder='.', static_url_path='')

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345',
    'database': 'toxic_web'
}

# 固定表名（移出DB_CONFIG）
TABLE_NAME = 'toxics_main_table'

# 排除不分析的列
EXCLUDE_COLUMNS = {'ID', 'Name', 'IUPAC_Name', 'PubChem_CID', 
                  'Canonical_SMILES', 'InChIKey'}

# 毒性特征字段显示名称映射
TOXICITY_FIELD_DISPLAY = {
    'ToxCast_Tox21_Assay': 'ToxCast&Tox21 Assay',
    'Ecotoxicity_LC50DM': '生态毒性 - LC50DM',
    'Ecotoxicity_LC50': '生态毒性 - LC50',
    'Ecotoxicity_IGC50': '生态毒性 - IGC50',
    'Ecotoxicity_BCF': '生态毒性 - BCF',
    'Clinical_Toxicity_Clinical_toxicity': '临床毒性',
    'Hepatotoxicity_Hepatotoxicity': '肝毒性',
    'Cardiotoxicity_Cardiotoxicity_1': '心脏毒性-1',
    'Cardiotoxicity_Cardiotoxicity_5': '心脏毒性-5',
    'Cardiotoxicity_Cardiotoxicity_10': '心脏毒性-10',
    'Cardiotoxicity_Cardiotoxicity_30': '心脏毒性-30',
    'Respiratory_Toxicity_Respiratory_Toxicity': '呼吸毒性',
    'Endocrine_Disruption_NR_AR_LBD': '内分泌干扰 - NR-AR-LBD',
    'Endocrine_Disruption_NR_AR': '内分泌干扰 - NR-AR',
    'Endocrine_Disruption_NR_AhR': '内分泌干扰 - NR-AhR',
    'Endocrine_Disruption_NR_aromatase': '内分泌干扰 - NR-芳香酶',
    'Endocrine_Disruption_NR_ER_LBD': '内分泌干扰 - NR-ER-LBD',
    'Endocrine_Disruption_NR_ER': '内分泌干扰 - NR-ER',
    'Endocrine_Disruption_SR_ATAD5': '内分泌干扰 - SR-ATAD5',
    'Endocrine_Disruption_SR_HSE': '内分泌干扰 - SR-HSE',
    'Endocrine_Disruption_NR_PPAR_gamma': '内分泌干扰 - NR-PPAR-γ',
    'Endocrine_Disruption_SR_MMP': '内分泌干扰 - SR-MMP',
    'Endocrine_Disruption_SR_p53': '内分泌干扰 - SR-p53',
    'Endocrine_Disruption_SR_ARE': '内分泌干扰 - SR-ARE',
    'Irritation_and_Corrosion_Eye_Irritation': '刺激和腐蚀 - 眼睛刺激',
    'Irritation_and_Corrosion_Eye_Corrosion': '刺激和腐蚀 - 眼睛腐蚀',
    'Carcinogenicity_Carcinogenicity': '致癌性',
    'Mutagenicity_Ames_Mutagenicity': '致突变性 - Ames',
    'Developmental_and_Reproductive_Toxicity_Developmental_Toxicity': '发育和生殖毒性 - 发育毒性',
    'Developmental_and_Reproductive_Toxicity_Reproductive_Toxicity': '发育和生殖毒性 - 生殖毒性',
    'CYP450': 'CYP450',
    
    # Acute toxicity fields
    'Acute_mammal_species_unspecified_intraperitoneal_LD50': '急性毒性 - 哺乳动物(未指定)腹腔注射LD50',
    'Acute_Toxicity_guinea_pig_intraperitoneal_LD50': '急性毒性 - 豚鼠腹腔注射LD50',
    'Acute_Toxicity_mouse_intraperitoneal_LD50': '急性毒性 - 小鼠腹腔注射LD50',
    'Acute_Toxicity_rat_intraperitoneal_LD50': '急性毒性 - 大鼠腹腔注射LD50',
    'Acute_Toxicity_rabbit_intraperitoneal_LD50': '急性毒性 - 兔腹腔注射LD50',
    'Acute_Toxicity_mouse_intraperitoneal_LDLo': '急性毒性 - 小鼠腹腔注射LDLo',
    'Acute_Toxicity_rat_intraperitoneal_LDLo': '急性毒性 - 大鼠腹腔注射LDLo',
    'Acute_Toxicity_mouse_intravenous_LD50': '急性毒性 - 小鼠静脉注射LD50',
    'Acute_Toxicity_guinea_pig_intravenous_LD50': '急性毒性 - 豚鼠静脉注射LD50',
    'Acute_Toxicity_rat_intravenous_LD50': '急性毒性 - 大鼠静脉注射LD50',
    'Acute_Toxicity_rabbit_intravenous_LD50': '急性毒性 - 兔静脉注射LD50',
    'Acute_Toxicity_dog_intravenous_LD50': '急性毒性 - 狗静脉注射LD50',
    'Acute_Toxicity_cat_intravenous_LD50': '急性毒性 - 猫静脉注射LD50',
    'Acute_Toxicity_mouse_intravenous_LDLo': '急性毒性 - 小鼠静脉注射LDLo',
    'Acute_Toxicity_guinea_pig_intravenous_LDLo': '急性毒性 - 豚鼠静脉注射LDLo',
    'Acute_Toxicity_rat_intravenous_LDLo': '急性毒性 - 大鼠静脉注射LDLo',
    'Acute_Toxicity_rabbit_intravenous_LDLo': '急性毒性 - 兔静脉注射LDLo',
    'Acute_Toxicity_dog_intravenous_LDLo': '急性毒性 - 狗静脉注射LDLo',
    'Acute_Toxicity_cat_intravenous_LDLo': '急性毒性 - 猫静脉注射LDLo',
    'Acute_Toxicity_mouse_oral_LD50': '急性毒性 - 小鼠口服LD50',
    'Acute_Toxicity_mammal_species_unspecified_oral_LD50': '急性毒性 - 哺乳动物(未指定)口服LD50',
    'Acute_Toxicity_guinea_pig_oral_LD50': '急性毒性 - 豚鼠口服LD50',
    'Acute_Toxicity_rat_oral_LD50': '急性毒性 - 大鼠口服LD50',
    'Acute_Toxicity_rabbit_oral_LD50': '急性毒性 - 兔口服LD50',
    'Acute_Toxicity_dog_oral_LD50': '急性毒性 - 狗口服LD50',
    'Acute_Toxicity_cat_oral_LD50': '急性毒性 - 猫口服LD50',
    'Acute_Toxicity_bird_wild_oral_LD50': '急性毒性 - 野生鸟类口服LD50',
    'Acute_Toxicity_quail_oral_LD50': '急性毒性 - 鹌鹑口服LD50',
    'Acute_Toxicity_duck_oral_LD50': '急性毒性 - 鸭口服LD50',
    'Acute_Toxicity_chicken_oral_LD50': '急性毒性 - 鸡口服LD50',
    'Acute_Toxicity_mouse_oral_LDLo': '急性毒性 - 小鼠口服LDLo',
    'Acute_Toxicity_rat_oral_LDLo': '急性毒性 - 大鼠口服LDLo',
    'Acute_Toxicity_rabbit_oral_LDLo': '急性毒性 - 兔口服LDLo',
    'Acute_Toxicity_dog_oral_LDLo': '急性毒性 - 狗口服LDLo',
    'Acute_Toxicity_cat_oral_LDLo': '急性毒性 - 猫口服LDLo',
    'Acute_Toxicity_man_oral_TDLo': '急性毒性 - 人口服TDLo',
    'Acute_Toxicity_women_oral_TDLo': '急性毒性 - 女性口服TDLo',
    'Acute_Toxicity_human_oral_TDLo': '急性毒性 - 人类口服TDLo',
    'Acute_Toxicity_mouse_unreported_LD50': '急性毒性 - 小鼠未报告LD50',
    'Acute_Toxicity_mammal_species_unspecified_unreported_LD50': '急性毒性 - 哺乳动物(未指定)未报告LD50',
    'Acute_Toxicity_rat_unreported_LD50': '急性毒性 - 大鼠未报告LD50',
    'Acute_Toxicity_mouse_skin_LD50': '急性毒性 - 小鼠皮肤LD50',
    'Acute_Toxicity_guinea_pig_skin_LD50': '急性毒性 - 豚鼠皮肤LD50',
    'Acute_Toxicity_rat_skin_LD50': '急性毒性 - 大鼠皮肤LD50',
    'Acute_Toxicity_rabbit_skin_LD50': '急性毒性 - 兔皮肤LD50',
    'Acute_Toxicity_rabbit_skin_LDLo': '急性毒性 - 兔皮肤LDLo',
    'Acute_Toxicity_mouse_subcutaneous_LD50': '急性毒性 - 小鼠皮下注射LD50',
    'Acute_Toxicity_mammal_species_unspecified_subcutaneous_LD50': '急性毒性 - 哺乳动物(未指定)皮下注射LD50',
    'Acute_Toxicity_guinea_pig_subcutaneous_LD50': '急性毒性 - 豚鼠皮下注射LD50',
    'Acute_Toxicity_rat_subcutaneous_LD50': '急性毒性 - 大鼠皮下注射LD50',
    'Acute_Toxicity_rabbit_subcutaneous_LD50': '急性毒性 - 兔皮下注射LD50',
    'Acute_Toxicity_mouse_subcutaneous_LDLo': '急性毒性 - 小鼠皮下注射LDLo',
    'Acute_Toxicity_guinea_pig_subcutaneous_LDLo': '急性毒性 - 豚鼠皮下注射LDLo',
    'Acute_Toxicity_rat_subcutaneous_LDLo': '急性毒性 - 大鼠皮下注射LDLo',
    'Acute_Toxicity_rabbit_subcutaneous_LDLo': '急性毒性 - 兔皮下注射LDLo',
    'Acute_Toxicity_frog_subcutaneous_LDLo': '急性毒性 - 青蛙皮下注射LDLo',
    'Acute_Toxicity_mouse_intramuscular_LD50': '急性毒性 - 小鼠肌肉注射LD50',
    'Acute_Toxicity_rat_intramuscular_LD50': '急性毒性 - 大鼠肌肉注射LD50',
    'Acute_Toxicity_mouse_parenteral_LD50': '急性毒性 - 小鼠非肠道给药LD50'
}

@app.route('/')
def index():
    return render_template('toxics.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/toxicity_search')
def toxicity_search():
    return render_template('toxicity_search.html')

@app.route('/search_result')
def search_result():
    search_field = request.args.get('search_field', '').strip()
    keyword = request.args.get('keyword', '').strip()
    
    if not search_field or not keyword:
        return render_template('search_result.html', 
                            error_message="请提供有效的搜索条件")

    try:
        # 连接数据库（移除了table参数）
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # 安全处理输入
        safe_keyword = re.sub(r"([%_'\"\\-])", r"\\\1", keyword) if search_field not in ['ID', 'PubChem_CID'] else keyword
        
        # 构建查询（使用固定表名）
        if search_field in ['ID']:
            try:
                keyword_num = float(keyword) if '.' in keyword else int(keyword)
                sql = f"SELECT * FROM `{TABLE_NAME}` WHERE `{search_field}` = %s"
                cursor.execute(sql, (keyword_num,))
                results = cursor.fetchall()
            except ValueError:
                return render_template('search_result.html',
                                    error_message=f"'{keyword}' 不是有效的数值")
        elif search_field in ['Canonical_SMILES', 'IUPAC_Name', 'Name', 'InChIKey','PubChem_CID']:
            # 对SMILES字符串或IUPAC名称进行精确匹配
            sql = f"SELECT * FROM `{TABLE_NAME}` WHERE `{search_field}` = %s"
            cursor.execute(sql, (keyword,))
            
            # 获取精确匹配的结果
            results = cursor.fetchall()
            
            # 如果精确匹配没有结果，尝试模糊匹配
            if len(results) == 0:
                sql = f"SELECT * FROM `{TABLE_NAME}` WHERE `{search_field}` LIKE %s ESCAPE '\\'"
                cursor.execute(sql, (f"%{safe_keyword}%",))
                results = cursor.fetchall()
        else:
            sql = f"SELECT * FROM `{TABLE_NAME}` WHERE `{search_field}` LIKE %s ESCAPE '\\'"
            cursor.execute(sql, (f"%{safe_keyword}%",))
            results = cursor.fetchall()

        # 分析毒性特征
        toxicity_data = []
        
        for row in results:
            # 检查不为0的列
            toxic_features = [
                col for col in row 
                if (col not in EXCLUDE_COLUMNS and 
                    row[col] is not None and 
                    str(row[col]).strip() not in ('0', '0.0', ''))
            ]
            
            toxicity_data.append({
                'id': row.get('ID', 'N/A'),
                'name': row.get('Name', 'N/A'),
                'toxic_features': toxic_features,
                'full_data': row  # 保留完整数据供备用
            })

        return render_template('search_result.html',
                            search_field=search_field,
                            keyword=keyword,
                            toxicity_data=toxicity_data,
                            count=len(toxicity_data))

    except mysql.connector.Error as err:
        # error_msg = "数据库错误，请尝试使用PubChem CID进行精确查询" if "1064" in str(err) else str(err)
        error_msg = "没有找到符合条件的数据" if "1064" in str(err) else str(err)
        return render_template('search_result.html', error_message=error_msg)
    except Exception as err:
        return render_template('search_result.html', error_message=str(err))
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/toxicity_result')
def toxicity_result():
    toxicity_field = request.args.get('toxicity_field', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    if not toxicity_field:
        return render_template('toxicity_result.html', 
                            error_message="请选择毒性特征字段")

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 获取总数
        count_sql = f"SELECT COUNT(*) as total FROM `{TABLE_NAME}` WHERE `{toxicity_field}` != 0 AND `{toxicity_field}` IS NOT NULL"
        cursor.execute(count_sql)
        total = cursor.fetchone()['total']
        
        # 计算总页数
        total_pages = (total + per_page - 1) // per_page
        
        # 获取分页数据
        offset = (page - 1) * per_page
        sql = f"""
            SELECT * FROM `{TABLE_NAME}` 
            WHERE `{toxicity_field}` != 0 AND `{toxicity_field}` IS NOT NULL
            LIMIT %s OFFSET %s
        """
        cursor.execute(sql, (per_page, offset))
        results = cursor.fetchall()
        
        toxicity_data = [{
            'id': row['ID'],
            'name': row['Name'],
            'full_data': row,
            'toxicity_value': row[toxicity_field]
        } for row in results]
        
        return render_template('toxicity_result.html',
                            toxicity_field=toxicity_field,
                            toxicity_field_display=TOXICITY_FIELD_DISPLAY.get(toxicity_field, toxicity_field),
                            toxicity_data=toxicity_data,
                            count=total,
                            page=page,
                            per_page=per_page,
                            total_pages=total_pages)
                            
    except mysql.connector.Error as err:
        return render_template('toxicity_result.html',
                            error_message=f"数据库错误: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/download_toxicity_results')
def download_toxicity_results():
    toxicity_field = request.args.get('toxicity_field', '').strip()
    
    if not toxicity_field:
        return "请选择毒性特征字段", 400

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 获取所有数据（不分页）
        sql = f"""
            SELECT * FROM `{TABLE_NAME}` 
            WHERE `{toxicity_field}` != 0 AND `{toxicity_field}` IS NOT NULL
        """
        cursor.execute(sql)
        results = cursor.fetchall()
        
        if not results:
            return "没有找到符合条件的数据", 404
            
        # 创建CSV文件
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入标题行
        headers = ['ID', 'Name', 'IUPAC_Name', 'PubChem_CID', 'Canonical_SMILES', 'InChIKey', toxicity_field]
        writer.writerow(headers)
        
        # 写入数据行
        for row in results:
            writer.writerow([
                row['ID'],
                row['Name'],
                row['IUPAC_Name'],
                row['PubChem_CID'],
                row['Canonical_SMILES'],
                row['InChIKey'],
                row[toxicity_field]
            ])
        
        # 准备响应
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename={toxicity_field}_results.csv'
        response.headers['Content-type'] = 'text/csv'
        
        return response
        
    except mysql.connector.Error as err:
        return f"数据库错误: {err}", 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/data_collection')
def data_collection():
    return render_template('data_collection.html')

@app.route('/toxicity_prediction')
def toxicity_prediction():
    return render_template('toxicity_prediction.html')

@app.route('/predict_toxicity', methods=['POST'])
def predict_toxicity_route():
    try:
        # 只使用eToxPred模型进行预测
        model_type = 'etoxpred'
        results = []
        
        # 检查是否有文件上传
        if 'smi_file' in request.files and request.files['smi_file'].filename:
            file = request.files['smi_file']
            
            # 检查文件扩展名
            if not file.filename.lower().endswith('.smi'):
                return jsonify({'error': '只支持.smi格式的文件'})
            
            # 保存上传的文件到临时目录
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, secure_filename(file.filename))
            file.save(file_path)
            
            # 处理.smi文件
            results = process_smi_file(file_path, model_type)
            
            # 删除临时文件
            os.remove(file_path)
            os.rmdir(temp_dir)
            
        # 检查是否有SMILES输入
        elif 'smiles_input' in request.form and request.form['smiles_input'].strip():
            smiles = request.form['smiles_input'].strip()
            
            # 处理多行SMILES输入
            for line in smiles.split('\n'):
                line = line.strip()
                if line:
                    # 预测毒性
                    result = predict_toxicity(line, model_type)
                    results.append(result)
        else:
            return jsonify({'error': '请提供SMILES序列或上传.smi文件'})
        
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': f'处理请求时发生错误: {str(e)}'})


@app.route('/download_dataset')
def download_dataset():
    try:
        return send_file('total_compound_data_utf8_clean.csv',
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='compound_toxicity_dataset.csv')
    except Exception as e:
        return render_template('data_collection.html', error_message=f"下载失败: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)