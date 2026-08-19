# 馬卡龍 2D 畫廊與驗收標準

狀態：Canonical

最後核對：2026-08-19

## 文件責任

本文件持有作品詳情頁的多圖 2D 畫廊、runtime 資產、全螢幕檢視互動、圖片傳輸處理與交付驗收規則。十顆馬卡龍的口味、色彩、內餡與裝飾設計仍由 [`macaron-visual-system.md`](macaron-visual-system.md) 持有；作者提供的專案文案是文字真相，不在本文件重寫。

作品詳情不再以 3D 模型呈現馬卡龍。repository 內既有 `.blend`、`.glb`、texture 與 Blender script 不得由作品詳情 runtime 載入，也不能被當成新的畫廊設計真相。唯一例外是首頁信件結語的紫夜兔耳馬卡龍 3D viewer；它只在使用者明確按下載入按鈕後請求 viewer runtime 與 GLB，且不改變本文件持有的作品詳情 2D 畫廊契約。

## 畫廊內容結構

每顆作品詳情使用一組可左右切換的圖片，預設順序為：

1. 馬卡龍正式預設視角。
2. 馬卡龍多視角圖。
3. 作者提供的專案畫面；張數依該作品內容決定。

第一張正式預設視角的 caption 必須直接引用 `src/data/macaronIdentity.ts` 中該 slug 的正式馬卡龍名稱；首頁口味標註則引用同一筆 identity 的正式口味。名稱與口味是兩個不同欄位，不得把造型名稱改寫成另一種口味，也不得在畫廊 registry 另存一份可漂移的正式名稱。

窗邊手記是第一個完成的詳情頁，route 為 `#/macarons/window-notes`，runtime 圖片由 `assets/galleries/window-notes/` 持有，順序為：

1. `default-view.webp`
2. `three-views.webp`
3. `homepage.webp`
4. `skills.webp`
5. `mobile-story.webp`

兔子的祕密檔案 route 為 `#/macarons/boundary-notes`，runtime 圖片由 `assets/galleries/boundary-notes/` 持有，順序為：

1. `default-view.webp`
2. `three-views.webp`
3. `guardian-rabbit.webp`
4. `boundary-file.webp`
5. `mobile-languages.webp`
6. `share-image.webp`

冷凍兔肉的巧匠工坊 route 為 `#/macarons/frozen-rabbit-workshop`，runtime 圖片由 `assets/galleries/frozen-rabbit-workshop/` 持有，順序為：

1. `default-view.webp`
2. `three-views.webp`
3. `prep-workbench.webp`
4. `todo-list.webp`
5. `mobile-languages.webp`

冷凍兔肉的大地秘笈 route 為 `#/macarons/frozen-rabbit-tome`，runtime 圖片由 `assets/galleries/frozen-rabbit-tome/` 持有，順序為：

1. `default-view.webp`
2. `three-views.webp`
3. `clear-entry.webp`
4. `solver-results.webp`
5. `mobile-languages.webp`

LinkArray route 為 `#/macarons/link-array`，runtime 圖片由 `assets/galleries/link-array/` 持有，順序為：

1. `default-view.webp`
2. `three-views.webp`
3. `structure-explainer.webp`
4. `operation-complexity-en.webp`
5. `refactored-area.webp`
6. `refactored-area-en.webp`

操作複雜度與重構區圖解各自只佔一個畫廊項目，並依目前 `zh`／`en` 語系切換對應圖片；切換語系時不得同時展示兩種語言，也不得改變目前的畫廊索引。

Dandelifeon route 為 `#/macarons/dandelifeon`，runtime 圖片由 `assets/galleries/dandelifeon/` 持有，順序為：

1. `default-view.webp`
2. `three-views.webp`
3. `perfect-board.webp`

nAnB route 為 `#/macarons/nanb`，runtime 圖片由 `assets/galleries/nanb/` 持有，順序為：

1. `default-view.webp`
2. `three-views.webp`
3. `game-screen.webp`
4. `clipboard-result.webp`

75% Alchohol route 為 `#/macarons/75-alchohol`，runtime 圖片由 `assets/galleries/75-alchohol/` 持有，順序為：

1. `default-view.webp`
2. `three-views.webp`
3. `website.webp`

50 Hiragana Test route 為 `#/macarons/50-hiragana-test`，runtime 圖片由 `assets/galleries/50-hiragana-test/` 持有，順序為：

1. `default-view.webp`
2. `three-views.webp`
3. `website.webp`

`src/data/macaronDetails.ts` 是詳細頁內容 registry，持有每個作品的 slug、雙語文案、連結、圖片順序、alt 與 caption；只有已登錄的作品才會開放首頁卡片連結與 `#/macarons/:slug` route。`src/components/MacaronDetailPage.vue` 持有跨作品共用的詳細版型，`src/components/MacaronGallery.vue` 持有跨作品共用的畫廊互動，`src/App.vue` 只負責依 route 選擇首頁或已登錄的詳細內容。

