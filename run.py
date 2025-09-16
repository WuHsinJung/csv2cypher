#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化的執行腳本
"""

from converter import KnowledgeGraphConverter

def main():
    # 創建轉換器
    converter = KnowledgeGraphConverter()
    
    # 轉換知識點檔案
    result = converter.convert_knowledge_points('knowledge_points_example.csv')
    
    # 儲存結果
    with open('output/knowledge_points.cypher', 'w', encoding='utf-8') as f:
        f.write(result)
    
    print('✅ 轉換完成！結果已儲存到 output/knowledge_points.cypher')
    print(f'📊 生成了 {len(result.split(chr(10)))} 行 Cypher 語句')

if __name__ == '__main__':
    main()
