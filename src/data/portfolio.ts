import type { Language, Localized } from '../types/portfolio'
import { macaronIdentityBySlug } from './macaronIdentity'
import { macaronPaletteBySlug } from './macaronPalette'

export interface PortfolioCopy {
  brand: string
  title: string
  introduction: readonly string[]
  collectionLabel: string
  signatureTitle: string
  innovationTitle: string
  classicTitle: string
  signatureCta: string
  backHome: string
  projectLinksLabel: string
  previousImage: string
  nextImage: string
  openImage: string
  closeImage: string
  zoomIn: string
  zoomOut: string
  resetZoom: string
  loadingImage: string
  imageLoadError: string
  languageLabel: string
  lightTheme: string
  darkTheme: string
  afterword: AfterwordCopy
}

export interface AfterwordCopy {
  title: string
  titleLines: readonly string[]
  openedTitle: string
  cardAlt: string
  openCard: string
  openingCard: string
  paragraphs: readonly string[]
  loadModel: string
  preparingViewer: string
  viewerLabel: string
  modelFallbackAlt: string
  loadingModel: string
  modelLoadError: string
  modelDiagnosticLabel: string
  interactionHint: string
  resetView: string
}

export interface BoxMacaron {
  name: string
  targetId: string
  src: string
  left: string
  top: string
  row: number
}

export interface FlavorCard {
  id: string
  category: Localized<string>
  title: Localized<string>
  flavor: Localized<string>
  description: Localized<readonly string[]>
  mobileDescription: Localized<readonly string[]>
  src: string
  imageAlt: Localized<string>
  color: string
  darkColor: string
}

export interface FlavorSection {
  id: 'signature' | 'innovation' | 'classic'
  title: string
  layout: 'double' | 'trio'
  flavors: readonly FlavorCard[]
}

