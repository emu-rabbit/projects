# 馬卡龍作品集產品方向

狀態：Canonical

最後核對：2026-08-19

## 產品使命

這個專案是絵夢羽さ沂的個人作品集。它不把作品排列成一般的軟體專案卡片，而是把一間已經收攤、但仍被喜愛與記得的馬卡龍店所留下的感受，轉化成一盒屬於自己的數位馬卡龍。

首批作品集固定收錄十個作品；每個作品都是一顆具有獨立口味、色彩、內餡結構與記憶點的馬卡龍。甜點不是與內容分離的裝飾，而是作品本身的敘事介面：外殼傳達品牌與第一印象，內餡解釋產品真正做的事，表面裝飾留下最值得記住的特徵。

作品詳情一律使用多張 2D 圖片組成的畫廊呈現：由馬卡龍預設視角與多視角圖建立甜點印象，再以實際專案截圖和作者親自撰寫的介紹，讓訪客看見作品與創作者本人的關係。網站不再以 3D 模型作為馬卡龍展示方向。

## 內容分級

### 主要焦點專案

- Frozen Rabbit Workshop
- Frozen Rabbit Tome
- Boundary Notes
- Emu Rabbit Github io

這四顆是作品集的招牌款。它們需要比其他作品多一層精緻度與故事性，但仍遵守同一套手作甜點語言，不能靠大量珠寶、金屬或複雜小物製造「高級感」。

### 技術實驗專區

- LinkArray
- Vue Router Rule
- Dandelifeon

這三顆強調一個清楚的技術概念或實驗機制。視覺應讓人先記得「鏈結、路由分支、演算法棋盤」之一，不把 README 全部畫在甜點上。

### 早期小作品

- nAnB
- 75% Alchohol
- 50 Hiragana Test

這三顆保留早期作品的直接、輕巧與練習感。它們不是需要被重新包裝成大型產品的招牌款；較低的裝飾密度是刻意的層級差異，而不是完成度不足。nAnB 可以保留夢夢與聊天室的角色性，但不需要以技術實驗款的機關密度呈現。

## 體驗原則

1. **先看見一盒收藏，再認識每個作品。** 十顆必須先被感知為同一位創作者、同一間數位甜點店的作品。
2. **甜點結構必須能解釋產品。** 顏色只負責辨識；內餡、切層與單一主裝飾才負責說明功能與個性。
3. **招牌款精緻，但不靠堆疊。** 特別感來自構圖、節奏、材質與一個被好好完成的主題，不來自更多裝飾。
4. **多視角仍共用同一份 2D 設計真相。** 頂面、側面與衍生構圖不能改變預設視角的殼、餡、糖片、果膠、擠花、數量與色序。
5. **保留手作與人的痕跡。** 略歪的殼、厚薄不完全一致的餡、暖棕線條與不均勻顏料，是這個作品集的溫度；衍生視角不能把它磨成制式商品渲染。
6. **桌機、平板與手機都是正式支援面。** 每個通過驗收的區塊都必須在三種裝置上維持清楚的資訊層級、舒適的閱讀與操作節奏、完整的核心視覺，且不得出現橫向溢出；不能把其中一種尺寸視為其他版面的單純縮放或事後補丁。目前實作由 `src/styles.css` 的 responsive rules 與實際 viewport 驗收保護。
7. **進入詳情就是專注閱讀。** 詳情頁不延續首頁導覽列；作者文字是主角，畫廊只提供支持敘事的視覺證據，介面控制以能完成任務的最少數量呈現。

## 十個作品的 GitHub 背景與作品集解讀

以下是 2026-08-14 依各 repository README 核對的 current-state 摘要。功能會演進；來源連結是之後重查的 owner。

