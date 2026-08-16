<script setup lang="ts">
import { computed, defineAsyncComponent, onBeforeUnmount, onMounted, ref, watch } from 'vue'

type Language = 'zh' | 'en'
type Theme = 'light' | 'dark'

const WindowNotesMacaronViewer = defineAsyncComponent(
  () => import('./components/WindowNotesMacaronViewer.vue'),
)

const copy = {
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
    languageLabel: '切換語言',
    lightTheme: '切換為明亮主題',
    darkTheme: '切換為暗色主題',
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
    languageLabel: 'Switch language',
    lightTheme: 'Switch to light theme',
    darkTheme: 'Switch to dark theme',
  },
} as const

const macaronBoxImage = new URL('../assets/hero/macaron-box-empty.webp', import.meta.url).href
const navMacaronImage = new URL('../assets/ui/nav-macaron.svg', import.meta.url).href
const windowNotesModel = new URL('../assets/models/window-notes-macaron.glb', import.meta.url).href
const boundaryNotesModel = new URL('../assets/models/boundary-notes-macaron.glb', import.meta.url).href

const macarons = [
  { name: 'Frozen Rabbit Workshop', targetId: 'frozen-rabbit-workshop', image: 'workshop.webp', left: '4.4%', top: '15%', row: 0 },
  { name: 'Frozen Rabbit Tome', targetId: 'frozen-rabbit-tome', image: 'tome.webp', left: '22.9%', top: '13.7%', row: 0 },
  { name: 'Boundary Notes', targetId: 'boundary-notes', image: 'boundary-notes.webp', left: '40.7%', top: '14.7%', row: 0 },
  { name: 'Emu Rabbit Github io', targetId: 'window-notes', image: 'emu-rabbit.webp', left: '58.1%', top: '13.5%', row: 0 },
  { name: 'LinkArray', targetId: 'link-array', image: 'link-array.webp', left: '75%', top: '14.6%', row: 0 },
  { name: 'Vue Router Rule', targetId: 'vue-router-rule', image: 'vue-router-rule.webp', left: '2.5%', top: '49.1%', row: 1 },
  { name: 'Dandelifeon', targetId: 'dandelifeon', image: 'dandelifeon.webp', left: '20.9%', top: '47.9%', row: 1 },
  { name: 'nAnB', targetId: 'nanb', image: 'nanb.webp', left: '39.6%', top: '49.2%', row: 1 },
  { name: '75 Alchohol', targetId: '75-alchohol', image: '75-alchohol.webp', left: '57.7%', top: '47.4%', row: 1 },
  { name: '50 Hiragana Test', targetId: '50-hiragana-test', image: '50-hiragana-test.webp', left: '75.1%', top: '48.7%', row: 1 },
].map((macaron) => ({
  ...macaron,
  src: new URL(`../assets/macarons-web/${macaron.image}`, import.meta.url).href,
}))

