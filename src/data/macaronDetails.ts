import type { Language, Localized } from '../types/portfolio'
import { macaronPaletteBySlug } from './macaronPalette'
import type { MacaronPalette } from './macaronPalette'

type LocalizedText = Localized<string>

export interface MacaronGalleryImage {
  src: string | Localized<string>
  alt: LocalizedText
  caption: LocalizedText
}

export interface MacaronProjectLink {
  href: string
  label: LocalizedText
}

export interface MacaronDetail {
  slug: string
  palette: MacaronPalette
  category: LocalizedText
  title: LocalizedText
  paragraphs: Record<Language, readonly string[]>
  closing: LocalizedText
  galleryLabel: LocalizedText
  gallery: readonly MacaronGalleryImage[]
  links: readonly MacaronProjectLink[]
}

const windowNotesGallery = {
  defaultView: new URL('../../assets/galleries/window-notes/default-view.webp', import.meta.url).href,
  threeViews: new URL('../../assets/galleries/window-notes/three-views.webp', import.meta.url).href,
  homepage: new URL('../../assets/galleries/window-notes/homepage.webp', import.meta.url).href,
  skills: new URL('../../assets/galleries/window-notes/skills.webp', import.meta.url).href,
  mobileStory: new URL('../../assets/galleries/window-notes/mobile-story.webp', import.meta.url).href,
} as const

const boundaryNotesGallery = {
  defaultView: new URL('../../assets/galleries/boundary-notes/default-view.webp', import.meta.url).href,
  threeViews: new URL('../../assets/galleries/boundary-notes/three-views.webp', import.meta.url).href,
  guardianRabbit: new URL('../../assets/galleries/boundary-notes/guardian-rabbit.webp', import.meta.url).href,
  boundaryFile: new URL('../../assets/galleries/boundary-notes/boundary-file.webp', import.meta.url).href,
  mobileLanguages: new URL('../../assets/galleries/boundary-notes/mobile-languages.webp', import.meta.url).href,
  shareImage: new URL('../../assets/galleries/boundary-notes/share-image.webp', import.meta.url).href,
} as const

const frozenRabbitWorkshopGallery = {
  defaultView: new URL('../../assets/galleries/frozen-rabbit-workshop/default-view.webp', import.meta.url).href,
  threeViews: new URL('../../assets/galleries/frozen-rabbit-workshop/three-views.webp', import.meta.url).href,
  prepWorkbench: new URL('../../assets/galleries/frozen-rabbit-workshop/prep-workbench.webp', import.meta.url).href,
  todoList: new URL('../../assets/galleries/frozen-rabbit-workshop/todo-list.webp', import.meta.url).href,
  mobileLanguages: new URL('../../assets/galleries/frozen-rabbit-workshop/mobile-languages.webp', import.meta.url).href,
} as const

const frozenRabbitTomeGallery = {
  defaultView: new URL('../../assets/galleries/frozen-rabbit-tome/default-view.webp', import.meta.url).href,
  threeViews: new URL('../../assets/galleries/frozen-rabbit-tome/three-views.webp', import.meta.url).href,
  clearEntry: new URL('../../assets/galleries/frozen-rabbit-tome/clear-entry.webp', import.meta.url).href,
  solverResults: new URL('../../assets/galleries/frozen-rabbit-tome/solver-results.webp', import.meta.url).href,
  mobileLanguages: new URL('../../assets/galleries/frozen-rabbit-tome/mobile-languages.webp', import.meta.url).href,
} as const

const linkArrayGallery = {
  defaultView: new URL('../../assets/galleries/link-array/default-view.webp', import.meta.url).href,
  threeViews: new URL('../../assets/galleries/link-array/three-views.webp', import.meta.url).href,
  operationComplexity: {
    zh: new URL('../../assets/galleries/link-array/structure-explainer.webp', import.meta.url).href,
    en: new URL('../../assets/galleries/link-array/operation-complexity-en.webp', import.meta.url).href,
  },
  refactoredArea: {
    zh: new URL('../../assets/galleries/link-array/refactored-area.webp', import.meta.url).href,
    en: new URL('../../assets/galleries/link-array/refactored-area-en.webp', import.meta.url).href,
  },
} as const

