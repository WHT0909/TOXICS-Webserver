import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski
from rdkit.Chem import AllChem
# 移除不存在的导入
# from rdkit.ML.Descriptors import MolecularDescriptorCalculator
import joblib
import os
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# 定义特征计算函数
def calculate_molecular_descriptors(smiles):
    """计算分子描述符"""
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
            
        # 计算基本描述符
        descriptors = {}
        descriptors['MolWt'] = Descriptors.MolWt(mol)
        descriptors['LogP'] = Descriptors.MolLogP(mol)
        descriptors['NumHDonors'] = Lipinski.NumHDonors(mol)
        descriptors['NumHAcceptors'] = Lipinski.NumHAcceptors(mol)
        descriptors['NumRotatableBonds'] = Descriptors.NumRotatableBonds(mol)
        descriptors['NumAromaticRings'] = Lipinski.NumAromaticRings(mol)
        descriptors['NumHeavyAtoms'] = Descriptors.HeavyAtomCount(mol)
        descriptors['TPSA'] = Descriptors.TPSA(mol)
        
        # 计算更多描述符
        descriptors['MolMR'] = Descriptors.MolMR(mol)
        descriptors['FractionCSP3'] = Descriptors.FractionCSP3(mol)
        descriptors['NumAliphaticRings'] = Lipinski.NumAliphaticRings(mol)
        descriptors['NumSaturatedRings'] = Lipinski.NumSaturatedRings(mol)
        descriptors['NumAromaticHeterocycles'] = Lipinski.NumAromaticHeterocycles(mol)
        descriptors['NumSaturatedHeterocycles'] = Lipinski.NumSaturatedHeterocycles(mol)
        descriptors['NumAliphaticHeterocycles'] = Lipinski.NumAliphaticHeterocycles(mol)
        descriptors['RingCount'] = Descriptors.RingCount(mol)
        
        return pd.Series(descriptors)
    except Exception as e:
        print(f"Error calculating descriptors for {smiles}: {str(e)}")
        return None

# 定义模型训练函数（仅用于初始化模型，实际应用中应该使用预训练模型）
def train_toxicity_models():
    """训练毒性预测模型"""
    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    # 创建随机森林模型
    models = {
        'general_toxicity': RandomForestClassifier(n_estimators=100, random_state=42),
        'hepatotoxicity': RandomForestClassifier(n_estimators=100, random_state=42),
        'cardiotoxicity': RandomForestClassifier(n_estimators=100, random_state=42),
        'mutagenicity': RandomForestClassifier(n_estimators=100, random_state=42)
    }
    
    # 创建标准化器
    scaler = StandardScaler()
    
    # 生成随机数据进行模拟训练
    np.random.seed(42)
    n_samples = 1000
    n_features = 16  # 与我们计算的描述符数量匹配
    
    # 为每个模型生成随机特征和标签
    for model_name, model in models.items():
        X = np.random.randn(n_samples, n_features)
        y = np.random.randint(0, 2, size=n_samples)  # 二分类问题
        
        # 标准化特征
        X_scaled = scaler.fit_transform(X)
        
        # 训练模型
        model.fit(X_scaled, y)
        
        # 保存模型和标准化器
        model_path = os.path.join(models_dir, f'{model_name}_model.pkl')
        scaler_path = os.path.join(models_dir, f'{model_name}_scaler.pkl')
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
    
    # 保存特征名称列表
    feature_names = [
        'MolWt', 'LogP', 'NumHDonors', 'NumHAcceptors', 'NumRotatableBonds',
        'NumAromaticRings', 'NumHeavyAtoms', 'TPSA', 'MolMR', 'FractionCSP3',
        'NumAliphaticRings', 'NumSaturatedRings', 'NumAromaticHeterocycles',
        'NumSaturatedHeterocycles', 'NumAliphaticHeterocycles', 'RingCount'
    ]
    
    with open(os.path.join(models_dir, 'feature_names.pkl'), 'wb') as f:
        pickle.dump(feature_names, f)
    
    return models_dir

# 定义预测函数 - 只使用eToxPred模型
def predict_toxicity(smiles, model_type='etoxpred'):
    """使用eToxPred模型预测化合物的毒性"""
    # 直接调用eToxPred预测函数
    return predict_etoxpred(smiles)

# 根据模型类型和概率提供详细信息
def get_toxicity_details(model_type, probability):
    """根据模型类型和概率提供详细的毒性信息"""
    # 只保留eToxPred相关的详细信息
    if probability < 0.3:
        return '该化合物可能具有较低的毒性风险 (eToxPred模型)'
    elif probability < 0.7:
        return '该化合物可能具有中等的毒性风险，建议进一步评估 (eToxPred模型)'
    else:
        return '该化合物可能具有较高的毒性风险，建议谨慎使用 (eToxPred模型)'
    
    return '无详细信息可提供。'

