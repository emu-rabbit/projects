<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import MacaronDetailPage from './components/MacaronDetailPage.vue'
import PortfolioHomePage from './components/PortfolioHomePage.vue'
import SiteHeader from './components/SiteHeader.vue'
import { usePortfolioPreferences } from './composables/usePortfolioPreferences'
import { macaronDetailsBySlug } from './data/macaronDetails'
import { portfolioCopy } from './data/portfolio'
import { syncDocumentSeo } from './data/seo'
import {
  alternateLanguage,
  parseLegacyDetailHash,
  parsePortfolioRoute,
  portfolioPath,
  type PortfolioRoute,
} from './routing/portfolioRoute'
import type { Language } from './types/portfolio'

const initialRoute = parsePortfolioRoute(window.location.pathname)
const { language, theme, setLanguage, toggleTheme } = usePortfolioPreferences(initialRoute?.language)
const currentRoute = ref<PortfolioRoute>(initialRoute ?? { language: language.value, slug: null })
let homeScrollY = 0
let routeScrollVersion = 0

const copy = computed(() => portfolioCopy[language.value])
const currentDetail = computed(() => {
  const slug = currentRoute.value.slug
  return slug ? macaronDetailsBySlug.get(slug) ?? null : null
})
const currentSlug = computed(() => currentDetail.value?.slug ?? null)
const homeHref = computed(() => portfolioPath(language.value))
const languageHrefs = computed(() => ({
  zh: portfolioPath('zh'),
  en: portfolioPath('en'),
}))
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
const nextLanguage = computed(() => alternateLanguage(language.value))
const alternateLanguageHref = computed(() => portfolioPath(nextLanguage.value, currentSlug.value))
const alternateLanguageLabel = computed(() => language.value === 'zh' ? 'English' : '中文')
const alternateLanguageAriaLabel = computed(() => (
  language.value === 'zh' ? 'Switch to English' : '切換為中文'
))

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

const applyRoute = (nextRoute: PortfolioRoute, restoreHome = true) => {
  const previousDetail = currentDetail.value !== null
  const nextDetail = nextRoute.slug ? macaronDetailsBySlug.has(nextRoute.slug) : false

  currentRoute.value = {
    language: nextRoute.language,
    slug: nextDetail ? nextRoute.slug : null,
  }
  setLanguage(nextRoute.language)
  syncDocumentSeo(nextRoute.language, nextDetail ? nextRoute.slug : null)

  if (nextDetail) {
    void scrollAfterRouteRender(0)
  } else if (previousDetail && restoreHome) {
    void scrollAfterRouteRender(homeScrollY)
  }
}

const navigate = (nextLanguage: Language, slug: string | null, replace = false) => {
  const validSlug = slug && macaronDetailsBySlug.has(slug) ? slug : null

  if (!currentDetail.value && validSlug) {
    homeScrollY = window.scrollY
  }

  const nextRoute = { language: nextLanguage, slug: validSlug }
  const nextPath = portfolioPath(nextLanguage, validSlug)
  window.history[replace ? 'replaceState' : 'pushState']({}, '', nextPath)
  applyRoute(nextRoute)
}

const openDetail = (slug: string) => navigate(language.value, slug)
const goHome = () => navigate(language.value, null)
const changeLanguage = (nextLanguage: Language) => navigate(nextLanguage, currentSlug.value)

const syncRouteFromLocation = () => {
  const nextRoute = parsePortfolioRoute(window.location.pathname)

  if (nextRoute) {
    applyRoute(nextRoute)
  }
}

onMounted(() => {
  window.history.scrollRestoration = 'manual'
  window.addEventListener('popstate', syncRouteFromLocation)

  const legacySlug = parseLegacyDetailHash(window.location.hash)
  if (legacySlug && macaronDetailsBySlug.has(legacySlug)) {
    window.history.replaceState({}, '', portfolioPath(language.value, legacySlug))
    applyRoute({ language: language.value, slug: legacySlug }, false)
    return
  }

  if (!initialRoute) {
    window.history.replaceState({}, '', portfolioPath(language.value))
    currentRoute.value = { language: language.value, slug: null }
  }

  syncDocumentSeo(language.value, currentSlug.value)
  if (currentDetail.value) {
    void scrollAfterRouteRender(0)
  }
})

onBeforeUnmount(() => {
  routeScrollVersion += 1
  window.removeEventListener('popstate', syncRouteFromLocation)
})
</script>

<template>
  <div class="site-shell">
    <SiteHeader
      v-if="!currentDetail"
      :copy="copy"
      :language="language"
      :language-hrefs="languageHrefs"
      :theme="theme"
      @set-language="changeLanguage"
      @toggle-theme="toggleTheme"
    />

    <MacaronDetailPage
      v-if="currentDetail"
      :detail="currentDetail"
      :language="language"
      :home-href="homeHref"
      :alternate-language-href="alternateLanguageHref"
      :alternate-language-label="alternateLanguageLabel"
      :alternate-language-aria-label="alternateLanguageAriaLabel"
      :theme="theme"
      :ui="detailUi"
      @back="goHome"
      @set-language="changeLanguage(nextLanguage)"
    />
    <PortfolioHomePage
      v-else
      :copy="copy"
      :language="language"
      :theme="theme"
      @open-detail="openDetail"
    />
  </div>
</template>
