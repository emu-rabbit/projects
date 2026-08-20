# GitHub Pages 多語路由與 SEO 契約

狀態：Canonical

最後核對：2026-08-20

## 責任範圍

本文件持有作品集在 GitHub Pages 上的公開 URL、語言分流、搜尋 metadata、結構化資料、sitemap、robots 與社群分享預覽契約。作品內容由 `src/data/macaronDetails.ts` 持有，馬卡龍視覺規格由 `docs/macaron-visual-system.md` 持有；本文件不重複這兩者的內容真相。

正式站點基底為 `https://emu-rabbit.github.io/projects/`，Vite runtime base 為 `/projects/`。

## 公開 URL

| 頁面 | 中文 | 英文 |
| --- | --- | --- |
| 首頁 | `/projects/zh/` | `/projects/en/` |
| 作品詳情 | `/projects/zh/macarons/:slug/` | `/projects/en/macarons/:slug/` |

- `src/routing/portfolioRoute.ts` 是 runtime URL parser 與 builder。
- 每個語言網址都必須能直接載入、重新整理與分享，不依賴 hash 才能找到內容。
- `/projects/` 只負責依瀏覽器語言導向 `/projects/zh/` 或 `/projects/en/`，並標記 `noindex`；可索引頁面只有語言首頁與已登錄作品詳情。
- 舊的 `#/macarons/:slug` 連結只作相容性遷移，載入後以 `history.replaceState` 換成對應語言的 clean URL；它不是 canonical URL。
- 語言切換維持同一頁面與同一 slug，並以 `hreflang` 連到另一語言版本。

## SEO 資料與輸出

- `src/data/seo.json` 是雙語 SEO title、description、keywords、圖片 alt、作品分類、色票與結構化資料欄位的單一資料來源。
- `src/data/seo.ts` 在 SPA 導航時同步 `<title>`、description、keywords、canonical、hreflang、Open Graph 與 Twitter metadata。
- `scripts/build-seo.mjs` 在 `vite build` 後產生 22 個可直接讀取的 HTML：兩個語言首頁與十個作品的雙語詳情；每頁包含唯一 title、description、canonical、hreflang、Open Graph、Twitter Card、JSON-LD 與無 JavaScript 的可爬連結。
- `dist/sitemap.xml` 列出上述 22 個 canonical URL，`dist/robots.txt` 宣告 sitemap；根頁與 404 fallback 不加入 sitemap。
- `meta name="keywords"` 只作內容治理與非 Google 搜尋系統的輔助訊號；不能把它當成 Google 排名保證。可搜尋性主要依靠可直接存取的 URL、語意內容、title、description、內部連結、canonical、hreflang、結構化資料與 sitemap。

## 分享預覽圖片

- 所有分享圖固定為 1200 × 630 PNG，公開於 `public/social/{language}/`。
- 第一階段只啟用兩張首頁預覽：`zh/home.png` 與 `en/home.png`。作品詳情目前也引用各自語言的首頁圖；十個作品的雙語圖檔保留在同一目錄，尚未作為 metadata 啟用。
- 首頁展示圖來源為 `assets/seo/home-macaron-product-shot.png`；它使用四顆馬卡龍的自然 2×2 產品陳列，並由 `scripts/generate_social_previews.py` 嵌入雙語版面。
- `python scripts/generate_social_previews.py` 預設只重建兩張已啟用的首頁圖；加入 `--all` 才會連同二十張保留中的作品圖一起重建。
- 首頁與各作品標題使用受控行分組，不依賴任意字元截斷；產生器必須在 1200 × 630 畫布內保證沒有文字爆版、裁切或超出邊界。

## 建置與驗證

- `npm run build` 依序執行 typecheck、Vite build、SEO 靜態頁產生與 `scripts/verify-seo.mjs`。
- `scripts/verify-seo.mjs` 驗證 22 個 route 的 metadata、canonical、hreflang、Open Graph、Twitter Card、JSON-LD、無 JavaScript 連結、sitemap、robots，以及兩張已啟用首頁預覽的 1200 × 630 尺寸。
- GitHub Actions 以 `SITE_URL` 與 `VITE_SITE_URL` 指向正式 Pages URL；若 fork 或站點路徑改變，兩者與 Vite base 必須一起更新。
- UI 或路由變更仍需用實際瀏覽器檢查中文／英文首頁、直接載入作品詳情、語言切換、返回首頁、桌機與手機溢出，以及 console 錯誤。