export const macaronDetails = [
  {
    slug: 'window-notes',
    palette: macaronPaletteBySlug['window-notes'],
    category: { zh: '個人網頁', en: 'Personal Website' },
    title: { zh: '絵夢羽さ沂的窗邊手記', en: "Emu-Rabbit's Window Notes" },
    paragraphs: {
      zh: [
        '我其實是一個很愛寫自我介紹的人，每一次的撰寫，都可以讓我在不同的時間點回頭審視自己。我是誰，我是怎樣的人，我喜歡什麼，我討厭什麼，還有最重要的——此時此刻我想往哪裡去。',
        '所以，我好好地做了一個真正屬於我自己的個人頁面，向所有人介紹我自己，讓想認識我的人有扇窗口可以靠近。',
        '即使和 AI 一起協作，也不能在這麼重要的專案裡，遺失屬於我的味道，這是我在做這個專案時最在乎的事。',
      ],
      en: [
        'I love writing introductions. Each one lets me meet myself again: who I am, what I love or dislike, and where I want to go next.',
        'So I made a page that is truly mine—a window for anyone who wants to come closer.',
        'Even with AI, I could not let this project lose the smell that is uniquely mine. That mattered most.',
      ],
    },
    closing: {
      zh: '「那麼，此時此刻的你正在看著我嗎？」',
      en: '“So, at this very moment, are you looking at me?”',
    },
    galleryLabel: {
      zh: '窗邊手記作品畫廊',
      en: 'Window Notes project gallery',
    },
    gallery: [
      {
        src: windowNotesGallery.defaultView,
        alt: { zh: '窗邊手記馬卡龍的預設視角插畫', en: 'Default view illustration of the Window Notes macaron' },
        caption: { zh: '紫夜兔耳馬卡龍', en: 'Purple Night Rabbit Macaron' },
      },
      {
        src: windowNotesGallery.threeViews,
        alt: { zh: '窗邊手記馬卡龍的預設、頂面與平放側面視圖', en: 'Default, top, and flat side views of the Window Notes macaron' },
        caption: { zh: '更多角度的我', en: 'More Angles of Me' },
      },
      {
        src: windowNotesGallery.homepage,
        alt: { zh: '窗邊手記個人網頁的桌機首頁截圖', en: 'Desktop homepage of the Window Notes personal website' },
        caption: { zh: '網頁主視覺', en: 'Website Hero' },
      },
      {
        src: windowNotesGallery.skills,
        alt: { zh: '窗邊手記個人網頁的英文版頁面截圖', en: 'English version of the Window Notes personal website' },
        caption: { zh: '支援英文版', en: 'English Version' },
      },
      {
        src: windowNotesGallery.mobileStory,
        alt: { zh: '窗邊手記個人網頁的手機版頁面截圖', en: 'Mobile layout of the Window Notes personal website' },
        caption: { zh: '支援手機版面', en: 'Mobile Layout' },
      },
    ],
    links: [
      {
        label: { zh: '線上展示', en: 'Live Website' },
        href: 'https://emu-rabbit.github.io/',
      },
      {
        label: { zh: 'Github頁面', en: 'GitHub Repo' },
        href: 'https://github.com/emu-rabbit/emu-rabbit.github.io',
      },
    ],
  },
  {
    slug: 'boundary-notes',
    palette: macaronPaletteBySlug['boundary-notes'],
    category: { zh: 'BDSM整理工具', en: 'BDSM Organizer' },
    title: { zh: '兔子的祕密檔案', en: "Bunny's Secret File" },
    paragraphs: {
      zh: [
        'BDSM的領域，用來表達自己對於各種項目的喜好、邊界的網頁較少，體驗也不佳。所以我結合了各種使用者對於測驗網頁會有的困擾，把這多達幾百個測驗項目，好好地整理、落地成一個網頁。',
        '使用者體驗是我在乎的事，使用者的隱私也有守密兔好好的把關，同時也致力於在免登入的後端中不致被濫用打爆。',
        'BDSM是我最喜歡的興趣，慾望可以是誠實的，有邊界的，也塑造了每個人的特色，使每個人成為了獨一無二的自己。',
      ],
      en: [
        'Few BDSM sites make interests and boundaries easy to express. I organized hundreds of quiz items into one clear experience.',
        'Experience and privacy both matter to me. The Secret-Keeping Bunny protects them, while the login-free backend resists abuse.',
        'BDSM is my favorite interest. Honest desires and clear boundaries make each of us unique.',
      ],
    },
    closing: {
      zh: '「不用怕，我在這裡陪你慢慢梳理這一切。」——守密兔如是說道',
      en: '“Don’t be afraid. I’ll help you sort it out.” — the Secret-Keeping Bunny',
    },
    galleryLabel: {
      zh: '兔子的祕密檔案作品畫廊',
      en: "Bunny's Secret File project gallery",
    },
    gallery: [
      {
        src: boundaryNotesGallery.defaultView,
        alt: { zh: '兔子的祕密檔案馬卡龍預設視角插畫', en: "Default view of the Bunny's Secret File macaron" },
        caption: { zh: '酒紅邊界馬卡龍', en: 'Burgundy Boundary Macaron' },
      },
      {
        src: boundaryNotesGallery.threeViews,
        alt: { zh: '兔子的祕密檔案馬卡龍預設、頂面與平放側面視圖', en: "Default, top, and flat side views of the Bunny's Secret File macaron" },
        caption: { zh: '每個人都有很多不一樣的喜好、邊界', en: 'Different Desires, Different Boundaries' },
      },
      {
        src: boundaryNotesGallery.guardianRabbit,
        alt: { zh: '守密兔陪伴使用者整理祕密檔案的介紹畫面', en: 'The Secret-Keeping Bunny guiding users through their file' },
        caption: { zh: '一路陪伴使用者的守密兔', en: 'A Bunny Who Stays With You' },
      },
      {
        src: boundaryNotesGallery.boundaryFile,
        alt: { zh: '桌機版邊界檔案的焦點喜好與分類畫面', en: 'Desktop boundary file with highlighted interests and categories' },
        caption: { zh: '足夠仔細卻易讀的邊界檔案', en: 'Detailed, Yet Easy to Read' },
      },
      {
        src: boundaryNotesGallery.mobileLanguages,
        alt: { zh: '英文手機版兔子的祕密檔案首頁', en: "English mobile layout of Bunny's Secret File" },
        caption: { zh: '支援四語系與手機版面', en: 'Four Languages, Mobile Ready' },
      },
      {
        src: boundaryNotesGallery.shareImage,
        alt: { zh: '適合分享到社群軟體的祕密檔案圖片', en: 'A Secret File image prepared for social sharing' },
        caption: { zh: '可以生成檔案圖片好放上社群軟體', en: 'Shareable File Images' },
      },
    ],
    links: [
      {
        label: { zh: '線上展示', en: 'Live Website' },
        href: 'https://boundarynotes.com/',
      },
      {
        label: { zh: 'Github頁面', en: 'GitHub Repo' },
        href: 'https://github.com/emu-rabbit/boundary_notes',
      },
    ],
  },
  {
    slug: 'frozen-rabbit-workshop',
    palette: macaronPaletteBySlug['frozen-rabbit-workshop'],
    category: { zh: 'Final Fantasy XIV 巧匠工具', en: 'Final Fantasy XIV Crafting Tool' },
    title: { zh: '冷凍兔肉的巧匠工坊', en: "Frozen Rabbit's Workshop" },
    paragraphs: {
      zh: [
        'FF14是我很愛的遊戲，我喜歡裡面的巧匠職業。然而，巢狀的配方依賴，加上多件裝備要一起製作的時候，備料的過程就成了一種地獄。',
        '大多數的工具都使用巢狀的方式來做UI呈現，但我認為這很理性，卻不太是使用者想看到的東西。憑藉著比起配方依賴關係，更在乎自己要備哪些料，我一刀切地決定：這專案會把巢狀打成平面列表。',
        '最後，當收到大量的感謝和喜愛的時候，是我最有成就感的時刻，也是我更相信程式終究要回到為人服務的這個理念上。',
      ],
      en: [
        'FF14 is a game I love, especially its crafting jobs. But nested recipes make preparing several pieces of gear hell.',
        'Most tools mirror those dependencies with nested UIs. It is logical, but users care more about what to prepare. So I flattened the tree into one list.',
        'The thanks and love I received became my proudest moment—and strengthened my belief that software should serve people.',
      ],
    },
    closing: {
      zh: '「Q：兔肉可以烤來吃嗎？A：不可以。」',
      en: '“Q: Can rabbit meat be roasted? A: No.”',
    },
    galleryLabel: {
      zh: '冷凍兔肉的巧匠工坊作品畫廊',
      en: "Frozen Rabbit's Workshop project gallery",
    },
    gallery: [
      {
        src: frozenRabbitWorkshopGallery.defaultView,
        alt: { zh: '冷凍兔肉的巧匠工坊薄荷青檸馬卡龍預設視角插畫', en: "Default view of Frozen Rabbit's Workshop mint lime macaron" },
        caption: { zh: '薄荷青檸馬卡龍', en: 'Mint Lime Macaron' },
      },
      {
        src: frozenRabbitWorkshopGallery.threeViews,
        alt: { zh: '冷凍兔肉的巧匠工坊馬卡龍預設、頂面與平放側面視圖', en: "Default, top, and flat side views of Frozen Rabbit's Workshop macaron" },
        caption: { zh: '想怎樣備料都可以，計算就交給我', en: 'Prep Your Way. I’ll Do the Math.' },
      },
      {
        src: frozenRabbitWorkshopGallery.prepWorkbench,
        alt: { zh: '冷凍兔肉的巧匠工坊備料台桌機畫面', en: "Frozen Rabbit's Workshop desktop prep workbench" },
        caption: { zh: '詳盡但不會迷路的備料台', en: 'A Detailed, Clear Workbench' },
      },
      {
        src: frozenRabbitWorkshopGallery.todoList,
        alt: { zh: '冷凍兔肉的巧匠工坊平面待辦清單畫面', en: "Frozen Rabbit's Workshop flat checklist" },
        caption: { zh: '簡潔但好用的待辦清單輸出', en: 'A Simple, Useful Checklist' },
      },
      {
        src: frozenRabbitWorkshopGallery.mobileLanguages,
        alt: { zh: '冷凍兔肉的巧匠工坊英文手機版畫面', en: "English mobile layout of Frozen Rabbit's Workshop" },
        caption: { zh: '支援四語系與手機版面', en: 'Four Languages, Mobile Ready' },
      },
    ],
    links: [
      {
        label: { zh: '線上展示', en: 'Live Website' },
        href: 'https://emu-rabbit.github.io/frozen_rabbit_workshop/',
      },
      {
        label: { zh: 'Github頁面', en: 'GitHub Repo' },
        href: 'https://github.com/emu-rabbit/frozen_rabbit_workshop',
      },
    ],
  },
  {
    slug: 'frozen-rabbit-tome',
    palette: macaronPaletteBySlug['frozen-rabbit-tome'],
    category: { zh: 'Final Fantasy XIV 大地工具', en: 'Final Fantasy XIV Gathering Tool' },
    title: { zh: '冷凍兔肉的大地秘笈', en: "Frozen Rabbit's Tome" },
    paragraphs: {
      zh: [
        '一開始要做這個專案，其實低估了它的困難度，不是說技術很難做，而是這東西真的太複雜，也需要高度的正確可靠性。',
        '決定把遊戲中的「收藏品」機制拉進來之後，更是一場風暴，最終我在可行性、使用者體驗、可用性達到了平衡。',
        '打從一開始就知道這專案不會很多人用，後續GA的數字也證明了這點，但我仍舊很喜歡這個專案。它教會了我在設計上降低認知負荷、處理視覺雜音，還有在多項資源中取得平衡，讓一個想法可以真正的落地。',
      ],
      en: [
        'I underestimated this project. The technology was not the hard part; its complexity and need for accuracy and reliability were.',
        "Adding the game's collectable system unleashed another storm. In the end, I balanced feasibility, user experience, and usability.",
        'I knew few people would use it, and the GA numbers proved me right. I still love it. It taught me to reduce cognitive load and visual noise, balance resources, and turn an idea into reality.',
      ],
    },
    closing: {
      zh: '「它對我來說，就像一堂很硬的線性代數，帶我回到過去，然後重新成長。」',
      en: '“To me, it was like a hard linear algebra class—taking me back, then helping me grow again.”',
    },
    galleryLabel: {
      zh: '冷凍兔肉的大地秘笈作品畫廊',
      en: "Frozen Rabbit's Tome project gallery",
    },
    gallery: [
      {
        src: frozenRabbitTomeGallery.defaultView,
        alt: { zh: '冷凍兔肉的大地秘笈森林綠柚馬卡龍預設視角插畫', en: "Default view of Frozen Rabbit's Tome forest green yuzu macaron" },
        caption: { zh: '森林綠柚馬卡龍', en: 'Forest Green Yuzu Macaron' },
      },
      {
        src: frozenRabbitTomeGallery.threeViews,
        alt: { zh: '冷凍兔肉的大地秘笈馬卡龍預設、頂面與平放側面視圖', en: "Default, top, and flat side views of Frozen Rabbit's Tome macaron" },
        caption: { zh: '到底哪個技能比較適合呢？', en: 'Which Skill Fits Best?' },
      },
      {
        src: frozenRabbitTomeGallery.clearEntry,
        alt: { zh: '冷凍兔肉的大地秘笈採集物品選擇入口畫面', en: "Gathering item selection in Frozen Rabbit's Tome" },
        caption: { zh: '清楚簡單的入口', en: 'A Clear, Simple Start' },
      },
      {
        src: frozenRabbitTomeGallery.solverResults,
        alt: { zh: '冷凍兔肉的大地秘笈求解器結果畫面', en: "Solver results in Frozen Rabbit's Tome" },
        caption: { zh: '一覽求解器結果', en: 'Solver Results at a Glance' },
      },
      {
        src: frozenRabbitTomeGallery.mobileLanguages,
        alt: { zh: '冷凍兔肉的大地秘笈英文手機版畫面', en: "English mobile layout of Frozen Rabbit's Tome" },
        caption: { zh: '支援四語系與手機版面', en: 'Four Languages, Mobile Ready' },
      },
    ],
    links: [
      {
        label: { zh: '線上展示', en: 'Live Website' },
        href: 'https://emu-rabbit.github.io/frozen_rabbit_tome/',
      },
      {
        label: { zh: 'Github頁面', en: 'GitHub Repo' },
        href: 'https://github.com/emu-rabbit/frozen_rabbit_tome',
      },
    ],
  },
  {
    slug: 'link-array',
    palette: macaronPaletteBySlug['link-array'],
    category: { zh: '資料結構', en: 'Data Structure' },
    title: { zh: 'LinkArray', en: 'LinkArray' },
    paragraphs: {
      zh: [
        '2020那年，想起了大學時的那段時光。課程上教了陣列，也教了鏈結串列。事實上我是後者的大粉絲，所以我就想到：那如果我把兩個綁在一起呢？',
        '抱持著這個想法，一頭熱地下去做，事實上還真的做出了不錯的成績。只是那時的我不知道該去哪裡發表，也不知道怎麼去查相近的研究。',
        '6年後，請AI回頭幫我審視這專案。原來現在對於我當初的目標已經有更好的選擇了，但我還是很愛這個專案。',
      ],
      en: [
        'In 2020, I thought back to university. We learned arrays and linked lists, and I was a big fan of the latter. So I wondered: what if I tied them together?',
        'I dove in and built something that worked surprisingly well. Back then, I did not know where to share it or how to find related research.',
        'Six years later, I asked AI to review the project. There are better choices now for what I once wanted to achieve, but I still love this project.',
      ],
    },
    closing: {
      zh: '「就像一個小孩子，不知世俗，不知現實，但那份勇於嘗試和求知的熱情才是最耀眼的。」',
      en: '“Like a child, unaware of convention or reality, whose courage to try and passion to learn shine brightest.”',
    },
    galleryLabel: {
      zh: 'LinkArray作品畫廊',
      en: 'LinkArray project gallery',
    },
    gallery: [
      {
        src: linkArrayGallery.defaultView,
        alt: { zh: 'LinkArray黑白芝麻馬卡龍預設視角插畫', en: 'Default view of the LinkArray black-and-white sesame macaron' },
        caption: { zh: '黑白鏈結馬卡龍', en: 'Black-and-White Linked Macaron' },
      },
      {
        src: linkArrayGallery.threeViews,
        alt: { zh: 'LinkArray馬卡龍預設、頂面與平放側面視圖', en: 'Default, top, and flat side views of the LinkArray macaron' },
        caption: { zh: '等等，那是蜈蚣還是蚯蚓？', en: 'Wait, Is That a Centipede or a Worm?' },
      },
      {
        src: linkArrayGallery.operationComplexity,
        alt: { zh: 'LinkArray各項操作的時間複雜度圖，GET列出最佳O(1)與最差O(n)', en: 'LinkArray operation time complexity chart, with GET best O(1) and worst O(n)' },
        caption: { zh: 'LinkArray操作的時間複雜度', en: 'LinkArray Operation Time Complexity' },
      },
      {
        src: linkArrayGallery.refactoredArea,
        alt: { zh: 'LinkArray重構區與未重構區的實體位置、節點索引及讀取成本示意圖', en: 'LinkArray refactored and unrefactored areas, showing physical slots, node indexes, and read costs' },
        caption: { zh: '什麼是重構區？', en: 'What Is the Refactored Area?' },
      },
    ],
    links: [
      {
        label: { zh: 'Github頁面', en: 'GitHub Repo' },
        href: 'https://github.com/emu-rabbit/LinkArray',
      },
    ],
  },
] as const satisfies readonly MacaronDetail[]

export const macaronDetailsBySlug: ReadonlyMap<string, MacaronDetail> = new Map(
  macaronDetails.map((detail) => [detail.slug, detail] as const),
)
