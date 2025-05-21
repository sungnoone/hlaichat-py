# HLAIChat 前端

這是 HLAIChat 管理平台的前端部分，使用 Vue.js 3 和 Vuetify 3 開發。

## 專案結構

```
frontend/
├── public/             # 靜態資源
├── src/                # 源代碼
│   ├── assets/         # 靜態資源
│   ├── components/     # 組件
│   │   ├── AdminLayout.vue  # 管理員布局
│   │   └── UserLayout.vue   # 使用者布局
│   ├── router/         # 路由配置
│   ├── views/          # 視圖
│   │   ├── admin/      # 管理員視圖
│   │   │   ├── Dashboard.vue       # 儀表板
│   │   │   ├── Users.vue           # 使用者管理
│   │   │   ├── Groups.vue          # 群組管理
│   │   │   ├── ChatLinks.vue       # 聊天連結管理
│   │   │   ├── ADConfig.vue        # AD 設定
│   │   │   ├── Logs.vue            # 操作紀錄
│   │   │   └── Profile.vue         # 個人設定
│   │   └── user/       # 使用者視圖
│   │       ├── UserDashboard.vue   # 使用者儀表板
│   │       ├── UserProfile.vue     # 使用者個人資料
│   │       └── UserHistory.vue     # 使用者使用紀錄
│   ├── App.vue         # 根組件
│   └── main.js         # 入口文件
├── index.html          # HTML 模板
├── package.json        # 依賴配置
└── vite.config.js      # Vite 配置
```

## 安裝與執行

1. 安裝依賴：

```bash
npm install
```

2. 啟動開發伺服器：

```bash
npm run dev
```

3. 構建生產版本：

```bash
npm run build
```

4. 預覽生產版本：

```bash
npm run preview
```

5. 代碼檢查：

```bash
npm run lint
```

## 技術堆疊

- **框架**：Vue.js 3
- **UI 元件**：Vuetify 3
- **路由**：Vue Router
- **HTTP 請求**：Axios
- **圖表**：Chart.js 和 Vue-ChartJS
- **日期處理**：date-fns
- **圖標**：Font Awesome 6 和 Material Design Icons
- **構建工具**：Vite

## 功能說明

### 管理員功能

- **儀表板**：顯示系統概況和統計資料
- **使用者管理**：管理平台使用者和 AD 使用者
- **群組管理**：管理平台群組和權限
- **聊天連結管理**：管理 AI 聊天流程對話網址
- **AD 設定**：設定 AD 連線參數
- **操作紀錄**：查詢使用者操作紀錄
- **個人設定**：管理個人資料和密碼

### 使用者功能

- **使用者儀表板**：顯示可用的聊天連結
- **使用者個人資料**：管理個人資料和密碼
- **使用者使用紀錄**：查詢個人操作紀錄

## 後端API整合

前端使用Axios與後端API通信，API基礎URL為`/api`。在開發模式下，請求會通過Vite的代理功能轉發到後端服務。

## 生產部署

構建完成後，將`dist`目錄下的文件部署到靜態文件服務器或將其複製到後端的靜態文件目錄中。 