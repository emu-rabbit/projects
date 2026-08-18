<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import MacaronDetailPage from './components/MacaronDetailPage.vue'
import PortfolioHomePage from './components/PortfolioHomePage.vue'
import SiteHeader from './components/SiteHeader.vue'
import { usePortfolioPreferences } from './composables/usePortfolioPreferences'
import { macaronDetailsBySlug } from './data/macaronDetails'
import { portfolioCopy } from './data/portfolio'

const { language, theme, setLanguage, toggleTheme } = usePortfolioPreferences()
const currentHash = ref(window.location.hash)
let homeScrollY = 0
let routeScrollVersion = 0

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

const isDetailHash = (hash: string) => {
  const match = hash.match(/^#\/macarons\/([^/?#]+)$/)
  return match ? macaronDetailsBySlug.has(match[1]) : false
}

const scrollAfterRouteRender = async (top: number) => {
  const version = ++routeScrollVersion

  await nextTick()
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(() => {
      if (version === routeScrollVersion) {
        window.scrollTo({ top, behavior: 'auto' })
      }
    })
  })
}

const rememberHomeScrollBeforeNavigation = (event: MouseEvent) => {
  if (currentDetail.value) {
    return
  }

  const target = event.target
  const link = target instanceof Element ? target.closest<HTMLAnchorElement>('a[href]') : null

  if (link && isDetailHash(link.hash)) {
    homeScrollY = window.scrollY
  }
}

const syncRoute = () => {
  const wasDetail = currentDetail.value !== null
  const nextHash = window.location.hash
  const willBeDetail = isDetailHash(nextHash)

  if (!wasDetail && willBeDetail) {
    homeScrollY = window.scrollY
  }

  currentHash.value = nextHash

  if (willBeDetail) {
    void scrollAfterRouteRender(0)
  } else if (wasDetail) {
    void scrollAfterRouteRender(homeScrollY)
  }
}

const goHome = () => {
  window.location.hash = ''
}

onMounted(() => {
  window.addEventListener('click', rememberHomeScrollBeforeNavigation, { capture: true })
  window.addEventListener('hashchange', syncRoute)

  if (currentDetail.value) {
    void scrollAfterRouteRender(0)
  }
})

onBeforeUnmount(() => {
  routeScrollVersion += 1
  window.removeEventListener('click', rememberHomeScrollBeforeNavigation, { capture: true })
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
      :theme="theme"
      :ui="detailUi"
      @back="goHome"
    />
    <PortfolioHomePage v-else :copy="copy" :language="language" />
  </div>
</template>
