#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV/Excel 轉 Neo4j Cypher 語句轉換工具
支援知識點檔案和先備關係檔案的轉換
支援多種編碼格式
"""

import os
import sys
import pandas as pd
from pathlib import Path
from converter import KnowledgeGraphConverter

def main():
    """主程式入口點"""
    print("=" * 60)
    print("CSV/Excel 轉 Neo4j Cypher 語句轉換工具")
    print("=" * 60)
    
    # 檢查是否有檔案參數
    if len(sys.argv) < 3:
        print("使用方法:")
        print("python csv2cypher.py <知識點檔案路徑> <先備關係檔案路徑>")
        print("\n範例:")
        print("python csv2cypher.py knowledge_points_EMA.csv Prerequisite_EMA.csv")
        print("\n或者直接執行，程式會提示您選擇檔案")
        
        # 顯示可用的檔案
        available_files = list_available_files()
        if available_files:
            print("\n可用的檔案:")
            for i, (knowledge, prerequisite) in enumerate(available_files, 1):
                print(f"{i}. {knowledge} + {prerequisite}")
            
            # 互動式選擇
            try:
                choice = input(f"\n請選擇檔案組合 (1-{len(available_files)}) 或按Enter使用預設檔案: ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(available_files):
                    selected = available_files[int(choice) - 1]
                    knowledge_file = selected[0]
                    prerequisite_file = selected[1]
                else:
                    # 使用預設檔案
                    knowledge_file = "knowledge_points_EMA.csv"
                    prerequisite_file = "Prerequisite_EMA.csv"
            except (ValueError, IndexError):
                knowledge_file = "knowledge_points_EMA.csv"
                prerequisite_file = "Prerequisite_EMA.csv"
        else:
            # 互動式輸入
            knowledge_file = input("\n請輸入知識點檔案路徑 (或按Enter使用預設檔案): ").strip()
            if not knowledge_file:
                knowledge_file = "knowledge_points_EMA.csv"
            
            prerequisite_file = input("請輸入先備關係檔案路徑 (或按Enter使用預設檔案): ").strip()
            if not prerequisite_file:
                prerequisite_file = "Prerequisite_EMA.csv"
    else:
        knowledge_file = sys.argv[1]
        prerequisite_file = sys.argv[2]
    
    # 檢查檔案是否存在
    if not os.path.exists(knowledge_file):
        print(f"錯誤: 找不到知識點檔案 '{knowledge_file}'")
        return
    
    if not os.path.exists(prerequisite_file):
        print(f"錯誤: 找不到先備關係檔案 '{prerequisite_file}'")
        return
    
    try:
        # 創建轉換器實例
        converter = KnowledgeGraphConverter()
        
        # 執行轉換
        print(f"\n正在處理知識點檔案: {knowledge_file}")
        print(f"正在處理先備關係檔案: {prerequisite_file}")
        
        # 轉換知識點
        knowledge_cypher = converter.convert_knowledge_points(knowledge_file)
        
        # 轉換先備關係
        prerequisite_cypher = converter.convert_prerequisites(prerequisite_file)
        
        # 輸出結果
        print("\n" + "=" * 60)
        print("轉換完成！")
        print("=" * 60)
        
        # 儲存到檔案
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # 取得檔案名稱（不含副檔名）作為輸出檔案名稱
        knowledge_name = Path(knowledge_file).stem
        prerequisite_name = Path(prerequisite_file).stem
        
        # 儲存知識點Cypher語句
        knowledge_output_file = output_dir / f"{knowledge_name}_nodes.cypher"
        with open(knowledge_output_file, 'w', encoding='utf-8') as f:
            f.write(knowledge_cypher)
        print(f"知識點Cypher語句已儲存至: {knowledge_output_file}")
        
        # 儲存先備關係Cypher語句
        prerequisite_output_file = output_dir / f"{prerequisite_name}_relationships.cypher"
        with open(prerequisite_output_file, 'w', encoding='utf-8') as f:
            f.write(prerequisite_cypher)
        print(f"先備關係Cypher語句已儲存至: {prerequisite_output_file}")
        
        # 儲存完整Cypher腳本
        complete_output_file = output_dir / f"{knowledge_name}_{prerequisite_name}_complete.cypher"
        complete_script = f"""// 完整的Neo4j Cypher腳本
// 由CSV轉換工具自動生成
// 檔案: {knowledge_file} + {prerequisite_file}

// 清除現有資料 (可選)
// MATCH (n) DETACH DELETE n;

{knowledge_cypher}

{prerequisite_cypher}

// 查詢範例
// MATCH (n:KnowledgePoint) RETURN n LIMIT 10;
// MATCH (a:KnowledgePoint)-[r:Prerequisite]->(b:KnowledgePoint) RETURN a, r, b LIMIT 10;
// MATCH (n:KnowledgePoint {{subject: 'math'}}) RETURN n;
// MATCH (n:KnowledgePoint {{isRoot: true}}) RETURN n;
"""
        
        with open(complete_output_file, 'w', encoding='utf-8') as f:
            f.write(complete_script)
        print(f"完整Cypher腳本已儲存至: {complete_output_file}")
        
        print("\n您可以直接複製這些檔案中的內容到Neo4j瀏覽器執行！")
        
    except Exception as e:
        print(f"轉換過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

def list_available_files():
    """列出可用的檔案組合"""
    available_files = []
    
    # 尋找知識點檔案
    knowledge_files = [f for f in os.listdir('.') if f.startswith('knowledge_points_') and f.endswith('.csv')]
    
    for knowledge_file in knowledge_files:
        # 提取檔案名稱中的類型（EMA, HMA, JMA等）
        file_type = knowledge_file.replace('knowledge_points_', '').replace('.csv', '')
        prerequisite_file = f"Prerequisite_{file_type}.csv"
        
        if os.path.exists(prerequisite_file):
            available_files.append((knowledge_file, prerequisite_file))
    
    return available_files

if __name__ == "__main__":
    main()