`src/data/macaronPalette.ts` 是首頁馬卡龍卡片與詳細頁畫廊共用的背景色 owner；兩個 surface 必須引用同一筆 light／dark 色彩，不得各自複製色碼。透明馬卡龍圖片會直接露出畫廊 surface，因此詳細頁沿用首頁卡片的同一組 radial glow 與背景色混合方式，不使用全站固定的紫色畫廊底。

作品詳情是專注閱讀模式：不顯示首頁的品牌、語言與主題導覽列，只保留一個返回入口。作者文字在 DOM 與視覺順序都先於畫廊；畫廊是支持敘事的證據，不與標題、正文爭奪主角位置。

作品對外的 GitHub repository 與 Live Website 連結放在文字區塊結尾，使用簡潔文字連結而非大型按鈕或卡片，並在新分頁開啟。

首頁中已開放的作品卡以整張卡為連結點擊區，不把進入詳情的互動限制在底部 CTA；連結仍需保留鍵盤 focus 與清楚焦點樣式。

## 詳細頁固定慣例

窗邊手記與兔子的祕密檔案共同使用的現行結構已底定，後續馬卡龍詳細頁預設沿用，不為單一作品另建近似版型：

1. 頁首只保留返回首頁入口；主要內容由作者文字與 2D 畫廊組成。手機版返回入口固定在 viewport 頂端，向下閱讀時不得隨頁面捲出畫面，也不得遮住主要內容。
2. 作者文字依序為 category、title、段落、closing quote、外部連結；不得在未經指示時增設摘要卡、功能標籤、額外 CTA 或首頁導覽。
3. 桌機使用文字在左、畫廊在右的雙欄閱讀順序；窄於既有 breakpoint 時轉為單欄，仍保持文字先於畫廊。
4. 中文與英文共用同一版型。中文保留作者原文；英文以保留語意的精簡翻譯控制高度。桌機雙欄版在 100% zoom 的 `1440 × 900` 與 `1920 × 900` viewport 中，`document.documentElement.scrollHeight` 必須小於或等於 `clientHeight`，不得出現頁面垂直捲軸。這是內容高度契約；不得以隱藏 scrollbar、縮小既定字級、壓縮畫廊或裁切內容通過。平板與手機轉為單欄後允許自然垂直閱讀，但仍不得出現橫向捲軸。
5. 畫廊背景使用 `src/data/macaronPalette.ts` 中該 slug 的 light／dark 色彩，並與首頁 `.signature-art` 使用相同的 glow 與混色規則；透明圖片在首頁卡片與詳細頁中必須呈現一致背景，不為單一詳情另配色。
6. 圖片張數依作品內容決定，但前兩張仍是正式預設視角與多視角圖；後續圖片以專案敘事順序排列。
7. 新作品只在 `src/data/macaronDetails.ts` 登錄資料、在 `src/data/macaronPalette.ts` 登錄共用背景色，並新增 `assets/galleries/<slug>/` runtime 資產；共用結構由 `MacaronDetailPage.vue`、共用互動由 `MacaronGallery.vue` 持有。只有需求真正改變共用契約時才修改這兩個元件。

若使用者明確要求不同敘事結構，可以提出可逆差異；未取得新指示時，以上是後續詳細頁的 default，而不是重新設計的起點。

## 多視角圖契約

- 以正式 current asset 為第一真相來源，不以舊模型、生成結果或暫存截圖推翻它。
- 使用寬幅非對稱構圖：預設三分之四視角約佔左側三分之二，尺寸最大。
- 右側上下排列兩張較小視角：頂面在上；正常平放、餡料水平延伸的正側面在下。
- 多視角圖不得出現標籤、箭頭、邊框、水印或額外道具。
- 多視角圖使用真實 alpha 透明底，不得將白底、棋盤格或落地陰影烘進圖片。
- 殼色、內餡層序、果膠位置、主裝飾、數量、色序與手繪材質逐項對回正式 current asset。
- 各角度只顯示物理上合理可見的元素；不能把被遮住的正面裝飾硬貼到側面。

## 圖片傳輸處理

- 原始 PNG 或作者提供的截圖先保留，不直接作為 runtime 大圖引用。
- 使用 `scripts/prepare_gallery_image.py` 依實際原始尺寸轉為 metadata-free WebP；不得放大低解析度來源。
- 產生器若無法直接輸出 alpha，可先要求單色 chroma key 背景，再使用 `--extract-green-background` 抽出與圖片邊緣連通的綠幕；主體內部的綠色裝飾必須保留，不得把棋盤格、色鍵或背景延伸瑕疵留在 runtime 資產。
- 馬卡龍多視角圖若取得的是暖白／暖象牙背景，保留該張已通過設計檢查的圖，不要為了透明度重新生成主體。使用 `python scripts/prepare_gallery_image.py <source> <destination> --quality 90 --extract-light-background`，將與圖片邊緣連通的淺暖色背景轉成 alpha；這是 Frozen Rabbit Tome 三視圖實際採用並成功的處理方式。
- 不以圖片預覽器顯示的底色判斷去背是否成功；透明像素仍可能保留原本的 RGB，部分預覽器會把這些 RGB 顯示成暖白背景。必須直接讀取輸出 WebP 的 alpha channel，確認模式為 `RGBA`、alpha extrema 同時包含 `0` 與 `255`，再到實際畫廊背景上檢查輪廓。若 alpha 已正確，不再重跑 image generation；重新生成可能改變馬卡龍光線、材質或裝飾，且仍不保證輸出真正透明。

  ```powershell
  python -c "from PIL import Image; image=Image.open(r'<destination>'); print(image.mode, image.getchannel('A').getextrema())"
  ```

  預期輸出為 `RGBA (0, 255)`；Frozen Rabbit Tome 的 `three-views.webp` 以此方式確認透明度。