const signatureFlavors = [
  {
    id: 'window-notes',
    category: { zh: '個人網頁', en: 'Personal Website' },
    title: { zh: '絵夢羽さ沂的窗邊手記', en: "Emu-Rabbit's Window Notes" },
    flavor: { zh: '暮色杏桃・蜂蜜玫瑰', en: 'Twilight Apricot · Honey Rose' },
    description: {
      zh: ['一扇打開的窗，兔子在窗邊等待著你靠近，', '閱讀著手記，一步一步的認識、了解她。'],
      en: [
        'An open window. A rabbit waits by it,',
        'inviting you closer to read her notes',
        'and slowly get to know her.',
      ],
    },
    mobileDescription: {
      zh: ['一扇打開的窗，兔子在窗邊', '等待著你靠近，閱讀著手記，', '一步一步的認識、了解她。'],
      en: [
        'An open window. A rabbit waits by it,',
        'inviting you closer to read her notes',
        'and slowly get to know her.',
      ],
    },
    image: 'emu-rabbit.webp',
    imageAlt: {
      zh: '暮色杏桃與蜂蜜玫瑰的窗邊手記馬卡龍',
      en: 'Window Notes macaron with twilight apricot and honey rose',
    },
    color: '#d9cddd',
    darkColor: '#42304f',
  },
  {
    id: 'boundary-notes',
    category: { zh: 'BDSM整理工具', en: 'BDSM Organizer' },
    title: { zh: '兔子的秘密檔案', en: 'Boundary Notes' },
    flavor: { zh: '黑醋栗・玫瑰伯爵', en: 'Blackcurrant · Rose Earl Grey' },
    description: {
      zh: ['把界線、喜好用最簡單好讀的方式整理起來，', '慾望沒有對錯，你依舊是你自己。'],
      en: [
        'A simple, readable way to sort out',
        'boundaries and desires. There is no',
        'right or wrong—you are still yourself.',
      ],
    },
    mobileDescription: {
      zh: ['把界線、喜好用最簡單好讀的方式', '整理起來，慾望沒有對錯，', '你依舊是你自己。'],
      en: [
        'A simple, readable way to sort out',
        'boundaries and desires. There is no',
        'right or wrong—you are still yourself.',
      ],
    },
    image: 'boundary-notes.webp',
    imageAlt: {
      zh: '黑醋栗與玫瑰伯爵的兔子秘密檔案馬卡龍',
      en: 'Boundary Notes macaron with blackcurrant and rose Earl Grey',
    },
    color: '#e1cfd2',
    darkColor: '#52303a',
  },
  {
    id: 'frozen-rabbit-workshop',
    category: { zh: 'Final Fantasy XIV 巧匠工具', en: 'Final Fantasy XIV Crafting Tool' },
    title: { zh: '冷凍兔肉的巧匠工坊', en: "Frozen Rabbit's Workshop" },
    flavor: { zh: '開心果・青檸・白巧克力', en: 'Pistachio · Lime · White Chocolate' },
    description: {
      zh: ['兔肉不私藏的好筆記，', '你最好的備料輔助工具。'],
      en: ["No secrets kept—Rabbit's best notes,", 'ready to make material prep easier.'],
    },
    mobileDescription: {
      zh: ['兔肉不私藏的好筆記，', '你最好的備料輔助工具。'],
      en: ["No secrets kept—Rabbit's best notes,", 'ready to make material prep easier.'],
    },
    image: 'workshop.webp',
    imageAlt: {
      zh: '開心果、青檸與白巧克力的巧匠工坊馬卡龍',
      en: 'Workshop macaron with pistachio, lime, and white chocolate',
    },
    color: '#d4dfce',
    darkColor: '#324d3b',
  },
  {
    id: 'frozen-rabbit-tome',
    category: { zh: 'Final Fantasy XIV 大地工具', en: 'Final Fantasy XIV Gathering Tool' },
    title: { zh: '冷凍兔肉的大地秘笈', en: "Frozen Rabbit's Tome" },
    flavor: { zh: '深焙抹茶・柚子金砂', en: 'Roasted Matcha · Yuzu Gold Dust' },
    description: {
      zh: ['兔肉不私藏的好秘笈，', '採集技能的推薦求解器。'],
      en: ["No secrets kept—Rabbit's best tome,", 'ready to guide your next gathering move.'],
    },
    mobileDescription: {
      zh: ['兔肉不私藏的好秘笈，', '採集技能的推薦求解器。'],
      en: [
        "No secrets kept—Rabbit's best tome,",
        'ready to guide your next',
        'gathering move.',
      ],
    },
    image: 'tome.webp',
    imageAlt: {
      zh: '深焙抹茶與柚子金砂的大地秘笈馬卡龍',
      en: 'Tome macaron with roasted matcha and yuzu gold dust',
    },
    color: '#ccdcd4',
    darkColor: '#2a473d',
  },
].map((flavor) => ({
  ...flavor,
  src: new URL(`../assets/macarons-web/${flavor.image}`, import.meta.url).href,
}))