export const portfolioCopy: Localized<PortfolioCopy> = {
  zh: {
    brand: '絵夢羽さ沂的作品集',
    title: '想從哪顆開始吃呢？',
    introduction: [
      '不知何處而來的兔子推給你了一盒馬卡龍，從她的表情看起來是她的自信之作。',
      '裡面每顆都飽滿而各有特色，像是被精心設計和烘焙的小傢伙。拿起來，左右看一看，選擇你有興趣的馬卡龍吃下去吧！',
    ],
    collectionLabel: '一盒緊湊排列的十顆馬卡龍',
    signatureTitle: '招牌推薦口味',
    innovationTitle: '技術創新口味',
    classicTitle: '早期懷念口味',
    signatureCta: '仔細查看這顆馬卡龍',
    backHome: '返回首頁',
    projectLinksLabel: '作品連結',
    previousImage: '上一張圖片',
    nextImage: '下一張圖片',
    openImage: '以全螢幕檢視圖片',
    closeImage: '退出全螢幕檢視',
    zoomIn: '放大圖片',
    zoomOut: '縮小圖片',
    resetZoom: '重設圖片縮放與位置',
    loadingImage: '正在載入圖片',
    imageLoadError: '圖片載入失敗，請再試一次',
    languageLabel: '切換語言',
    lightTheme: '切換為明亮主題',
    darkTheme: '切換為暗色主題',
    afterword: {
      title: '……？盒子的下方似乎夾了一封信？',
      titleLines: ['……？', '盒子的下方似乎夾了一封信？'],
      openedTitle: 'From: 絵夢羽さ沂',
      cardAlt: '一封以兔耳蠟封封起、點綴小花的精巧卡片',
      openCard: '打開卡片',
      openingCard: '正在打開卡片',
      paragraphs: [
        '如果有人問我，為麼想當工程師，我肯定會毫不猶豫地說：「因為我想解決問題。」',
        '我著迷於問題被解決的那一刻，不論那是我的，還是別人的痛點。因為我認為那才是一段程式真正展現它的價值的地方，就像一本書會因為讀者的存在而開始活起來。',
        '從最早期的50音測驗、75%的酒精計算機，製作這作品集的時候，我沒有驚訝於他們怎麼這麼陽春，那年紀的我怎麼敢把這種作品端出去（好啦，其實有一點）。我更多時候是驚訝於，原來這一路上的我都沒有變。發現哪裡麻煩、討厭，那不如就自己來做吧。這點一直到後來的FF14巧匠網頁和BDSM測驗網頁都一樣。',
        'AI的崛起，一開始我也害怕過，但現在的我心中更多的是興奮，因為我做這些工具再也不會嫌太過麻煩，甚至他加速了我做出新的東西的速度。但我也注意到了：在這AI的生產力大爆炸時代，作品中擁有自己的氣味是十分重要的。',
        '個人網頁便是我走出自己味道的第一步，我不是教AI怎麼用我的語氣說話，而是叫他不要動我的文字。我親筆的寫下了那一段又一段用來描述自己的字，然後編排，用自己的節奏，引導版面的流動。事實是，我覺得我成功了，然後帶著這個心得還有處理視覺雜音的能力，投入BDSM工具網頁的製作。',
        '其實想做作品集很久了，但苦於找不到那個點子，最後在一次沖澡的時候，馬卡龍這個詞就打進了我的腦袋。我有一家心目中最棒的馬卡龍店，它設計特別、餡料厚實，每顆都有自己的特色，以及最重要的——它並不會太甜。就像你看到的上面那些馬卡龍一樣，我把它落實進了本作品集的每個角落。然而，那家馬卡龍已經收攤不賣了，放進我的作品集，也是我希望藉此有個地方可以懷念它帶給我的六年時光。',
        '最後，就讓我用最喜歡的作品的馬卡龍來做結吧，這一次，你可以好好的，仔細的看。3D檔案有點大，對網路環境在意的朋友請多加留意囉。',
      ],
      loadModel: '開始載入 3D 馬卡龍（14.7 MB）',
      preparingViewer: '正在準備 3D 檢視器',
      viewerLabel: '可旋轉查看的紫夜兔耳馬卡龍 3D 模型',
      modelFallbackAlt: '暮色杏桃與蜂蜜玫瑰的紫夜兔耳馬卡龍',
      loadingModel: '正在載入 3D 馬卡龍',
      modelLoadError: '3D 馬卡龍載入失敗，請重新整理頁面後再試一次。',
      modelDiagnosticLabel: '診斷代碼',
      interactionHint: '拖曳旋轉・滾輪縮放',
      resetView: '重設 3D 模型視角',
    },
  },
  en: {
    brand: 'Emu Rabbit Portfolio',
    title: 'Which one will you try first?',
    introduction: [
      'A rabbit appeared with a box of macarons. Her proud smile says they’re her best work.',
      'Each one is plump, full of character, and made with care. Pick one up and taste whichever calls to you.',
    ],
    collectionLabel: 'A snug box of ten macarons',
    signatureTitle: 'Signature Flavors',
    innovationTitle: 'Experimental Flavors',
    classicTitle: 'Nostalgic Flavors',
    signatureCta: 'Take a closer look',
    backHome: 'Back home',
    projectLinksLabel: 'Project links',
    previousImage: 'Previous image',
    nextImage: 'Next image',
    openImage: 'View image full screen',
    closeImage: 'Exit full-screen view',
    zoomIn: 'Zoom in',
    zoomOut: 'Zoom out',
    resetZoom: 'Reset image zoom and position',
    loadingImage: 'Loading image',
    imageLoadError: 'Image failed to load. Please try again.',
    languageLabel: 'Switch language',
    lightTheme: 'Switch to light theme',
    darkTheme: 'Switch to dark theme',
    afterword: {
      title: '…? Is there a letter tucked underneath the box?',
      titleLines: ['…?', 'Is there a letter tucked underneath the box?'],
      openedTitle: 'From: Emu-Rabbit',
      cardAlt: 'A delicate floral card sealed with a tiny rabbit-ear wax seal',
      openCard: 'Open the card',
      openingCard: 'Opening the card',
      paragraphs: [
        'If someone asked why I wanted to become an engineer, I would answer without hesitation: “Because I want to solve problems.”',
        'I am fascinated by the moment a problem is solved, whether it is my own problem or someone else\'s pain point. That is when a piece of software truly shows its value, just as a book begins to live when it finds a reader.',
        'When I looked back at my earliest projects—the 50 Hiragana Test and the 75% alcohol calculator—while making this portfolio, I was not shocked by how simple they were, or by how I had dared to show them to anyone at that age. (All right, maybe a little.) What surprised me more was realizing that I had never really changed along the way. Whenever I find something troublesome or annoying, I think: why not make the solution myself? That remained true for the FFXIV crafting website and the BDSM quiz website that came later.',
        'The rise of AI frightened me at first, too. Now, though, I feel far more excitement. These tools no longer feel too troublesome to make, and AI has even accelerated the pace at which I can bring new things into being. But I also noticed that, in this age of explosive AI productivity, it matters enormously for a work to carry a scent of its own.',
        'My personal website was my first step toward finding that scent. I did not teach AI to speak in my voice; I told it not to touch my words. I wrote every passage that describes me by hand, then arranged them in my own rhythm to guide the flow of the page. The truth is, I think I succeeded. I carried that lesson—and the ability to clear away visual noise—into making the BDSM tool website.',
        'I had wanted to make a portfolio for a long time, but I could never find the right idea. Then one day in the shower, the word “macaron” popped into my head. There was a macaron shop I considered the very best: its designs were distinctive, its fillings generous, every piece had a character of its own, and most importantly—it was never too sweet. Just like the macarons you saw above, I worked that feeling into every corner of this portfolio. The shop has since closed, so placing it here is also my way of giving myself somewhere to remember the six years it gave me.',
        'So let me close with the macaron from my favorite work. This time, you can take your time and look closely. The 3D file is a little large, so please keep that in mind if your connection is limited.',
      ],
      loadModel: 'Load the 3D macaron (14.7 MB)',
      preparingViewer: 'Preparing the 3D viewer',
      viewerLabel: 'Rotatable 3D model of the Violet Night Rabbit-Ear macaron',
      modelFallbackAlt: 'Violet Night Rabbit-Ear macaron with twilight apricot and honey rose',
      loadingModel: 'Loading the 3D macaron',
      modelLoadError: 'The 3D macaron could not be loaded. Refresh the page and try again.',
      modelDiagnosticLabel: 'Diagnostic code',
      interactionHint: 'Drag to rotate · Scroll to zoom',
      resetView: 'Reset the 3D model view',
    },
  },
}