- 馬卡龍與多視角插畫預設使用 quality 90；有細字的專案截圖可在目視確認後使用 quality 86–90。
- 必須保留原始長寬比，不裁掉使用者畫面、文字或馬卡龍輪廓。
- 交付時比較來源與 runtime 檔案尺寸，並在實際畫廊與全螢幕放大狀態確認沒有明顯壓縮瑕疵。

## 互動與可及性

- 畫廊只保留上一張、下一張、文字 caption 與位置計數；不重複增加可直接跳轉的裝飾性分頁列。
- 從首頁作品卡進入詳情時記住當下的頁面捲動位置；使用詳情返回入口或瀏覽器上一頁回到首頁後，必須恢復到進入詳情前的位置。直接開啟詳情頁時仍從頁首開始。手機版返回入口在詳細內容捲動期間保持固定於 viewport 頂端，且不可造成內容遮擋或橫向 overflow。
- 一般畫廊與全螢幕檢視都支援水平滑動切圖：觸控裝置使用手指 swipe，桌機使用滑鼠拖曳；目前圖片與相鄰圖片必須在拖曳過程中連續跟隨指標，讓切換方向的下一張從畫面邊緣漸進進入。達到切換門檻後，放手須從當前位置一次滑到終點並在終點無動畫重置軌道，不得先回彈或讓下一張再次進場；未達門檻時才回到原位。一般畫廊保留垂直頁面捲動；全螢幕放大後先平移圖片，到達左右邊界後繼續向外拖曳則漸進轉為切圖手勢。
- 進入詳情後預先下載並解碼該畫廊的全部圖片；切圖時仍須確認目標圖片已就緒，再一次更新圖片、caption 與計數。
- 目標圖片尚未就緒時保留目前圖片與計數，顯示克制的載入狀態並暫停重複切換；載入失敗不得提前改動 caption 或計數。
- 點擊主圖開啟覆蓋整個 viewport 的全螢幕檢視；背景頁面停止捲動。
- 全螢幕的 100% 狀態必須完整容納任何橫式、方形或直式圖片，不得以寬度撐滿造成上下裁切。
- 全螢幕模式支援按鈕與滾輪縮放、滑鼠／觸控平移、雙指縮放、重設，以及明確的退出按鈕；目前圖片的 caption 必須保持可見，並與切圖、計數及縮放收斂在同一個底部區域，不把 caption、箭頭與縮放拆散到四周。
- 全螢幕覆蓋層必須阻止行動瀏覽器的雙擊頁面縮放；圖片仍保留畫廊自行處理的雙擊縮放與雙指縮放，不能讓 viewport 被瀏覽器放大後失去退出路徑。
- 鍵盤支援 `ArrowLeft`、`ArrowRight`、`+`、`-` 與 `Escape`；離開後焦點回到原本的開啟按鈕。
- 圖片需要對應目前語言的 alt 與 caption；只有裝飾性圖像才能使用空 alt。
- 手機控制不能遮住主要內容，所有可點擊控制保留合理觸控尺寸，且不得造成橫向 overflow。

## 文字與跨語言

- 中文以作者提供文案為準，除了明確錯字與錯誤標點，不改寫語氣、內容、段落意圖或品牌名稱。
- 英文需要保留中文的語意與意境，同時控制篇幅，使兩種語言能共用同一套版面。
- 任何可見文字增減都必須依 [`macaron-visual-system.md`](macaron-visual-system.md) 重建字型 subset 並確認無缺字。

## 交付閘門

1. `npm run build`、`git diff --check` 與資產路徑檢查通過。
2. 桌機、平板、手機與明暗主題都完成實際 browser QA，沒有裁切、溢出、缺字、錯誤 fallback 或控制遮擋；桌機另以中英文逐一驗證 `1440 × 900`、`1920 × 900`，確認 root `scrollHeight <= clientHeight` 且畫面沒有垂直捲軸。
3. 逐張切換圖片，確認一般畫廊與全螢幕的 caption、計數、alt 與圖片順序正確。
4. 實際開啟全螢幕，驗證滑鼠滾輪、按鈕、拖曳、雙指、鍵盤切圖與退出路徑。
5. 放大檢查馬卡龍線條、截圖細字與生成多視角圖，確認 WebP 壓縮沒有造成不可接受的品質下降；同時比對首頁卡片與詳細頁畫廊在 light／dark theme 下的背景，確認透明圖片露出的色彩一致。
