# 更新日誌

## 版本 2.0.0 - 2024年12月

### 重大變更

#### 1. 取消 Learning Performance 欄位
- 移除了 `Learning Performance` 欄位的支援
- 簡化了知識點節點的屬性結構

#### 2. IsRoot 改為非必填欄位
- `IsRoot` 欄位從必填改為選填
- 當 `IsRoot` 為空時，屬性為空值（null）
- 更新了必要欄位驗證邏輯

#### 3. 新增中英文並列欄位支援
- 支援新的欄位名稱格式：
  - `主題(Topic)` 或 `Topic`
  - `次主題(Unit)` 或 `Unit`
  - `概念(Concept)` 或 `Concept`
- 向後相容舊的欄位名稱：
  - `第一層知識` → `主題(Topic)`
  - `第二層知識` → `次主題(Unit)`
  - `第三層知識` → `概念(Concept)`

#### 4. 知識層級欄位調整
- 將原本的「第一層知識、第二層知識、第三層知識」調整為「主題(Topic)、次主題(Unit)、概念(Concept)」
- 所有知識層級欄位均為非必填
- 當欄位值為 'x' 時，視為空值處理

#### 5. 知識點唯一性檢查
- 新增知識點名稱唯一性驗證
- 當發現重複的知識點名稱時，會拋出錯誤並指出重複的行號
- 確保資料庫中不會有重複的知識點

### 技術改進

#### 程式碼優化
- 重構了欄位處理邏輯，支援多種欄位名稱格式
- 改進了錯誤處理機制，提供更詳細的錯誤訊息
- 優化了資料驗證流程

#### 向後相容性
- 保持對舊格式檔案的支援
- 自動檢測並處理不同格式的欄位名稱
- 平滑遷移，無需修改現有檔案

### 使用範例

#### 新的檔案格式
```csv
Label,ID,Name,Education System,Subject,IsRoot,Topic,Unit,Concept
KnowledgePoint,KP001,認識1~5的數,國小(Elementary school),數學(Math),TRUE,數,數到10,認識數字
KnowledgePoint,KP002,認識6~10的數,國小(Elementary school),數學(Math),,數,數到10,認識數字
```

#### IsRoot 欄位處理
- `TRUE` → 節點會有 `isRoot: true` 屬性
- `FALSE` → 節點會有 `isRoot: false` 屬性
- 空白 → 節點不會有 `isRoot` 屬性（空值）

#### 中英文並列格式
```csv
Label,ID,Name,Education System,Subject,IsRoot,主題(Topic),次主題(Unit),概念(Concept)
KnowledgePoint,KP001,認識1~5的數,國小(Elementary school),數學(Math),TRUE,數,數到10,認識數字
```

### 錯誤處理

#### 重複知識點名稱
```
ValueError: 知識點名稱重複: '認識1~5的數' (第2行)
```

#### 缺少必要欄位
```
ValueError: 缺少必要欄位: ['Label', 'Name', 'Education System', 'Subject']
```

### 遷移指南

#### 從舊版本遷移
1. **Learning Performance 欄位**：如果您的檔案包含此欄位，請移除或忽略
2. **IsRoot 欄位**：現在是可選的，可以保留或移除
3. **知識層級欄位**：可以繼續使用舊名稱，或更新為新名稱
4. **知識點名稱**：確保所有知識點名稱都是唯一的

#### 建議的檔案格式
- 使用英文欄位名稱以獲得最佳相容性
- 確保知識點名稱唯一
- 使用 'x' 表示空值而不是留空

### 測試

所有新功能都經過了完整測試：
- ✅ 基本轉換功能
- ✅ 中英文並列欄位支援
- ✅ 知識點唯一性檢查
- ✅ 'x' 值處理
- ✅ 向後相容性
- ✅ 錯誤處理

### 範例檔案

請參考 `knowledge_points_example.csv` 檔案，了解新的檔案格式。
