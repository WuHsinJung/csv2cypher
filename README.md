# CSV/Excel 轉 Neo4j Cypher 語句轉換工具

這是一個專門用於將教育知識圖譜的CSV/Excel檔案轉換為Neo4j Cypher語句的Python工具。

## 功能特色

- 支援知識點檔案和先備關係檔案的轉換
- 自動處理多個先備知識點（換行分隔）
- 智能處理空白值和布林值轉換
- 自動建立索引以提升查詢效能
- 支援Excel (.xlsx) 和CSV檔案格式
- **自動檢測檔案編碼**（支援UTF-8、Big5、GBK等）
- 輸出多種格式的Cypher語句檔案
- 支援多套檔案（EMA、HMA、JMA等）

## 檔案結構

```
csv2cypher/
├── csv2cypher.py          # 主程式
├── converter.py            # 轉換器模組
├── requirements.txt        # Python依賴
├── README.md              # 使用說明
├── knowledge_points_EMA.csv    # 國小數學知識點
├── Prerequisite_EMA.csv       # 國小數學先備關係
├── knowledge_points_HMA.csv   # 高中數學知識點
├── Prerequisite_HMA.csv      # 高中數學先備關係
├── knowledge_points_JMA.csv  # 國中數學知識點
├── Prerequisite_JMA.csv     # 國中數學先備關係
└── output/                 # 輸出目錄（自動建立）
    ├── knowledge_points_EMA_nodes.cypher
    ├── Prerequisite_EMA_relationships.cypher
    └── knowledge_points_EMA_Prerequisite_EMA_complete.cypher
```

## 安裝需求

### 1. Python環境
- Python 3.7 或以上版本

### 2. 安裝依賴套件
```bash
pip install -r requirements.txt
```

## 使用方法

### 方法1：命令列參數
```bash
python csv2cypher.py <知識點檔案路徑> <先備關係檔案路徑>
```

範例：
```bash
python csv2cypher.py knowledge_points_EMA.csv Prerequisite_EMA.csv
```

### 方法2：互動式選擇
```bash
python csv2cypher.py
```
程式會自動偵測可用的檔案組合，讓您選擇要轉換的檔案。

## 檔案格式要求

### 知識點檔案（必填欄位）
- `Label`: 節點標籤（如：KnowledgePoint）
- `Name`: 知識點名稱（主要識別屬性）
- `Education System`: 教育階段（如：Elementary School）
- `Subject`: 學科領域（如：math）
- `IsRoot`: 是否為根節點（TRUE/FALSE，空白視為TRUE）

### 知識點檔案（選填欄位）
- `ID`: 知識點編號
- `第一層知識`: 知識分類第一層
- `第二層知識`: 知識分類第二層
- `第三層知識`: 知識分類第三層
- `Learning Performance`: 學習表現描述

### 先備關係檔案
- `Types`: 關係類型（如：Prerequisite）
- `Prerequisite`: 先備知識點名稱（支援多個，換行分隔）
- `Target`: 目標知識點名稱

## 編碼支援

程式會自動檢測檔案編碼，支援：
- UTF-8
- Big5（繁體中文）
- GBK（簡體中文）
- GB2312
- CP950

## 輸出檔案

程式會自動建立 `output/` 目錄，並產生以下檔案：

1. **{知識點檔案名}_nodes.cypher**: 包含所有知識點節點的創建語句
2. **{先備關係檔案名}_relationships.cypher**: 包含所有先備關係的創建語句
3. **{知識點檔案名}_{先備關係檔案名}_complete.cypher**: 完整的Neo4j Cypher腳本

## Neo4j使用說明

1. 將產生的Cypher語句複製到Neo4j瀏覽器
2. 執行腳本建立知識圖譜
3. 使用查詢範例來驗證資料

### 查詢範例
```cypher
// 查看所有知識點
MATCH (n:KnowledgePoint) RETURN n LIMIT 10;

// 查看先備關係
MATCH (a:KnowledgePoint)-[r:Prerequisite]->(b:KnowledgePoint) 
RETURN a, r, b LIMIT 10;

// 查看特定科目的知識點
MATCH (n:KnowledgePoint {subject: 'math'}) RETURN n;

// 查看根節點
MATCH (n:KnowledgePoint {isRoot: true}) RETURN n;

// 查看特定教育階段的知識點
MATCH (n:KnowledgePoint {educationSystem: 'Elementary School'}) RETURN n;
```

## 注意事項

1. **檔案編碼**: 程式會自動檢測編碼，但建議使用UTF-8
2. **欄位名稱**: 欄位名稱必須完全匹配（區分大小寫）
3. **資料完整性**: 知識點名稱在先備關係檔案中必須存在於知識點檔案中
4. **特殊字元**: 程式會自動處理單引號、換行符等特殊字元

## 錯誤處理

如果轉換過程中發生錯誤，程式會顯示詳細的錯誤訊息，包括：
- 缺少必要欄位
- 檔案讀取錯誤
- 資料格式問題
- 編碼問題

## 技術細節

- 使用pandas進行CSV檔案處理
- 使用chardet自動檢測檔案編碼
- 自動建立資料庫索引以提升查詢效能
- 支援多種檔案格式（CSV、Excel）
- 智能處理空白值和資料清理

## 支援格式

- CSV檔案 (.csv)
- Excel檔案 (.xlsx, .xls)

## 授權

本工具為開源軟體，可自由使用和修改。
