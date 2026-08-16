# Agent 工作指南

## 文件範圍

這份文件是本 repository 的 Agent 入口，只保存跨專案可重用的工作方式、文件路由、安全摘要與驗證要求。它不假設本專案的使命、產品行為、技術棧、部署環境、資料模型或 UI 語言；這些內容若日後需要，應由使用者明確提供，並放在責任清楚的 canonical owner。

若本文件與使用者當次明確指示衝突，以使用者指示為準；若涉及安全、資料邊界、外部狀態或授權範圍，不能自行擴大解讀。

## Canonical 文件路由

開始任務時只讀取與任務相關的文件，不把整個 `.agents` 當成固定上下文：

| 任務 | Canonical owner |
| --- | --- |
| Agent 如何理解、執行與交付任務 | `.agents/skills/core/operating_contract.md` |
| 持久文件的 owner、更新、移動與驗證 | `.agents/skills/core/documentation_governance.md` |
| 程式碼、設定、測試與建置的通用標準 | `.agents/skills/professional/development_standards.md` |
| `add and commit all`、`commit all` 或全部提交 | `.agents/workflows/add-commit-all.md` |
| 作品集使命、內容範圍、專案分級與 GitHub 背景 | `docs/product-direction.md` |
| 十顆馬卡龍的統一視覺系統、個別設計、2D 資產、字型 subset 與 UI 視覺驗收 | `docs/macaron-visual-system.md` |
| 馬卡龍 3D 建模、共用圓蓋、對圖標準、常見失敗與模型交付驗收 | `docs/macaron-3d-acceptance.md` |

本 repository 的作品集使命、馬卡龍視覺系統與 3D 驗收標準由上表三份 `docs/` 文件持有；尚未定義實作架構、部署、資料模型或專案專屬 subagent 文件。不得把 sibling repository 的假設當成本 repository 的設定。

## 工作方式

- 先確認使用者要得到的結果、限制、非目標與可接受的證據，再決定實作方式。
- 以實際 code、config、tests、built output 或 live surface 為準；文件記憶與舊摘要只能協助路由，不能取代 current-state 驗證。
- 用 `rg` 搜尋 code、文件與引用；只讀取與任務關聯的上下文。
- 先檢查工作樹與變更邊界。既有 modified、staged、untracked 內容預設屬於使用者或其他工作，不得擅自刪除、覆寫或提交。
- 維持最小且完整的 scope；沿用既有 owner、資料流、元件與工具，只有真實重複或複雜度存在時才增加抽象。
- 對 state-dependent 行為使用明確的 domain state，不以 falsy 值、模糊 fallback 或過度寬鬆的條件代替規則。
- 對使用者提供的品牌、標題、文案、命名與互動意圖精準保留，不用泛化措辭取代。
- 以風險決定驗證深度：文件做 diff、引用、編碼與格式檢查；程式邏輯做 tests/typecheck；建置、資料、UI 或部署依實際風險增加 build、browser、rules 或 live 驗證。
- 分類 sandbox、權限、網路、平台與程式錯誤；環境工具失敗不是修改產品邏輯的理由。
- 沒有完成的驗證、外部阻塞、殘留風險與未處理工作，必須在交付時清楚說明。

## 文件治理

- 長期真相只保留一個 canonical owner；`AGENTS.md` 只負責入口與路由，不複製完整 mission、feature、architecture 或 current-state。
- 只有持久契約、長期目標、限制或非目標改變時才更新 `.agents` 文件；單次問答、診斷或局部修正不必為了程序新增文件。
- 文件描述 current behavior 時，必須附可重查的 code/config/test owner；不要把 snapshot 寫成永久命令。

## 語言與回報

- 使用者可見回覆與 repository 文件預設使用自然繁體中文。
- 技術關鍵字、commands、API、套件、code identifiers 與既定名稱保留原文。
- 回覆先交代結果與重要判斷，再提供必要的驗證證據、殘留風險與後續工作；避免無意義的程序流水帳。
- 若使用者表示會自行進行實際瀏覽器或視覺驗收，停止替代性的主觀驗收，改提供 code review、機械測試與 build 證據。

## 編輯與安全

- 搜尋優先使用 `rg`／`rg --files`；編輯文字檔優先使用 `apply_patch`。
- 不使用 destructive Git 操作或廣泛刪除來清理不確定的內容；需要這類操作時，先確認精確目標與使用者授權。
- 不因任務需要而自行 push、deploy、傳送外部訊息、改變權限或修改外部系統；這些都是獨立的授權邊界。
- 任何提交前都要重新檢查 staged diff，確認沒有混入其他工作。

## 初始化狀態

本 repository 目前只初始化了通用 Agent 治理文件，沒有預設任何產品使命或技術內容。當使用者提供專案專屬真相時，請新增對應 owner，更新本入口的路由，並保持通用工作規則與專案內容分離。
