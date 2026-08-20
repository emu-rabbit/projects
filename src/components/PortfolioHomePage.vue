<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { getFlavorSections, type PortfolioCopy } from '../data/portfolio'
import type { Language, Theme } from '../types/portfolio'
import AfterwordLetter from './AfterwordLetter.vue'
import FlavorSection from './FlavorSection.vue'
import MacaronHero from './MacaronHero.vue'

const props = defineProps<{
  copy: PortfolioCopy
  language: Language
  theme: Theme
}>()

const emit = defineEmits<{
  openDetail: [slug: string]
}>()

const highlightedFlavorId = ref<string | null>(null)
const flavorSections = computed(() => getFlavorSections(props.language))

let highlightFrame = 0
let scrollHighlightTimer = 0
let pendingScrollEnd: (() => void) | null = null
let reducedMotionQuery: MediaQueryList | null = null

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

  target.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth', block: 'start' })
}

const handleMotionPreferenceChange = () => {
  clearPendingScrollHighlight()
  highlightedFlavorId.value = null
}

onMounted(() => {
  reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  reducedMotionQuery.addEventListener('change', handleMotionPreferenceChange)
})

onBeforeUnmount(() => {
  clearPendingScrollHighlight()
  reducedMotionQuery?.removeEventListener('change', handleMotionPreferenceChange)
})
</script>

<template>
  <main id="top">
    <section class="hero" aria-labelledby="hero-title">
      <div class="hero-copy">
        <h1 id="hero-title" :class="{ 'is-english': language === 'en' }">
          <template v-if="language === 'zh'">
            <span class="title-segment">想從哪顆</span><span class="title-segment">開始吃呢？</span>
          </template>
          <template v-else>{{ copy.title }}</template>
        </h1>
        <p v-for="paragraph in copy.introduction" :key="paragraph">{{ paragraph }}</p>
      </div>

      <MacaronHero :collection-label="copy.collectionLabel" @select="scrollToFlavor" />
    </section>

    <FlavorSection
      v-for="section in flavorSections"
      :key="section.id"
      :section="section"
      :language="language"
      :cta="copy.signatureCta"
      :highlighted-flavor-id="highlightedFlavorId"
      @open-detail="emit('openDetail', $event)"
    />

    <AfterwordLetter :copy="copy.afterword" :language="language" :theme="theme" />
  </main>
</template>