const macaronAsset = (fileName: string) =>
  new URL(`../../assets/macarons-web/${fileName}`, import.meta.url).href

export const boxMacarons: readonly BoxMacaron[] = [
  { name: 'Frozen Rabbit Workshop', targetId: 'frozen-rabbit-workshop', src: macaronAsset('workshop.webp'), left: '4.4%', top: '15%', row: 0 },
  { name: 'Frozen Rabbit Tome', targetId: 'frozen-rabbit-tome', src: macaronAsset('tome.webp'), left: '22.9%', top: '13.7%', row: 0 },
  { name: 'Boundary Notes', targetId: 'boundary-notes', src: macaronAsset('boundary-notes.webp'), left: '40.7%', top: '14.7%', row: 0 },
  { name: 'Emu Rabbit Github io', targetId: 'window-notes', src: macaronAsset('emu-rabbit.webp'), left: '58.1%', top: '13.5%', row: 0 },
  { name: 'LinkArray', targetId: 'link-array', src: macaronAsset('link-array.webp'), left: '75%', top: '14.6%', row: 0 },
  { name: 'Vue Router Rule', targetId: 'vue-router-rule', src: macaronAsset('vue-router-rule.webp'), left: '2.5%', top: '49.1%', row: 1 },
  { name: 'Dandelifeon', targetId: 'dandelifeon', src: macaronAsset('dandelifeon.webp'), left: '20.9%', top: '47.9%', row: 1 },
  { name: 'nAnB', targetId: 'nanb', src: macaronAsset('nanb.webp'), left: '39.6%', top: '49.2%', row: 1 },
  { name: '75% Alchohol', targetId: '75-alchohol', src: macaronAsset('75-alchohol.webp'), left: '57.7%', top: '47.4%', row: 1 },
  { name: '50 Hiragana Test', targetId: '50-hiragana-test', src: macaronAsset('50-hiragana-test.webp'), left: '75.1%', top: '48.7%', row: 1 },
]