const innovationFlavors = [
  {
    id: 'link-array',
    category: { zh: '資料結構', en: 'Data Structure' },
    title: { zh: 'LinkArray', en: 'LinkArray' },
    flavor: { zh: '黑白芝麻・鹽焦糖', en: 'Black & White Sesame · Salted Caramel' },
    description: {
      zh: ['陣列擅長隨機存取，鏈結串列擅長插入移除，', '加起來究竟是優點相加還是缺點倍顯呢？'],
      en: [
        'Arrays excel at random access;',
        'linked lists at insertion and removal.',
        'Together, do their strengths add up—',
        'or do their flaws multiply?',
      ],
    },
    mobileDescription: {
      zh: ['陣列擅長隨機存取，', '鏈結串列擅長插入移除，', '加起來究竟是優點相加', '還是缺點倍顯呢？'],
      en: [
        'Arrays excel at random access;',
        'linked lists at insertion and removal.',
        'Together, do their strengths add up—',
        'or do their flaws multiply?',
      ],
    },
    image: 'link-array.webp',
    imageAlt: {
      zh: '黑白芝麻與鹽焦糖的 LinkArray 馬卡龍',
      en: 'LinkArray macaron with black and white sesame and salted caramel',
    },
    color: '#ddd8d1',
    darkColor: '#35322f',
  },
  {
    id: 'vue-router-rule',
    category: { zh: '插件', en: 'Plugin' },
    title: { zh: 'Vue Router Rule', en: 'Vue Router Rule' },
    flavor: { zh: '青葡萄・荔枝・紫羅蘭', en: 'Green Grape · Lychee · Violet' },
    description: {
      zh: ['撰寫簡單，容易閱讀的 Vue Router 鉤子，', '不會遇到義大利麵程式碼了（應該）。'],
      en: ['Simple, readable Vue Router hooks—', 'no more spaghetti code. (Probably.)'],
    },
    mobileDescription: {
      zh: ['撰寫簡單，容易閱讀的', 'Vue Router 鉤子，不會遇到', '義大利麵程式碼了（應該）。'],
      en: ['Simple, readable Vue Router hooks—', 'no more spaghetti code. (Probably.)'],
    },
    image: 'vue-router-rule.webp',
    imageAlt: {
      zh: '青葡萄、荔枝與紫羅蘭的 Vue Router Rule 馬卡龍',
      en: 'Vue Router Rule macaron with green grape, lychee, and violet',
    },
    color: '#d7dfd7',
    darkColor: '#28473f',
  },
  {
    id: 'dandelifeon',
    category: { zh: '遊戲機制求解', en: 'Game Mechanic Solver' },
    title: { zh: 'Dandelifeon', en: 'Dandelifeon' },
    flavor: { zh: '蒲公英蜜・青蘋果', en: 'Dandelion Honey · Green Apple' },
    description: {
      zh: ['Minecraft 的 Botania 模組有個特別的花，', '到底怎樣才能生成最大魔力呢？'],
      en: [
        "Minecraft's Botania mod",
        'has a peculiar flower.',
        'What arrangement generates',
        'the most mana?',
      ],
    },
    mobileDescription: {
      zh: ['Minecraft 的 Botania 模組', '有個特別的花，到底怎樣才能', '生成最大魔力呢？'],
      en: [
        "Minecraft's Botania mod",
        'has a peculiar flower.',
        'What arrangement generates',
        'the most mana?',
      ],
    },
    image: 'dandelifeon.webp',
    imageAlt: {
      zh: '蒲公英蜜與青蘋果的 Dandelifeon 馬卡龍',
      en: 'Dandelifeon macaron with dandelion honey and green apple',
    },
    color: '#e6dfbd',
    darkColor: '#334f32',
  },
].map((flavor) => ({
  ...flavor,
  src: new URL(`../assets/macarons-web/${flavor.image}`, import.meta.url).href,
}))

