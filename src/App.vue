<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

type Language = 'zh' | 'en'
type Theme = 'light' | 'dark'

const copy = {
  zh: {
    brand: '絵夢羽さ沂的作品集',
    title: '想從哪顆開始吃呢？',
    introduction: [
      '不知何處而來的兔子推給你了一盒馬卡龍，從她的表情看起來是她的自信之作。',
      '裡面每顆都飽滿而各有特色，像是被精心設計和烘焙的小傢伙。拿起來，左右看一看，選擇你有興趣的馬卡龍吃下去吧！',
    ],
    collectionLabel: '一盒緊湊排列的十顆馬卡龍',
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
    languageLabel: 'Switch language',
    lightTheme: 'Switch to light theme',
    darkTheme: 'Switch to dark theme',
  },
} as const

const macaronBoxImage = new URL('../assets/hero/macaron-box-empty.webp', import.meta.url).href

const macarons = [
  { name: 'Frozen Rabbit Workshop', image: 'workshop.webp', left: '4.4%', top: '15%', row: 0 },
  { name: 'Frozen Rabbit Tome', image: 'tome.webp', left: '22.9%', top: '13.7%', row: 0 },
  { name: 'Boundary Notes', image: 'boundary-notes.webp', left: '40.7%', top: '14.7%', row: 0 },
  { name: 'Emu Rabbit Github io', image: 'emu-rabbit.webp', left: '58.1%', top: '13.5%', row: 0 },
  { name: 'LinkArray', image: 'link-array.webp', left: '75%', top: '14.6%', row: 0 },
  { name: 'Vue Router Rule', image: 'vue-router-rule.webp', left: '2.5%', top: '49.1%', row: 1 },
  { name: 'Dandelifeon', image: 'dandelifeon.webp', left: '20.9%', top: '47.9%', row: 1 },
  { name: 'nAnB', image: 'nanb.webp', left: '39.6%', top: '49.2%', row: 1 },
  { name: '75 Alchohol', image: '75-alchohol.webp', left: '57.7%', top: '47.4%', row: 1 },
  { name: '50 Hiragana Test', image: '50-hiragana-test.webp', left: '75.1%', top: '48.7%', row: 1 },
].map((macaron) => ({
  ...macaron,
  src: new URL(`../assets/macarons-web/${macaron.image}`, import.meta.url).href,
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
const macaronScene = ref<HTMLElement | null>(null)

let macaronElements: HTMLElement[] = []
let motionFrame = 0
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
})

onBeforeUnmount(() => {
  clearMacaronMotion()
  unlockMacaronWave()
  reducedMotionQuery?.removeEventListener('change', handleMotionPreferenceChange)
  window.removeEventListener('wheel', handleWheel)
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('touchstart', handleTouchStart)
  window.removeEventListener('touchmove', handleTouchMove)
  window.removeEventListener('touchend', handleTouchEnd)
  window.removeEventListener('touchcancel', handleTouchEnd)
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
      <a class="brand" href="#top">{{ text.brand }}</a>

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
    </header>

    <main id="top">
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

        <div ref="macaronScene" class="macaron-scene" role="img" :aria-label="text.collectionLabel">
          <img
            class="macaron-box-layer macaron-box-back"
            :src="macaronBoxImage"
            alt=""
            draggable="false"
          />

          <div
            v-for="(macaron, index) in macarons"
            :key="macaron.name"
            class="macaron"
            :class="`macaron-row-${macaron.row}`"
            :style="{ left: macaron.left, top: macaron.top, '--wave-index': index }"
          >
            <img class="macaron-art" :src="macaron.src" alt="" draggable="false" />
          </div>

          <img
            class="macaron-box-layer macaron-box-front"
            :src="macaronBoxImage"
            alt=""
            draggable="false"
          />
        </div>
      </section>
    </main>
  </div>
</template>
