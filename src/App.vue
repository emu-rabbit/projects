<script setup lang="ts">
import { computed, ref, watch } from 'vue'

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

const macaronBoxImage = new URL('../assets/hero/macaron-box-with-rabbit-transparent.webp', import.meta.url).href

const languageStorageKey = 'portfolio-language'
const themeStorageKey = 'portfolio-theme'

const getInitialLanguage = (): Language => {
  const savedLanguage = window.localStorage.getItem(languageStorageKey)
  return savedLanguage === 'zh' || savedLanguage === 'en' ? savedLanguage : 'zh'
}

const getInitialTheme = (): Theme => {
  const savedTheme = window.localStorage.getItem(themeStorageKey)

  if (savedTheme === 'light' || savedTheme === 'dark') {
    return savedTheme
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

const language = ref<Language>(getInitialLanguage())
const theme = ref<Theme>(getInitialTheme())

const text = computed(() => copy[language.value])
const nextThemeLabel = computed(() =>
  theme.value === 'light' ? text.value.darkTheme : text.value.lightTheme,
)

const setLanguage = (nextLanguage: Language) => {
  language.value = nextLanguage
}

const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
}

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
    window.localStorage.setItem(themeStorageKey, nextTheme)
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

        <div class="macaron-scene">
          <img
            class="macaron-box-art"
            :src="macaronBoxImage"
            :alt="text.collectionLabel"
            draggable="false"
          />
        </div>
      </section>
    </main>
  </div>
</template>