const classicFlavors = [
  {
    id: 'nanb',
    category: { zh: '數字小遊戲', en: 'Number Game' },
    title: { zh: 'nAnB', en: 'nAnB' },
    flavor: { zh: '藍莓優格・葵花子', en: 'Blueberry Yogurt · Sunflower Seeds' },
    description: {
      zh: ['玩過 nAnB 嗎？我家的黃金鼠夢夢', '很會這遊戲，來玩玩看吧！'],
      en: ['Ever played nAnB?', 'My hamster Meng-Meng is great at it.', 'Come play a round!'],
    },
    mobileDescription: {
      zh: ['玩過 nAnB 嗎？我家的黃金鼠', '夢夢很會這遊戲，來玩玩看吧！'],
      en: ['Ever played nAnB?', 'My hamster Meng-Meng is great at it.', 'Come play a round!'],
    },
    image: 'nanb.webp',
    imageAlt: {
      zh: '藍莓優格與葵花子的 nAnB 馬卡龍',
      en: 'nAnB macaron with blueberry yogurt and sunflower seeds',
    },
    color: '#d8d8e4',
    darkColor: '#313853',
  },
  {
    id: '75-alchohol',
    category: { zh: '疫情期間小工具', en: 'Pandemic-Era Tool' },
    title: { zh: '75 Alchohol', en: '75 Alchohol' },
    flavor: { zh: '白葡萄・檸檬蘇打', en: 'White Grape · Lemon Soda' },
    description: {
      zh: ['簡單的，幫你算酒精濃度的小工具，', '不用再按計算機了。'],
      en: ['A simple tool for calculating', 'alcohol concentration—', 'no calculator needed.'],
    },
    mobileDescription: {
      zh: ['簡單的，幫你算酒精濃度的小工具，', '不用再按計算機了。'],
      en: ['A simple tool for calculating', 'alcohol concentration—', 'no calculator needed.'],
    },
    image: '75-alchohol.webp',
    imageAlt: {
      zh: '白葡萄與檸檬蘇打的 75 Alchohol 馬卡龍',
      en: '75 Alchohol macaron with white grape and lemon soda',
    },
    color: '#d7e3e5',
    darkColor: '#294753',
  },
  {
    id: '50-hiragana-test',
    category: { zh: '日文學習小工具', en: 'Japanese Learning Tool' },
    title: { zh: '50 Hiragana Test', en: '50 Hiragana Test' },
    flavor: { zh: '櫻花牛奶・紅豆', en: 'Sakura Milk · Red Bean' },
    description: {
      zh: ['當初是為了要學日文做的，', '怎麼現在我好像還是沒學會日文（？）'],
      en: ['I made this to learn Japanese.', "Somehow, I still haven't. (?)"],
    },
    mobileDescription: {
      zh: ['當初是為了要學日文做的，', '怎麼現在我好像還是', '沒學會日文（？）'],
      en: ['I made this to learn Japanese.', "Somehow, I still haven't. (?)"],
    },
    image: '50-hiragana-test.webp',
    imageAlt: {
      zh: '櫻花牛奶與紅豆的 50 Hiragana Test 馬卡龍',
      en: '50 Hiragana Test macaron with sakura milk and red bean',
    },
    color: '#ead7dc',
    darkColor: '#56343f',
  },
].map((flavor) => ({
  ...flavor,
  src: new URL(`../assets/macarons-web/${flavor.image}`, import.meta.url).href,
}))

const languageStorageKey = 'portfolio-language'
const themeStorageKey = 'portfolio-theme'

const getInitialLanguage = (): Language => {
  const savedLanguage = window.localStorage.getItem(languageStorageKey)
  return savedLanguage === 'zh' || savedLanguage === 'en' ? savedLanguage : 'zh'
}

const getSavedTheme = (): Theme | null => {
  try {
    const savedTheme = window.localStorage.getItem(themeStorageKey)
    return savedTheme === 'light' || savedTheme === 'dark' ? savedTheme : null
  } catch {
    return null
  }
}

const getSystemTheme = (): Theme => {
  try {
    return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  } catch {
    return 'light'
  }
}

const getInitialTheme = (): Theme => {
  return getSavedTheme() ?? getSystemTheme()
}

const language = ref<Language>(getInitialLanguage())
const theme = ref<Theme>(getInitialTheme())
const currentHash = ref(window.location.hash)
const macaronScene = ref<HTMLElement | null>(null)
const highlightedFlavorId = ref<string | null>(null)

let macaronElements: HTMLElement[] = []
let motionFrame = 0
let highlightFrame = 0
let scrollHighlightTimer = 0
let pendingScrollEnd: (() => void) | null = null
let lastScrollY = 0
let lastWheelTime = 0
let waveStartTime = 0
let waveDirection = 1
let waveLocked = false
let waveUnlockTimer = 0
let lastTouchY: number | null = null
let reducedMotionQuery: MediaQueryList | null = null

const waveLift = 12
const waveLiftDuration = 320
const waveColumnDelay = 70
const waveRowDelay = 35
const waveDuration = waveLiftDuration + waveColumnDelay * 4 + waveRowDelay
const waveCooldown = 500