const signatureFlavors: readonly FlavorCard[] = [
  {
    id: 'window-notes',
    category: { zh: '個人網頁', en: 'Personal Website' },
    title: { zh: '絵夢羽さ沂的窗邊手記', en: "Emu-Rabbit's Window Notes" },
    flavor: macaronIdentityBySlug['window-notes'].flavor,
    description: {
      zh: ['一扇打開的窗，兔子在窗邊等待著你靠近，', '閱讀著手記，一步一步的認識、了解她。'],
      en: ['An open window. A rabbit waits by it,', 'inviting you closer to read her notes', 'and slowly get to know her.'],
    },
    mobileDescription: {
      zh: ['一扇打開的窗，兔子在窗邊', '等待著你靠近，閱讀著手記，', '一步一步的認識、了解她。'],
      en: ['An open window. A rabbit waits by it,', 'inviting you closer to read her notes', 'and slowly get to know her.'],
    },
    src: macaronAsset('emu-rabbit.webp'),
    imageAlt: { zh: '暮色杏桃與蜂蜜玫瑰的窗邊手記馬卡龍', en: 'Window Notes macaron with twilight apricot and honey rose' },
    color: macaronPaletteBySlug['window-notes'].color,
    darkColor: macaronPaletteBySlug['window-notes'].darkColor,
  },
  {
    id: 'boundary-notes',
    category: { zh: 'BDSM整理工具', en: 'BDSM Organizer' },
    title: { zh: '兔子的秘密檔案', en: 'Boundary Notes' },
    flavor: macaronIdentityBySlug['boundary-notes'].flavor,
    description: {
      zh: ['把界線、喜好用最簡單好讀的方式整理起來，', '慾望沒有對錯，你依舊是你自己。'],
      en: ['A simple, readable way to sort out', 'boundaries and desires. There is no', 'right or wrong—you are still yourself.'],
    },
    mobileDescription: {
      zh: ['把界線、喜好用最簡單好讀的方式', '整理起來，慾望沒有對錯，', '你依舊是你自己。'],
      en: ['A simple, readable way to sort out', 'boundaries and desires. There is no', 'right or wrong—you are still yourself.'],
    },
    src: macaronAsset('boundary-notes.webp'),
    imageAlt: { zh: '黑醋栗與玫瑰伯爵的兔子秘密檔案馬卡龍', en: 'Boundary Notes macaron with blackcurrant and rose Earl Grey' },
    color: macaronPaletteBySlug['boundary-notes'].color,
    darkColor: macaronPaletteBySlug['boundary-notes'].darkColor,
  },
  {
    id: 'frozen-rabbit-workshop',
    category: { zh: 'Final Fantasy XIV 巧匠工具', en: 'Final Fantasy XIV Crafting Tool' },
    title: { zh: '冷凍兔肉的巧匠工坊', en: "Frozen Rabbit's Workshop" },
    flavor: macaronIdentityBySlug['frozen-rabbit-workshop'].flavor,
    description: {
      zh: ['兔肉不私藏的好筆記，', '你最好的備料輔助工具。'],
      en: ["No secrets kept—Rabbit's best notes,", 'ready to make material prep easier.'],
    },
    mobileDescription: {
      zh: ['兔肉不私藏的好筆記，', '你最好的備料輔助工具。'],
      en: ["No secrets kept—Rabbit's best notes,", 'ready to make material prep easier.'],
    },
    src: macaronAsset('workshop.webp'),
    imageAlt: { zh: '薄荷、青檸與白巧克力的巧匠工坊馬卡龍', en: 'Workshop macaron with mint, lime, and white chocolate' },
    color: macaronPaletteBySlug['frozen-rabbit-workshop'].color,
    darkColor: macaronPaletteBySlug['frozen-rabbit-workshop'].darkColor,
  },
  {
    id: 'frozen-rabbit-tome',
    category: { zh: 'Final Fantasy XIV 大地工具', en: 'Final Fantasy XIV Gathering Tool' },
    title: { zh: '冷凍兔肉的大地秘笈', en: "Frozen Rabbit's Tome" },
    flavor: macaronIdentityBySlug['frozen-rabbit-tome'].flavor,
    description: {
      zh: ['兔肉不私藏的好秘笈，', '採集技能的推薦求解器。'],
      en: ["No secrets kept—Rabbit's best tome,", 'ready to guide your next gathering move.'],
    },
    mobileDescription: {
      zh: ['兔肉不私藏的好秘笈，', '採集技能的推薦求解器。'],
      en: ["No secrets kept—Rabbit's best tome,", 'ready to guide your next', 'gathering move.'],
    },
    src: macaronAsset('tome.webp'),
    imageAlt: { zh: '深焙抹茶與柚子金砂的大地秘笈馬卡龍', en: 'Tome macaron with roasted matcha and yuzu gold dust' },
    color: macaronPaletteBySlug['frozen-rabbit-tome'].color,
    darkColor: macaronPaletteBySlug['frozen-rabbit-tome'].darkColor,
  },
]

