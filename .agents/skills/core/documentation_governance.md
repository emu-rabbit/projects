# 文件庫治理規範

## 文件角色

本文件規範 Agent 如何新增、更新、拆分、移動與移除 repository 的持久文件。目標是維持清楚的資訊架構與單一真相來源，不是要求每次任務都增加文件。

## 觸發條件

只有下列情況需要讀取並執行本規範：

- 任務明確要求建立、整理或更新文件。
- 程式、產品行為、資料、架構或 workflow 的持久契約已改變。
- 使用者確認新的長期目標、限制或非目標。
- 現有文件與實際 code/config、其他 canonical 文件或使用者最新指示衝突。

純問答、診斷、review、臨時探索或未改變持久契約的修正，不需要為了程序更新文件，也不必固定回報「無需更新」。

## 核心原則

### 單一 canonical owner

每一項持久真相只能有一個 canonical owner。其他文件可以說明何時應讀取該 owner、提供一行摘要或使用相對路徑連結；不得複製完整規則、數值、步驟或長篇摘要。

### 文件分類與責任

| 類型 | Canonical responsibility | 不應承載 |
| --- | --- | --- |
| `AGENTS.md` | 入口、優先級、任務路由、安全摘要、驗證入口 | mission、feature、architecture 的完整副本 |
| `mission/` | 產品目的、使用者價值、非目標、長期語氣 | route、CSS selector、runtime implementation |
| `skills/core/` | Agent 的共通操作與文件治理 | 產品或 feature 規格 |
| `skills/professional/` | 跨功能的開發、UI、architecture 原則 | 單一頁面的完整 layout |
| `skills/domain/` | 無法只靠通用工程知識補完的領域判斷 | runtime schema 或部署步驟 |
| `specs/` | 功能行為、資料契約、相容性與 feature UX | Agent 共通工作方式 |
| `workflows/` | 有觸發條件、輸入、步驟、驗證與輸出的操作流程 | 產品使命或聊天紀錄 |
| `subagents/` | 委派條件、必要來源、輸入輸出與 handoff contract | 已由 skill/spec 擁有的完整專業知識 |

本機 PATH、sandbox、npm shim、GUI 或平台 workaround 屬於 user/machine-level guidance，不應複製到 repository 文件。

## 規則層級

- **Invariant**：沒有明確授權不得偏離的安全、production、隱私、資料或產品底線。
- **Default**：目前偏好的設計或實作方向；有更好證據時可提出替代。
- **Snapshot**：會隨 code、config、版本或環境改變的現況；必須附驗證來源，必要時加 `last_verified`。

不得把 snapshot 用永久命令語氣複製到多份文件，也不得把一次 UI 修正自動升格為跨功能 invariant。

## 更新前檢查

更新文件前依序回答：

1. 這是持久真相，還是只屬於本次任務？
2. 能否由 code、schema、test、type system 或 config 直接保護？若可以，文件只保留目的與 owner。
3. 它屬於 invariant、default 還是 snapshot？
4. 現有 canonical owner 是哪一份文件？
5. 寫入後是否會與其他文件重複、矛盾或跨越責任？
6. 哪些直接引用或摘要需要同步調整？

找不到 owner 時，先檢查是否應擴充現有文件分類。只有通過「新文件守衛」後才建立新檔。

## 更新操作

1. 修改 canonical owner。
2. 用 `rg` 搜尋關鍵詞、舊名稱、數值、路徑與直接引用。
3. 檢查 owner 的第一層引用文件。
4. 移除競爭版本；需要保留導覽時改為短連結。
5. 檢查 code/config/tests 是否仍是實際 source of truth。
6. 執行文件驗證並回報真正改變的文件。

只有使用者明確要求文件治理、milestone audit，或局部修正無法消除責任衝突時，才進行全庫結構調整。結構性更新必須列出舊 owner、新 owner、移動內容與受影響引用，並搜尋失效路徑與孤兒文件。

## 新文件、移除與歷史

建立新文件前必須同時符合：有明確且獨立的 responsibility、會被一類可辨識任務重複使用、放入現有 owner 會破壞責任邊界、不是聊天摘要或暫時狀態，且已決定由 `AGENTS.md` 或哪一份 owner 路由到它。

過期規則應直接修正或移除，不以舊版規則長期堆疊在 canonical 文件。

## 驗證清單

文件更新完成後至少檢查：

- `rg` 找不到被刪除或移動文件的失效引用。
- 同一規則沒有多份完整 owner。
- `AGENTS.md` 能把任務路由到新的 canonical owner。
- Markdown、TOML 與相對路徑可讀。
- UTF-8 without BOM。
- `git diff --check` 無 whitespace error。
- `git diff` 只包含本次文件治理範圍。

若文件描述 current behavior，還要用對應 code、config、tests 或 live surface 驗證；不能只做文件彼此的一致性檢查。