const text = computed(() => copy[language.value])
const viewerModels = {
  'window-notes': windowNotesModel,
  'boundary-notes': boundaryNotesModel,
} as const
const viewerFlavorId = computed(() => {
  const match = currentHash.value.match(/^#\/viewer\/(window-notes|boundary-notes)$/)
  return match?.[1] as keyof typeof viewerModels | undefined
})
const viewerFlavor = computed(() =>
  signatureFlavors.find((flavor) => flavor.id === viewerFlavorId.value),
)
const viewerModelUrl = computed(() =>
  viewerFlavorId.value ? viewerModels[viewerFlavorId.value] : undefined,
)
const viewerTitle = computed(() => `${viewerFlavor.value?.title[language.value] ?? ''} 3D`)
const isViewerRoute = computed(() => Boolean(viewerFlavor.value && viewerModelUrl.value))
const flavorSections = computed(() => [
  {
    id: 'signature',
    title: text.value.signatureTitle,
    layout: 'double',
    flavors: signatureFlavors,
  },
  {
    id: 'innovation',
    title: text.value.innovationTitle,
    layout: 'trio',
    flavors: innovationFlavors,
  },
  {
    id: 'classic',
    title: text.value.classicTitle,
    layout: 'trio',
    flavors: classicFlavors,
  },
])
const nextThemeLabel = computed(() =>
  theme.value === 'light' ? text.value.darkTheme : text.value.lightTheme,
)

const setLanguage = (nextLanguage: Language) => {
  language.value = nextLanguage
}

const toggleTheme = () => {
  const nextTheme = theme.value === 'light' ? 'dark' : 'light'
  theme.value = nextTheme

  try {
    window.localStorage.setItem(themeStorageKey, nextTheme)
  } catch {
    // The selected theme still applies for this visit when storage is unavailable.
  }
}

const syncRoute = () => {
  currentHash.value = window.location.hash
  window.scrollTo({ top: 0, behavior: 'auto' })
}

const goHome = () => {
  window.location.hash = ''
}

const handleMacaronClick = (targetId: string) => {
  scrollToFlavor(targetId)
}

const clearPendingScrollHighlight = () => {
  if (pendingScrollEnd) {
    window.removeEventListener('scrollend', pendingScrollEnd)
    pendingScrollEnd = null
  }

  if (scrollHighlightTimer) {
    window.clearTimeout(scrollHighlightTimer)
    scrollHighlightTimer = 0
  }

  if (highlightFrame) {
    window.cancelAnimationFrame(highlightFrame)
    highlightFrame = 0
  }
}

const highlightFlavor = (targetId: string) => {
  highlightedFlavorId.value = null
  highlightFrame = window.requestAnimationFrame(() => {
    highlightedFlavorId.value = targetId
    highlightFrame = 0
  })
}

const scrollToFlavor = (targetId: string) => {
  const target = document.getElementById(targetId)

  if (!target) {
    return
  }

  clearPendingScrollHighlight()
  highlightedFlavorId.value = null

  const reducedMotion = reducedMotionQuery?.matches ?? false
  const finishScroll = () => {
    clearPendingScrollHighlight()

    if (!reducedMotion) {
      highlightFlavor(targetId)
    }
  }

  if (!reducedMotion) {
    pendingScrollEnd = finishScroll
    window.addEventListener('scrollend', finishScroll, { once: true })
    scrollHighlightTimer = window.setTimeout(finishScroll, 1600)
  }

  target.scrollIntoView({
    behavior: reducedMotion ? 'auto' : 'smooth',
    block: 'start',
  })
}

const clearMacaronMotion = () => {
  if (motionFrame) {
    window.cancelAnimationFrame(motionFrame)
    motionFrame = 0
  }

  waveStartTime = 0
  macaronElements.forEach((element) => element.style.removeProperty('--scroll-lift'))
}

const unlockMacaronWave = () => {
  if (waveUnlockTimer) {
    window.clearTimeout(waveUnlockTimer)
    waveUnlockTimer = 0
  }

  waveLocked = false
}

const finishMacaronWave = () => {
  clearMacaronMotion()
  waveUnlockTimer = window.setTimeout(unlockMacaronWave, waveCooldown)
}

const animateMacaronWave = (time: number) => {
  if (!waveStartTime) {
    waveStartTime = time
  }

  const elapsed = time - waveStartTime

  macaronElements.forEach((element, index) => {
    const column = index % 5
    const row = Math.floor(index / 5)
    const orderedColumn = waveDirection > 0 ? column : 4 - column
    const delay = orderedColumn * waveColumnDelay + row * waveRowDelay
    const progress = (elapsed - delay) / waveLiftDuration
    const lift = progress >= 0 && progress <= 1 ? -Math.sin(Math.PI * progress) * waveLift : 0
    element.style.setProperty('--scroll-lift', `${lift.toFixed(2)}px`)
  })

  if (elapsed < waveDuration) {
    motionFrame = window.requestAnimationFrame(animateMacaronWave)
    return
  }

  finishMacaronWave()
}

const addWaveImpulse = (delta: number) => {
  if (!delta || waveLocked || reducedMotionQuery?.matches) {
    return
  }

  waveLocked = true
  waveDirection = delta > 0 ? 1 : -1
  motionFrame = window.requestAnimationFrame(animateMacaronWave)
}

const handleMotionPreferenceChange = () => {
  clearPendingScrollHighlight()
  highlightedFlavorId.value = null
  clearMacaronMotion()
  unlockMacaronWave()
}

const handleWheel = (event: WheelEvent) => {
  lastWheelTime = window.performance.now()
  addWaveImpulse(event.deltaY)
}

const handleScroll = () => {
  const nextScrollY = window.scrollY
  const delta = nextScrollY - lastScrollY
  lastScrollY = nextScrollY

  if (window.performance.now() - lastWheelTime > 80) {
    addWaveImpulse(delta)
  }
}

const handleTouchStart = (event: TouchEvent) => {
  lastTouchY = event.touches[0]?.clientY ?? null
}

const handleTouchMove = (event: TouchEvent) => {
  const nextTouchY = event.touches[0]?.clientY

  if (nextTouchY === undefined || lastTouchY === null) {
    return
  }

  addWaveImpulse(lastTouchY - nextTouchY)
  lastTouchY = nextTouchY
}

const handleTouchEnd = () => {
  lastTouchY = null
}

onMounted(() => {
  macaronElements = Array.from(macaronScene.value?.querySelectorAll<HTMLElement>('.macaron') ?? [])
  lastScrollY = window.scrollY
  reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  reducedMotionQuery.addEventListener('change', handleMotionPreferenceChange)
  window.addEventListener('wheel', handleWheel, { passive: true })
  window.addEventListener('scroll', handleScroll, { passive: true })
  window.addEventListener('touchstart', handleTouchStart, { passive: true })
  window.addEventListener('touchmove', handleTouchMove, { passive: true })
  window.addEventListener('touchend', handleTouchEnd, { passive: true })
  window.addEventListener('touchcancel', handleTouchEnd, { passive: true })
  window.addEventListener('hashchange', syncRoute)

  if (isViewerRoute.value) {
    window.scrollTo({ top: 0, behavior: 'auto' })
  }
})

onBeforeUnmount(() => {
  clearPendingScrollHighlight()
  clearMacaronMotion()
  unlockMacaronWave()
  reducedMotionQuery?.removeEventListener('change', handleMotionPreferenceChange)
  window.removeEventListener('wheel', handleWheel)
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('touchstart', handleTouchStart)
  window.removeEventListener('touchmove', handleTouchMove)
  window.removeEventListener('touchend', handleTouchEnd)
  window.removeEventListener('touchcancel', handleTouchEnd)
  window.removeEventListener('hashchange', syncRoute)
})

watch(
  language,
  (nextLanguage) => {
    document.documentElement.lang = nextLanguage === 'zh' ? 'zh-Hant' : 'en'
    window.localStorage.setItem(languageStorageKey, nextLanguage)
  },
  { immediate: true },
)

watch(
  theme,
  (nextTheme) => {
    document.documentElement.dataset.theme = nextTheme
  },
  { immediate: true },
)
</script>

<template>
  <div class="site-shell">
    <header class="site-header">
      <div class="site-header-inner">
        <a class="brand" href="#top" @click="isViewerRoute && ($event.preventDefault(), goHome())">
          <img class="brand-icon" :src="navMacaronImage" alt="" draggable="false" />
          <span class="brand-label">{{ text.brand }}</span>
        </a>

        <div class="header-actions">
          <div class="language-toggle" role="group" :aria-label="text.languageLabel">
            <button
              type="button"
              :class="{ active: language === 'zh' }"
              :aria-pressed="language === 'zh'"
              @click="setLanguage('zh')"
            >
              中文
            </button>
            <button
              type="button"
              :class="{ active: language === 'en' }"
              :aria-pressed="language === 'en'"
              @click="setLanguage('en')"
            >
              English
            </button>
          </div>

          <button
            class="theme-toggle"
            type="button"
            :aria-label="nextThemeLabel"
            :title="nextThemeLabel"
            @click="toggleTheme"
          >
            <span
              class="theme-icon"
              :class="theme === 'light' ? 'dark' : 'light'"
              aria-hidden="true"
            >
              <span class="theme-icon-core" />
            </span>
          </button>
        </div>
      </div>
    </header>

    <main v-if="isViewerRoute && viewerFlavor && viewerModelUrl" class="detail-main">
      <section class="detail-page" :aria-labelledby="'detail-title'">
        <h1 id="detail-title" class="visually-hidden">{{ viewerTitle }}</h1>

        <button class="detail-back" type="button" @click="goHome">
          <span aria-hidden="true">←</span>
          <span>{{ text.backHome }}</span>
        </button>

        <div class="detail-layout">
          <section class="detail-viewer-panel" :aria-label="viewerTitle">
            <WindowNotesMacaronViewer
              :accessible-label="viewerTitle"
              :fallback-alt="viewerFlavor.imageAlt[language]"
              :fallback-image="viewerFlavor.src"
              :model-name="`${viewerFlavor.id}-macaron`"
              :model-url="viewerModelUrl"
              :theme="theme"
            />
          </section>
        </div>
      </section>
    </main>

    <main v-else id="top">
      <section class="hero" aria-labelledby="hero-title">
        <div class="hero-copy">
          <h1 id="hero-title" :class="{ 'is-english': language === 'en' }">
            <template v-if="language === 'zh'">
              <span class="title-segment">想從哪顆</span><span class="title-segment">開始吃呢？</span>
            </template>
            <template v-else>{{ text.title }}</template>
          </h1>
          <p v-for="paragraph in text.introduction" :key="paragraph">{{ paragraph }}</p>
        </div>

        <div ref="macaronScene" class="macaron-scene" role="group" :aria-label="text.collectionLabel">
          <img
            class="macaron-box-layer macaron-box-back"
            :src="macaronBoxImage"
            alt=""
            draggable="false"
          />

          <button
            v-for="(macaron, index) in macarons"
            :key="macaron.name"
            class="macaron"
            :class="`macaron-row-${macaron.row}`"
            :style="{ left: macaron.left, top: macaron.top, '--wave-index': index }"
            type="button"
            :aria-label="macaron.name"
            @click="handleMacaronClick(macaron.targetId)"
          >
            <img class="macaron-art" :src="macaron.src" alt="" draggable="false" />
          </button>

          <img
            class="macaron-box-layer macaron-box-front"
            :src="macaronBoxImage"
            alt=""
            draggable="false"
          />
        </div>
      </section>

      <section
        v-for="section in flavorSections"
        :key="section.id"
        class="signature-section"
        :class="`signature-section-${section.id}`"
        :aria-labelledby="`${section.id}-title`"
      >
        <header class="signature-heading">
          <h2 :id="`${section.id}-title`">{{ section.title }}</h2>
        </header>

        <div class="signature-grid" :class="`signature-grid-${section.layout}`">
          <article
            v-for="flavor in section.flavors"
            :id="flavor.id"
            :key="flavor.id"
            class="signature-card"
            :class="{ 'is-scroll-highlighted': highlightedFlavorId === flavor.id }"
          >
            <div
              class="signature-art"
              :style="{
                '--card-color': flavor.color,
                '--card-color-dark': flavor.darkColor,
              }"
            >
              <img
                :src="flavor.src"
                :alt="flavor.imageAlt[language]"
                loading="lazy"
                draggable="false"
              />
            </div>

            <div class="signature-card-body">
              <p class="signature-category">{{ flavor.category[language] }}</p>
              <h3 :class="{ 'is-english': language === 'en' }">{{ flavor.title[language] }}</h3>
              <p class="signature-flavor">{{ flavor.flavor[language] }}</p>
              <p class="signature-description">
                <span class="signature-description-layout signature-description-layout-desktop">
                  <span
                    v-for="line in flavor.description[language]"
                    :key="line"
                    class="signature-description-line"
                  >
                    {{ line }}
                  </span>
                </span>
                <span class="signature-description-layout signature-description-layout-mobile">
                  <span
                    v-for="line in flavor.mobileDescription[language]"
                    :key="line"
                    class="signature-description-line"
                  >
                    {{ line }}
                  </span>
                </span>
              </p>
              <p class="signature-cta">
                <span>{{ text.signatureCta }}</span>
                <span aria-hidden="true">→</span>
              </p>
            </div>
          </article>
        </div>
      </section>
    </main>
  </div>
</template>