const innovationFlavors: readonly FlavorCard[] = [
  {
    id: 'link-array',
    category: { zh: '資料結構', en: 'Data Structure' },
    title: { zh: 'LinkArray', en: 'LinkArray' },
    flavor: macaronIdentityBySlug['link-array'].flavor,
    description: {
      zh: ['陣列擅長隨機存取，', '鏈結串列擅長插入移除，', '加起來究竟是優點相加還是缺點倍顯呢？'],
      en: ['Arrays excel at random access;', 'linked lists at insertion and removal.', 'Together, do their strengths add up—', 'or do their flaws multiply?'],
    },
    mobileDescription: {
      zh: ['陣列擅長隨機存取，', '鏈結串列擅長插入移除，', '加起來究竟是優點相加', '還是缺點倍顯呢？'],
      en: ['Arrays excel at random access;', 'linked lists at insertion and removal.', 'Together, do their strengths add up—', 'or do their flaws multiply?'],
    },
    src: macaronAsset('link-array.webp'),
    imageAlt: { zh: '黑白芝麻與鹽焦糖的 LinkArray 馬卡龍', en: 'LinkArray macaron with black and white sesame and salted caramel' },
    color: macaronPaletteBySlug['link-array'].color,
    darkColor: macaronPaletteBySlug['link-array'].darkColor,
  },
  {
    id: 'vue-router-rule',
    category: { zh: '插件', en: 'Plugin' },
    title: { zh: 'Vue Router Rule', en: 'Vue Router Rule' },
    flavor: macaronIdentityBySlug['vue-router-rule'].flavor,
    description: {
      zh: ['撰寫簡單易讀的 Vue Router 鉤子，', '不會遇到義大利麵程式碼了（應該）。'],
      en: ['Simple, readable Vue Router hooks—', 'no more spaghetti code. (Probably.)'],
    },
    mobileDescription: {
      zh: ['撰寫簡單易讀的 Vue Router 鉤子，', '不會遇到義大利麵程式碼了', '（應該）。'],
      en: ['Simple, readable Vue Router hooks—', 'no more spaghetti code. (Probably.)'],
    },
    src: macaronAsset('vue-router-rule.webp'),
    imageAlt: { zh: '青葡萄、荔枝與紫羅蘭的 Vue Router Rule 馬卡龍', en: 'Vue Router Rule macaron with green grape, lychee, and violet' },
    color: macaronPaletteBySlug['vue-router-rule'].color,
    darkColor: macaronPaletteBySlug['vue-router-rule'].darkColor,
  },
  {
    id: 'dandelifeon',
    category: { zh: '遊戲機制求解', en: 'Game Mechanic Solver' },
    title: { zh: 'Dandelifeon', en: 'Dandelifeon' },
    flavor: macaronIdentityBySlug.dandelifeon.flavor,
    description: {
      zh: ['Minecraft 的魔法模組有個特別的花，', '到底怎樣才能生成最大魔力呢？'],
      en: ["Minecraft's Botania mod", 'has a peculiar flower.', 'What arrangement generates', 'the most mana?'],
    },
    mobileDescription: {
      zh: ['Minecraft 的魔法模組有個特別的花，', '到底怎樣才能生成最大魔力呢？'],
      en: ["Minecraft's Botania mod", 'has a peculiar flower.', 'What arrangement generates', 'the most mana?'],
    },
    src: macaronAsset('dandelifeon.webp'),
    imageAlt: { zh: '蒲公英蜜與青蘋果的 Dandelifeon 馬卡龍', en: 'Dandelifeon macaron with dandelion honey and green apple' },
    color: macaronPaletteBySlug['dandelifeon'].color,
    darkColor: macaronPaletteBySlug['dandelifeon'].darkColor,
  },
]