| 分級 | 作品 | GitHub 背景 | 放進作品集時要說清楚的核心 |
| --- | --- | --- | --- |
| 主要焦點 | [Frozen Rabbit Workshop](https://github.com/emu-rabbit/frozen_rabbit_workshop) | 使用 Vue 3 + Vite 製作的 FFXIV 製作／採集備料工具；能拆解大型製作目標、分配購買／製作／採集／庫存、估算市場成本與時間，並產生行動清單。 | 把龐大、混亂的備料工作轉成清楚且可執行的準備路線。 |
| 主要焦點 | [Frozen Rabbit Tome](https://github.com/emu-rabbit/frozen_rabbit_tome) | 面向 FFXIV 採掘師與園藝師的策略工具；依角色與採集點狀態推薦手法，支援一般採集與收藏品策略、機率／風險比較、自訂 rotation 模擬及保存結果。 | 在多個狀態與取捨之間求解、比較，留下可回看的知識。 |
| 主要焦點 | [Boundary Notes](https://github.com/emu-rabbit/boundary_notes) | 使用 Vue 3、TypeScript、Vite 與 Firebase 的私密筆記；協助使用者整理 BDSM 經驗、興趣、界線與重要條件，回看變化，並在選擇時以私密連結分享。 | 提供安靜、尊重且不評判的空間，把感受與界線整理成可溝通的話。 |
| 主要焦點 | [Emu Rabbit Github io](https://github.com/emu-rabbit/emu-rabbit.github.io) | 以 Vite + TypeScript 建立的輕量個人自我介紹網站；透過窗邊手記介紹絵夢羽さ沂的生活、程式工作、遊戲、存錢、約會，以及對愛、自由與誠實的重視。 | 不是平台首頁或履歷摘要，而是一扇讓人能靠近創作者本人的窗。 |
| 技術實驗 | [LinkArray](https://github.com/emu-rabbit/LinkArray) | 探索結合 dynamic array 隨機讀取與 doubly linked list 頭尾操作優點的資料結構；包含手動 `refactor`、自動選擇時機的 AutoLinkArray，以及小資料量先維持原生 array 的 AdaptiveArray。 | 讓節點在「鏈結」與「重新排列成可快速讀取的順序」之間切換。 |
| 早期小作品 | [nAnB](https://github.com/emu-rabbit/nAnB) | 聊天室風格的 nA nB 猜數字機器人；角色夢夢來自作者飼養的黃金鼠，介面靈感來自 Discord 與 Wordle。 | 把規則型猜數字遊戲包裝成與一隻有個性的鼠鼠聊天。 |
| 技術實驗 | [Vue Router Rule](https://github.com/emu-rabbit/vue-router-rule) | Vue Router addon；把容易因授權與商業規則而膨脹的 `beforeEach` navigation guard，改寫成較可讀、可除錯與可維護的規則表達。 | 讓複雜路由判斷分岔後仍能被讀懂與維護。 |
| 技術實驗 | [Dandelifeon](https://github.com/emu-rabbit/Dandelifeon) | 以 Node.js／JavaScript 尋找 Minecraft Botania 的 Dandelifeon 最大 mana 產量；比較隨機生成、simulated annealing 與 genetic algorithm。 | 植物與魔力是外觀，搜尋棋盤最佳解的演算法才是內核。 |
| 早期小作品 | [75% Alchohol](https://github.com/emu-rabbit/75alcohol) | 酒精稀釋計算機；依來源濃度與酒精量、水量或總量其中之一，推算預設 75% 目標的其餘數值；另有最終濃度模擬器。 | 用可見的兩種液體、刻度與比例，直接說明一個實用計算。 |
| 早期小作品 | [50 Hiragana Test](https://github.com/emu-rabbit/50-Hiragana-Test) | 用來練習日文五十音的輕量網頁。 | 一個字、一張練習格就足夠；親切與直接比裝飾更重要。 |

## 已決定與尚未決定

已決定：

- 首批收藏是以上十個作品與三個分級。
- 每個作品對應一顆馬卡龍，並以 `docs/macaron-visual-system.md` 為統一視覺 owner。
- 每顆作品詳情一律使用可左右切換的多圖 2D 畫廊，搭配作者親自撰寫的介紹。
- 畫廊圖片可開啟全螢幕檢視，並支援放大、縮小、平移與明確退出。
- 十個作品都已完成共用版型的詳情頁，runtime route 由 `src/data/macaronDetails.ts` 的 registry 持有。
- 網站不再載入或呈現馬卡龍 3D 模型。
- 四個主要焦點專案的視覺層級最高，但不能破壞整盒一致性。

尚未決定：

- 紙盒場景與音效。
- 部署方式與分析工具。

這些未決定事項不能由目前的 2D 圖或本文件反推成既定需求；進入實作前應由對應 canonical owner 補充。