# eToxPred预测函数
def predict_etoxpred(smiles, name=None):
    """使用eToxPred模型预测化合物的毒性"""
    try:
        import os
        import numpy as np
        from rdkit import Chem
        from rdkit.Chem import AllChem
        import sys
        import pickle
        import joblib
        
        # 添加eToxPred目录到系统路径
        etoxpred_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'eToxPred')
        if etoxpred_dir not in sys.path:
            sys.path.append(etoxpred_dir)
        
        # 检查输入
        if not smiles or not isinstance(smiles, str):
            return {
                'compound': name or smiles,
                'prediction': 'Error',
                'probability': 0.0,
                'details': '无效的SMILES序列'
            }
        
        # 加载模型 - 尝试多种方式加载以解决兼容性问题
        model_path = os.path.join(etoxpred_dir, 'etoxpred_best_model.joblib')
        try:
            # 首先尝试使用joblib直接加载，设置allow_pickle=True以提高兼容性
            try:
                clf = joblib.load(model_path, mmap_mode=None)
            except Exception as joblib_error:
                # 如果直接加载失败，尝试使用pickle兼容模式加载
                try:
                    with open(model_path, 'rb') as f:
                        clf = pickle.load(f, encoding='latin1')
                except Exception as pickle_error:
                    # 如果pickle也失败，尝试使用numpy加载
                    try:
                        import numpy as np
                        clf = np.load(model_path, allow_pickle=True)
                    except Exception as numpy_error:
                        # 如果所有方法都失败，返回详细错误信息
                        return {
                            'compound': name or smiles,
                            'prediction': 'Error',
                            'probability': 0.0,
                            'details': f'模型加载错误: 无法加载模型文件，请确认etoxpred_best_model.joblib文件格式正确'
                        }
        except Exception as load_error:
            return {
                'compound': name or smiles,
                'prediction': 'Error',
                'probability': 0.0,
                'details': f'模型加载错误: {str(load_error)}'
            }
        
        # 生成分子指纹
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return {
                'compound': name or smiles,
                'prediction': 'Error',
                'probability': 0.0,
                'details': '无法解析SMILES序列'
            }
        
        mol = Chem.AddHs(mol)
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=1024)
        fp_string = fp.ToBitString()
        X = np.array(list(fp_string), dtype=float).reshape(1, 1024)
        
        # 预测毒性 - 添加异常处理
        try:
            tox_score = clf.predict_proba(X)[:, 1][0]
        except Exception as pred_error:
            return {
                'compound': name or smiles,
                'prediction': 'Error',
                'probability': 0.0,
                'details': f'预测过程错误: {str(pred_error)}'
            }
        
        # 根据毒性分数提供详细信息
        if tox_score < 0.3:
            details = '该化合物可能具有较低的毒性风险 (eToxPred模型)'
        elif tox_score < 0.7:
            details = '该化合物可能具有中等的毒性风险，建议进一步评估 (eToxPred模型)'
        else:
            details = '该化合物可能具有较高的毒性风险，建议谨慎使用 (eToxPred模型)'
        
        return {
            'compound': name or smiles,
            'prediction': '有毒性' if tox_score > 0.5 else '无毒性',
            'probability': float(tox_score),  # 确保是Python原生浮点数
            'details': details
        }
    except Exception as e:
        return {
            'compound': name or smiles,
            'prediction': 'Error',
            'probability': 0.0,
            'details': f'预测过程中发生错误: {str(e)}'
        }

# 处理.smi文件
def process_smi_file(file_path, model_type='etoxpred'):
    """处理.smi文件并使用eToxPred预测每个化合物的毒性"""
    results = []
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 处理不同格式的.smi文件
                parts = line.split()
                if len(parts) > 0:
                    smiles = parts[0]  # 通常SMILES是第一列
                    name = parts[1] if len(parts) > 1 else smiles  # 如果有名称，使用名称
                    
                    # 只使用eToxPred进行预测
                    result = predict_etoxpred(smiles, name)
                    results.append(result)
    except Exception as e:
        results.append({
            'compound': 'Error',
            'prediction': 'Error',
            'probability': 0.0,
            'details': f'处理文件时发生错误: {str(e)}'
        })
    
    return results

# 如果直接运行此脚本，则初始化模型
if __name__ == '__main__':
    train_toxicity_models()