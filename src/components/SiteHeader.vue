<script setup lang="ts">
import type { PortfolioCopy } from '../data/portfolio'
import type { Language, Theme } from '../types/portfolio'

defineProps<{
  copy: PortfolioCopy
  language: Language
  theme: Theme
}>()

const emit = defineEmits<{
  setLanguage: [language: Language]
  toggleTheme: []
}>()

const navMacaronImage = new URL('../../assets/ui/nav-macaron.svg', import.meta.url).href
</script>

<template>
  <header class="site-header">
    <div class="site-header-inner">
      <a class="brand" href="#top">
        <img class="brand-icon" :src="navMacaronImage" alt="" draggable="false" />
        <span class="brand-label">{{ copy.brand }}</span>
      </a>

      <div class="header-actions">
        <div class="language-toggle" role="group" :aria-label="copy.languageLabel">
          <button
            type="button"
            :class="{ active: language === 'zh' }"
            :aria-pressed="language === 'zh'"
            @click="emit('setLanguage', 'zh')"
          >
            中文
          </button>
          <button
            type="button"
            :class="{ active: language === 'en' }"
            :aria-pressed="language === 'en'"
            @click="emit('setLanguage', 'en')"
          >
            English
          </button>
        </div>

        <button
          class="theme-toggle"
          type="button"
          :aria-label="theme === 'light' ? copy.darkTheme : copy.lightTheme"
          :title="theme === 'light' ? copy.darkTheme : copy.lightTheme"
          @click="emit('toggleTheme')"
        >
          <span class="theme-icon" :class="theme === 'light' ? 'dark' : 'light'" aria-hidden="true">
            <span class="theme-icon-core" />
          </span>
        </button>
      </div>
    </div>
  </header>
</template>
