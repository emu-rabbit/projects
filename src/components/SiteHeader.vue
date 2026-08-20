<script setup lang="ts">
import type { PortfolioCopy } from '../data/portfolio'
import type { Language, Theme } from '../types/portfolio'

defineProps<{
  copy: PortfolioCopy
  language: Language
  languageHrefs: Record<Language, string>
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
          <a
            :href="languageHrefs.zh"
            hreflang="zh-Hant"
            lang="zh-Hant"
            :class="{ active: language === 'zh' }"
            :aria-current="language === 'zh' ? 'page' : undefined"
            @click.prevent="emit('setLanguage', 'zh')"
          >
            中文
          </a>
          <a
            :href="languageHrefs.en"
            hreflang="en"
            lang="en"
            :class="{ active: language === 'en' }"
            :aria-current="language === 'en' ? 'page' : undefined"
            @click.prevent="emit('setLanguage', 'en')"
          >
            English
          </a>
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
