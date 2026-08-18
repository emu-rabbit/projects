import { ref, watch } from 'vue'
import type { Language, Theme } from '../types/portfolio'

const languageStorageKey = 'portfolio-language'
const themeStorageKey = 'portfolio-theme'

const readStorage = (key: string) => {
  try {
    return window.localStorage.getItem(key)
  } catch {
    return null
  }
}

const getInitialLanguage = (): Language => {
  const savedLanguage = readStorage(languageStorageKey)
  return savedLanguage === 'zh' || savedLanguage === 'en' ? savedLanguage : 'zh'
}

const getInitialTheme = (): Theme => {
  const savedTheme = readStorage(themeStorageKey)

  if (savedTheme === 'light' || savedTheme === 'dark') {
    return savedTheme
  }

  try {
    return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  } catch {
    return 'light'
  }
}

export const usePortfolioPreferences = () => {
  const language = ref<Language>(getInitialLanguage())
  const theme = ref<Theme>(getInitialTheme())

  const setLanguage = (nextLanguage: Language) => {
    language.value = nextLanguage
  }

  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'

    try {
      window.localStorage.setItem(themeStorageKey, theme.value)
    } catch {
      // Keep the in-session choice when storage is unavailable.
    }
  }

  watch(
    language,
    (nextLanguage) => {
      document.documentElement.lang = nextLanguage === 'zh' ? 'zh-Hant' : 'en'

      try {
        window.localStorage.setItem(languageStorageKey, nextLanguage)
      } catch {
        // Keep the in-session choice when storage is unavailable.
      }
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

  return {
    language,
    theme,
    setLanguage,
    toggleTheme,
  }
}
