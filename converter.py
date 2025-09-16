#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知識圖譜轉換器模組
負責將CSV檔案轉換為Neo4j Cypher語句
支援多種編碼格式
"""

import pandas as pd
import re
import chardet

class KnowledgeGraphConverter:
    """知識圖譜轉換器類別"""
    
    def __init__(self):
        """初始化轉換器"""
        pass
    
    def detect_encoding(self, file_path):
        """
        自動檢測檔案編碼
        
        Args:
            file_path (str): 檔案路徑
            
        Returns:
            str: 檢測到的編碼
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                confidence = result['confidence']
                
                print(f"檢測到編碼: {encoding} (信心度: {confidence:.2f})")
                
                # 如果信心度太低，嘗試常見編碼
                if confidence < 0.7:
                    common_encodings = ['utf-8', 'big5', 'gbk', 'gb2312', 'cp950']
                    for enc in common_encodings:
                        try:
                            with open(file_path, 'r', encoding=enc) as f:
                                f.read()
                            print(f"使用常見編碼: {enc}")
                            return enc
                        except UnicodeDecodeError:
                            continue
                
                return encoding
        except Exception as e:
            print(f"編碼檢測失敗: {e}")
            return 'utf-8'
    
    def read_csv_with_encoding(self, file_path):
        """
        使用適當編碼讀取CSV檔案
        
        Args:
            file_path (str): CSV檔案路徑
            
        Returns:
            pandas.DataFrame: 讀取的資料
        """
        # 嘗試檢測編碼
        encoding = self.detect_encoding(file_path)
        
        # 嘗試讀取檔案
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            return df
        except UnicodeDecodeError:
            # 如果檢測的編碼失敗，嘗試常見編碼
            common_encodings = ['utf-8', 'big5', 'gbk', 'gb2312', 'cp950']
            for enc in common_encodings:
                if enc != encoding:
                    try:
                        print(f"嘗試編碼: {enc}")
                        df = pd.read_csv(file_path, encoding=enc)
                        return df
                    except UnicodeDecodeError:
                        continue
            
            # 如果所有編碼都失敗，使用錯誤處理
            print("所有編碼都失敗，使用錯誤處理模式")
            df = pd.read_csv(file_path, encoding='utf-8', errors='ignore')
            return df
    
    def convert_knowledge_points(self, file_path):
        """
        轉換知識點CSV檔案為Cypher語句
        
        Args:
            file_path (str): 知識點CSV檔案路徑
            
        Returns:
            str: Cypher語句字串
        """
        try:
            # 讀取CSV檔案
            df = self.read_csv_with_encoding(file_path)
            
            # 清理資料
            df = df.dropna(how='all')  # 移除完全空白的列
            
            # 建立欄位名稱對應表（支援中英文）
            column_mapping = {
                'Label': ['Label', '標籤(Label)', '標籤'],
                'Name': ['Name', '名稱(Name)', '名稱'],
                'Education System': ['Education System', '學制(Education System)', '學制'],
                'Subject': ['Subject', '學科(Subject)', '學科'],
                'ID': ['ID', '編號(ID)', '編號'],
                'IsRoot': ['IsRoot', '是否為根結點(IsRoot)', '是否為根結點'],
                'Topic': ['Topic', '主題(Topic)', '主題', '第一層知識'],
                'Unit': ['Unit', '次主題(Unit)', '次主題', '第二層知識'],
                'Concept': ['Concept', '概念(Concept)', '概念', '第三層知識']
            }
            
            # 檢查必要欄位並建立對應關係
            required_fields = ['Label', 'Name', 'Education System', 'Subject']
            field_mapping = {}
            missing_columns = []
            
            for field in required_fields:
                found = False
                for col in df.columns:
                    if col in column_mapping[field]:
                        field_mapping[field] = col
                        found = True
                        break
                if not found:
                    missing_columns.append(field)
            
            if missing_columns:
                raise ValueError(f"缺少必要欄位: {missing_columns}")
            
            cypher_statements = []
            cypher_statements.append("// 創建知識點節點")
            cypher_statements.append("")
            
            # 準備批量創建的資料
            nodes_data = []
            seen_names = set()  # 用於檢查知識點名稱唯一性
            
            # 處理每一行資料
            for index, row in df.iterrows():
                # 跳過標題行或空行
                name_col = field_mapping['Name']
                if pd.isna(row[name_col]) or str(row[name_col]).strip() == '':
                    continue
                
                # 取得欄位值（使用對應的欄位名稱）
                label_col = field_mapping['Label']
                label = str(row[label_col]).strip() if pd.notna(row[label_col]) else 'KnowledgePoint'
                name = str(row[name_col]).strip()
                
                # 檢查知識點名稱唯一性
                if name in seen_names:
                    raise ValueError(f"知識點名稱重複: '{name}' (第{index+1}行)")
                seen_names.add(name)
                
                education_system_col = field_mapping['Education System']
                subject_col = field_mapping['Subject']
                education_system = str(row[education_system_col]).strip() if pd.notna(row[education_system_col]) else ''
                subject = str(row[subject_col]).strip() if pd.notna(row[subject_col]) else ''
                
                # 處理 IsRoot 欄位（如果存在）
                is_root = ''
                if 'IsRoot' in field_mapping:
                    is_root_col = field_mapping['IsRoot']
                    is_root = str(row[is_root_col]).strip().upper() if pd.notna(row[is_root_col]) and str(row[is_root_col]).strip() != '' else ''
                
                # 處理選填欄位
                knowledge_id = ''
                if 'ID' in field_mapping:
                    id_col = field_mapping['ID']
                    knowledge_id = str(row[id_col]).strip() if pd.notna(row[id_col]) and str(row[id_col]).strip() != '' else ''
                
                # 處理知識層級欄位（支援中英文並列）
                topic = ''
                unit = ''
                concept = ''
                
                # 處理 Topic 欄位
                for col in df.columns:
                    if col in column_mapping['Topic']:
                        topic = str(row[col]).strip() if pd.notna(row[col]) and str(row[col]).strip() != '' and str(row[col]).strip().upper() != 'X' else ''
                        break
                
                # 處理 Unit 欄位
                for col in df.columns:
                    if col in column_mapping['Unit']:
                        unit = str(row[col]).strip() if pd.notna(row[col]) and str(row[col]).strip() != '' and str(row[col]).strip().upper() != 'X' else ''
                        break
                
                # 處理 Concept 欄位
                for col in df.columns:
                    if col in column_mapping['Concept']:
                        concept = str(row[col]).strip() if pd.notna(row[col]) and str(row[col]).strip() != '' and str(row[col]).strip().upper() != 'X' else ''
                        break
                
                # 轉換布林值（空白時為空值）
                if is_root == 'TRUE':
                    is_root_bool = 'true'
                elif is_root == 'FALSE':
                    is_root_bool = 'false'
                else:
                    is_root_bool = None  # 空值
                
                # 建立節點屬性
                properties = {
                    'name': name,
                    'educationSystem': education_system,
                    'subject': subject
                }
                
                # 只有當 isRoot 有值時才添加
                if is_root_bool is not None:
                    properties['isRoot'] = is_root_bool
                
                # 添加選填屬性
                if knowledge_id:
                    properties['knowledgeId'] = knowledge_id
                if topic:
                    properties['topic'] = topic
                if unit:
                    properties['unit'] = unit
                if concept:
                    properties['concept'] = concept
                
                nodes_data.append(properties)
            
            # 使用UNWIND批量創建節點
            if nodes_data:
                # 轉換為Cypher格式的資料
                cypher_data = []
                for node_data in nodes_data:
                    # 轉義字串值
                    escaped_data = {}
                    for key, value in node_data.items():
                        if isinstance(value, str):
                            escaped_data[key] = self._escape_string(value)
                        else:
                            escaped_data[key] = str(value)
                    
                    # 建立屬性字串
                    properties_str = ', '.join([f'{k}: {v}' for k, v in escaped_data.items()])
                    cypher_data.append(f"{{{properties_str}}}")
                
                # 建立UNWIND語句
                cypher_statements.append("UNWIND [")
                cypher_statements.append(",\n".join(cypher_data))
                cypher_statements.append("] AS nodeData")
                cypher_statements.append("CREATE (n:KnowledgePoint) SET n = nodeData")
                cypher_statements.append("")
            
            cypher_statements.append("// 建立索引以提升查詢效能")
            cypher_statements.append("// 建立名稱索引")
            cypher_statements.append("CREATE INDEX FOR (n:KnowledgePoint) ON (n.name)")
            cypher_statements.append("")
            cypher_statements.append("// 建立科目索引")
            cypher_statements.append("CREATE INDEX FOR (n:KnowledgePoint) ON (n.subject)")
            cypher_statements.append("")
            cypher_statements.append("// 建立教育階段索引")
            cypher_statements.append("CREATE INDEX FOR (n:KnowledgePoint) ON (n.educationSystem)")
            
            return '\n'.join(cypher_statements)
            
        except Exception as e:
            raise Exception(f"轉換知識點檔案時發生錯誤: {str(e)}")
    
    def convert_prerequisites(self, file_path):
        """
        轉換先備關係CSV檔案為Cypher語句
        
        Args:
            file_path (str): 先備關係CSV檔案路徑
            
        Returns:
            str: Cypher語句字串
        """
        try:
            # 讀取CSV檔案
            df = self.read_csv_with_encoding(file_path)
            
            # 清理資料
            df = df.dropna(how='all')  # 移除完全空白的列
            
            # 建立欄位名稱對應表（支援中英文）
            prerequisite_column_mapping = {
                'Types': ['Types', '類型(Types)', '類型'],
                'Prerequisite': ['Prerequisite', '先備關係(Prerequisite)', '先備關係'],
                'Target': ['Target', '名稱(Name)', '名稱', 'Name']
            }
            
            # 檢查必要欄位並建立對應關係
            required_fields = ['Types', 'Prerequisite', 'Target']
            prerequisite_field_mapping = {}
            missing_columns = []
            
            for field in required_fields:
                found = False
                for col in df.columns:
                    if col in prerequisite_column_mapping[field]:
                        prerequisite_field_mapping[field] = col
                        found = True
                        break
                if not found:
                    missing_columns.append(field)
            
            if missing_columns:
                raise ValueError(f"缺少必要欄位: {missing_columns}")
            
            cypher_statements = []
            cypher_statements.append("// 創建先備關係")
            cypher_statements.append("")
            
            # 準備批量創建的資料
            relationships_data = []
            
            # 處理每一行資料
            for index, row in df.iterrows():
                # 跳過標題行或空行
                target_col = prerequisite_field_mapping['Target']
                if pd.isna(row[target_col]) or str(row[target_col]).strip() == '':
                    continue
                
                # 取得欄位值（使用對應的欄位名稱）
                types_col = prerequisite_field_mapping['Types']
                prerequisite_col = prerequisite_field_mapping['Prerequisite']
                relationship_type = str(row[types_col]).strip() if pd.notna(row[types_col]) else 'Prerequisite'
                prerequisite = str(row[prerequisite_col]).strip() if pd.notna(row[prerequisite_col]) else ''
                target = str(row[target_col]).strip()
                
                # 跳過空白的先備知識點
                if not prerequisite or prerequisite == '' or prerequisite.upper() == '無':
                    continue
                
                # 處理多個先備知識點（換行分隔）
                prerequisite_list = [p.strip() for p in prerequisite.split('\n') if p.strip() and p.strip().upper() != '無']
                
                if not prerequisite_list:
                    continue
                
                # 為每個先備知識點建立關係資料
                for prereq in prerequisite_list:
                    if prereq and prereq.upper() != '無':
                        relationships_data.append({
                            'prerequisite': prereq,
                            'target': target,
                            'type': relationship_type
                        })
            
            # 使用UNWIND批量創建關係
            if relationships_data:
                # 轉換為Cypher格式的資料
                cypher_data = []
                for rel_data in relationships_data:
                    # 轉義字串值
                    prereq_name = self._escape_string(rel_data['prerequisite'])
                    target_name = self._escape_string(rel_data['target'])
                    rel_type = rel_data['type']
                    
                    cypher_data.append(f"{{prerequisite: {prereq_name}, target: {target_name}, type: '{rel_type}'}}")
                
                # 建立UNWIND語句
                cypher_statements.append("UNWIND [")
                cypher_statements.append(",\n".join(cypher_data))
                cypher_statements.append("] AS relData")
                cypher_statements.append("MATCH (a:KnowledgePoint {name: relData.prerequisite})")
                cypher_statements.append("MATCH (b:KnowledgePoint {name: relData.target})")
                cypher_statements.append("CREATE (a)-[r:Prerequisite]->(b)")
                cypher_statements.append("")
            
            return '\n'.join(cypher_statements)
            
        except Exception as e:
            raise Exception(f"轉換先備關係檔案時發生錯誤: {str(e)}")
    
    def _escape_string(self, text):
        """
        轉義字串中的特殊字元
        
        Args:
            text (str): 要轉義的字串
            
        Returns:
            str: 轉義後的字串
        """
        if not text:
            return '""'
        
        # 轉換為字串
        text = str(text)
        
        # 轉義單引號
        text = text.replace("'", "\\'")
        
        # 轉義反斜線
        text = text.replace("\\", "\\\\")
        
        # 轉義換行符
        text = text.replace("\n", "\\n")
        text = text.replace("\r", "\\r")
        text = text.replace("\t", "\\t")
        
        return f"'{text}'"
    
    def validate_csv_structure(self, knowledge_file, prerequisite_file):
        """
        驗證CSV檔案結構
        
        Args:
            knowledge_file (str): 知識點檔案路徑
            prerequisite_file (str): 先備關係檔案路徑
            
        Returns:
            tuple: (知識點檔案是否有效, 先備關係檔案是否有效, 錯誤訊息列表)
        """
        errors = []
        knowledge_valid = True
        prerequisite_valid = True
        
        try:
            # 驗證知識點檔案
            df_knowledge = self.read_csv_with_encoding(knowledge_file)
            required_knowledge_columns = ['Label', 'Name', 'Education System', 'Subject']
            missing_knowledge = [col for col in required_knowledge_columns if col not in df_knowledge.columns]
            
            if missing_knowledge:
                knowledge_valid = False
                errors.append(f"知識點檔案缺少必要欄位: {missing_knowledge}")
            
            # 驗證先備關係檔案
            df_prerequisite = self.read_csv_with_encoding(prerequisite_file)
            required_prerequisite_columns = ['Types', 'Prerequisite', 'Target']
            missing_prerequisite = [col for col in required_prerequisite_columns if col not in df_prerequisite.columns]
            
            if missing_prerequisite:
                prerequisite_valid = False
                errors.append(f"先備關係檔案缺少必要欄位: {missing_prerequisite}")
            
        except Exception as e:
            errors.append(f"檔案讀取錯誤: {str(e)}")
            knowledge_valid = False
            prerequisite_valid = False
        
        return knowledge_valid, prerequisite_valid, errors
