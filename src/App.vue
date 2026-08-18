<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import MacaronDetailPage from './components/MacaronDetailPage.vue'
import PortfolioHomePage from './components/PortfolioHomePage.vue'
import SiteHeader from './components/SiteHeader.vue'
import { usePortfolioPreferences } from './composables/usePortfolioPreferences'
import { macaronDetailsBySlug } from './data/macaronDetails'
import { portfolioCopy } from './data/portfolio'

const { language, theme, setLanguage, toggleTheme } = usePortfolioPreferences()
const currentHash = ref(window.location.hash)

const copy = computed(() => portfolioCopy[language.value])
const detailSlug = computed(() => {
  const match = currentHash.value.match(/^#\/macarons\/([^/?#]+)$/)
  return match?.[1] ?? null
})
const currentDetail = computed(() => {
  const slug = detailSlug.value
  return slug ? macaronDetailsBySlug.get(slug) ?? null : null
})
const detailUi = computed(() => ({
  backHome: copy.value.backHome,
  projectLinksLabel: copy.value.projectLinksLabel,
  previousImage: copy.value.previousImage,
  nextImage: copy.value.nextImage,
  openImage: copy.value.openImage,
  closeImage: copy.value.closeImage,
  zoomIn: copy.value.zoomIn,
  zoomOut: copy.value.zoomOut,
  resetZoom: copy.value.resetZoom,
  loadingImage: copy.value.loadingImage,
  imageLoadError: copy.value.imageLoadError,
}))

const syncRoute = () => {
  currentHash.value = window.location.hash
  window.scrollTo({ top: 0, behavior: 'auto' })
}

const goHome = () => {
  window.location.hash = ''
}

onMounted(() => {
  window.addEventListener('hashchange', syncRoute)

  if (currentDetail.value) {
    window.scrollTo({ top: 0, behavior: 'auto' })
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('hashchange', syncRoute)
})
</script>

<template>
  <div class="site-shell">
    <SiteHeader
      v-if="!currentDetail"
      :copy="copy"
      :language="language"
      :theme="theme"
      @set-language="setLanguage"
      @toggle-theme="toggleTheme"
    />

    <MacaronDetailPage
      v-if="currentDetail"
      :detail="currentDetail"
      :language="language"
      :ui="detailUi"
      @back="goHome"
    />
    <PortfolioHomePage v-else :copy="copy" :language="language" />
  </div>
</template>