const classicFlavors: readonly FlavorCard[] = [
  {
    id: 'nanb',
    category: { zh: '數字小遊戲', en: 'Number Game' },
    title: { zh: 'nAnB', en: 'nAnB' },
    flavor: macaronIdentityBySlug.nanb.flavor,
    description: {
      zh: ['玩過 nAnB 嗎？我家的黃金鼠夢夢', '很會這遊戲，來玩玩看吧！'],
      en: ['Ever played nAnB?', 'My hamster Meng-Meng is great at it.', 'Come play a round!'],
    },
    mobileDescription: {
      zh: ['玩過 nAnB 嗎？我家的黃金鼠', '夢夢很會這遊戲，來玩玩看吧！'],
      en: ['Ever played nAnB?', 'My hamster Meng-Meng is great at it.', 'Come play a round!'],
    },
    src: macaronAsset('nanb.webp'),
    imageAlt: { zh: '藍莓優格與葵花子的 nAnB 馬卡龍', en: 'nAnB macaron with blueberry yogurt and sunflower seeds' },
    color: macaronPaletteBySlug.nanb.color,
    darkColor: macaronPaletteBySlug.nanb.darkColor,
  },
  {
    id: '75-alchohol',
    category: { zh: '疫情期間小工具', en: 'Pandemic-Era Tool' },
    title: { zh: '75% Alchohol', en: '75% Alchohol' },
    flavor: macaronIdentityBySlug['75-alchohol'].flavor,
    description: {
      zh: ['簡單的，幫你算酒精濃度的小工具，', '不用再按計算機了。'],
      en: ['A simple tool for calculating', 'alcohol concentration—', 'no calculator needed.'],
    },
    mobileDescription: {
      zh: ['簡單的，幫你算酒精濃度的小工具，', '不用再按計算機了。'],
      en: ['A simple tool for calculating', 'alcohol concentration—', 'no calculator needed.'],
    },
    src: macaronAsset('75-alchohol.webp'),
    imageAlt: { zh: '白葡萄與檸檬蘇打的 75% Alchohol 馬卡龍', en: '75% Alchohol macaron with white grape and lemon soda' },
    color: macaronPaletteBySlug['75-alchohol'].color,
    darkColor: macaronPaletteBySlug['75-alchohol'].darkColor,
  },
  {
    id: '50-hiragana-test',
    category: { zh: '日文學習小工具', en: 'Japanese Learning Tool' },
    title: { zh: '50 Hiragana Test', en: '50 Hiragana Test' },
    flavor: macaronIdentityBySlug['50-hiragana-test'].flavor,
    description: {
      zh: ['當初是為了要學日文做的，', '怎麼現在我好像還是沒學會日文（？）'],
      en: ['I made this to learn Japanese.', "Somehow, I still haven't. (?)"],
    },
    mobileDescription: {
      zh: ['當初是為了要學日文做的，', '怎麼現在我好像還是', '沒學會日文（？）'],
      en: ['I made this to learn Japanese.', "Somehow, I still haven't. (?)"],
    },
    src: macaronAsset('50-hiragana-test.webp'),
    imageAlt: { zh: '櫻花牛奶與紅豆的 50 Hiragana Test 馬卡龍', en: '50 Hiragana Test macaron with sakura milk and red bean' },
    color: macaronPaletteBySlug['50-hiragana-test'].color,
    darkColor: macaronPaletteBySlug['50-hiragana-test'].darkColor,
  },
]

export const getFlavorSections = (language: Language): readonly FlavorSection[] => [
  { id: 'signature', title: portfolioCopy[language].signatureTitle, layout: 'double', flavors: signatureFlavors },
  { id: 'innovation', title: portfolioCopy[language].innovationTitle, layout: 'trio', flavors: innovationFlavors },
  { id: 'classic', title: portfolioCopy[language].classicTitle, layout: 'trio', flavors: classicFlavors },
]
