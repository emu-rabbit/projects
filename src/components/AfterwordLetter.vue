<script setup lang="ts">
import { defineAsyncComponent, onBeforeUnmount, ref } from 'vue'
import type { AfterwordCopy } from '../data/portfolio'
import type { Language, Theme } from '../types/portfolio'

const props = defineProps<{
  copy: AfterwordCopy
  language: Language
  theme: Theme
}>()

const WindowNotesMacaronViewer = defineAsyncComponent(
  () => import('./WindowNotesMacaronViewer.vue'),
)

const closedCardImage = new URL('../../assets/letter/card-closed.webp', import.meta.url).href
const openCardImage = new URL('../../assets/letter/card-open.webp', import.meta.url).href
const modelFallbackImage = new URL('../../assets/macarons-web/emu-rabbit.webp', import.meta.url).href
const modelUrl = new URL('../../assets/models/window-notes-macaron.glb', import.meta.url).href

const isOpening = ref(false)
const isOpen = ref(false)
const modelRequested = ref(false)
const openedHeading = ref<HTMLHeadingElement | null>(null)
let openingTimer = 0

const finishOpening = () => {
  isOpen.value = true
}

const focusOpenedHeading = () => {
  openedHeading.value?.focus()
}

const openCard = () => {
  if (isOpening.value || isOpen.value) return

  isOpening.value = true
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    finishOpening()
    return
  }

  openingTimer = window.setTimeout(() => {
    openingTimer = 0
    finishOpening()
  }, 900)
}

onBeforeUnmount(() => {
  if (openingTimer) window.clearTimeout(openingTimer)
})
</script>

<template>
  <section class="afterword-section">
    <Transition name="letter-section" mode="out-in" @after-enter="focusOpenedHeading">
      <div v-if="!isOpen" key="teaser" class="afterword-teaser">
        <h2 id="afterword-title" :aria-label="copy.title">
          <span v-for="line in copy.titleLines" :key="line" class="afterword-title-line" aria-hidden="true">
            {{ line }}
          </span>
        </h2>

        <div class="letter-card-stage" :class="{ 'is-opening': isOpening }" aria-hidden="true">
          <img class="letter-card-image letter-card-closed" :src="closedCardImage" alt="" />
          <img class="letter-card-image letter-card-open" :src="openCardImage" alt="" />
        </div>

        <p class="visually-hidden">{{ copy.cardAlt }}</p>
        <button class="letter-action" type="button" :disabled="isOpening" @click="openCard">
          <span>{{ isOpening ? copy.openingCard : copy.openCard }}</span>
          <span aria-hidden="true">↗</span>
        </button>
      </div>

      <article v-else key="content" class="letter-paper" aria-labelledby="afterword-title-opened">
        <h2
          id="afterword-title-opened"
          ref="openedHeading"
          :class="{ 'is-english': language === 'en' }"
          :aria-label="copy.openedTitle"
          tabindex="-1"
        >
          {{ copy.openedTitle }}
        </h2>

        <div class="letter-copy">
          <p v-for="paragraph in copy.paragraphs" :key="paragraph">{{ paragraph }}</p>
        </div>

        <div class="letter-model-area">
          <Suspense v-if="modelRequested">
            <WindowNotesMacaronViewer
              :accessible-label="copy.viewerLabel"
              :fallback-alt="copy.modelFallbackAlt"
              :fallback-image="modelFallbackImage"
              :interaction-hint="copy.interactionHint"
              :loading-label="copy.loadingModel"
              :load-error="copy.modelLoadError"
              :diagnostic-label="copy.modelDiagnosticLabel"
              :model-url="modelUrl"
              :reset-label="copy.resetView"
              :theme="theme"
            />
            <template #fallback>
              <div class="letter-model-preparing" role="status">{{ copy.preparingViewer }}</div>
            </template>
          </Suspense>

          <div v-else class="letter-model-gate">
            <img :src="modelFallbackImage" :alt="copy.modelFallbackAlt" />
            <button class="letter-action letter-model-action" type="button" @click="modelRequested = true">
              <span>{{ copy.loadModel }}</span>
              <span aria-hidden="true">→</span>
            </button>
          </div>
        </div>
      </article>
    </Transition>
  </section>
</template>

<style scoped>
.afterword-section {
  padding: clamp(96px, 12vw, 168px) 0 clamp(110px, 14vw, 190px);
  border-top: 1px solid var(--line);
}

.afterword-teaser {
  display: flex;
  min-height: min(760px, 80svh);
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.afterword-teaser h2,
.letter-paper h2 {
  margin: 0;
  font-size: clamp(2.15rem, 4.4vw, 4.35rem);
  font-weight: 400;
  letter-spacing: -0.065em;
  line-height: 1.18;
}

.afterword-teaser h2 {
  width: 100%;
}

.afterword-title-line {
  display: block;
}

.letter-card-stage {
  position: relative;
  width: min(100%, 680px);
  margin: clamp(34px, 5vw, 62px) auto clamp(22px, 3vw, 36px);
  aspect-ratio: 3 / 2;
  filter: drop-shadow(0 22px 20px rgb(71 48 35 / 13%));
}

.letter-card-image {
  position: absolute;
  inset: 0;
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  user-select: none;
  transition:
    opacity 520ms ease,
    transform 760ms cubic-bezier(0.22, 0.72, 0.25, 1);
}

.letter-card-closed {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.letter-card-open {
  opacity: 0;
  transform: translateY(12px) scale(0.975);
}

.letter-card-stage.is-opening .letter-card-closed {
  opacity: 0;
  transform: translateY(-10px) scale(0.96);
}

.letter-card-stage.is-opening .letter-card-open {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.letter-action {
  display: inline-flex;
  min-height: 48px;
  align-items: center;
  justify-content: center;
  gap: 13px;
  padding: 11px 22px;
  border: 1px solid color-mix(in srgb, var(--accent) 48%, var(--line));
  border-radius: 999px;
  background: var(--control);
  box-shadow: 0 8px 24px var(--control-shadow);
  color: var(--accent);
  cursor: pointer;
  font-size: 0.86rem;
  letter-spacing: 0.06em;
  transition:
    background-color 180ms ease,
    box-shadow 220ms ease,
    transform 220ms ease;
}

.letter-action:disabled {
  cursor: wait;
  opacity: 0.72;
}

.letter-paper {
  position: relative;
  overflow: hidden;
  padding: clamp(42px, 7vw, 92px) clamp(24px, 8vw, 112px) clamp(34px, 7vw, 90px);
  border: 1px solid var(--line);
  border-radius: 36px;
  background:
    linear-gradient(90deg, transparent 0 8%, rgb(155 87 84 / 7%) 8% calc(8% + 1px), transparent calc(8% + 1px)),
    repeating-linear-gradient(0deg, transparent 0 38px, rgb(111 82 66 / 4%) 38px 39px),
    var(--card);
  box-shadow: 0 24px 70px var(--card-shadow);
}

.letter-paper::before {
  position: absolute;
  top: 0;
  right: 0;
  width: 180px;
  height: 180px;
  border-bottom: 1px solid var(--line);
  border-left: 1px solid var(--line);
  background: color-mix(in srgb, var(--card) 72%, var(--canvas));
  clip-path: polygon(100% 0, 0 0, 100% 100%);
  content: '';
  opacity: 0.72;
  pointer-events: none;
}

.letter-paper h2 {
  position: relative;
  width: min(100%, 13em);
  outline: 0;
}

.letter-paper h2.is-english {
  width: min(100%, 13em);
  letter-spacing: -0.04em;
}

.letter-paper h2::after {
  display: block;
  width: 42px;
  height: 2px;
  margin-top: 28px;
  border-radius: 999px;
  background: var(--accent);
  content: '';
}

.letter-copy {
  width: min(100%, 780px);
  margin: clamp(42px, 6vw, 70px) auto 0;
}

.letter-copy p {
  margin: 0;
  color: var(--ink-soft);
  font-size: clamp(0.96rem, 1.25vw, 1.08rem);
  letter-spacing: 0.035em;
  line-height: 2.05;
}

.letter-copy p + p {
  margin-top: 1.4em;
}

.letter-copy p:first-child {
  color: var(--ink);
  font-size: clamp(1.08rem, 1.5vw, 1.24rem);
}

.letter-copy p:last-child {
  margin-top: 2.3em;
  color: var(--ink);
}

.letter-model-area {
  margin-top: clamp(54px, 8vw, 92px);
}

.letter-model-gate,
.letter-model-preparing {
  position: relative;
  display: grid;
  min-height: clamp(420px, 58vw, 690px);
  place-items: center;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 30px;
  background:
    radial-gradient(circle at 50% 40%, var(--gallery-glow), transparent 48%),
    var(--gallery-surface);
}

.letter-model-gate img {
  display: block;
  width: min(70%, 560px);
  height: auto;
  filter: drop-shadow(0 14px 13px rgb(62 37 55 / 14%));
  opacity: 0.92;
}

.letter-model-action {
  position: absolute;
  bottom: clamp(22px, 4vw, 40px);
  max-width: calc(100% - 36px);
  background: var(--header-surface);
  backdrop-filter: blur(14px);
}

.letter-model-preparing {
  color: var(--ink-soft);
  letter-spacing: 0.05em;
}

.letter-section-enter-active,
.letter-section-leave-active {
  transition: opacity 360ms ease, transform 460ms cubic-bezier(0.22, 0.72, 0.25, 1);
}

.letter-section-enter-from,
.letter-section-leave-to {
  opacity: 0;
  transform: translateY(14px);
}

@media (hover: hover) and (pointer: fine) {
  .letter-action:not(:disabled):hover {
    background: var(--control-active);
    box-shadow: 0 12px 30px var(--control-shadow);
    transform: translateY(-2px);
  }
}

@media (max-width: 680px) {
  .afterword-section {
    padding: 84px 0 110px;
  }

  .afterword-teaser {
    min-height: 620px;
  }

  .afterword-teaser h2,
  .letter-paper h2 {
    font-size: clamp(2rem, 10vw, 3.2rem);
  }

  .letter-card-stage {
    width: calc(100% + 22px);
    margin-inline: -11px;
  }

  .letter-paper {
    padding: 42px 24px 24px;
    border-radius: 24px;
    background:
      repeating-linear-gradient(0deg, transparent 0 34px, rgb(111 82 66 / 4%) 34px 35px),
      var(--card);
  }

  .letter-paper::before {
    width: 100px;
    height: 100px;
  }

  .letter-copy p {
    font-size: 0.94rem;
    line-height: 1.95;
  }

  .letter-model-gate,
  .letter-model-preparing {
    min-height: min(116vw, 560px);
    border-radius: 24px;
  }

  .letter-model-gate img {
    width: 88%;
  }

  .letter-model-action {
    bottom: 18px;
    padding-inline: 17px;
    font-size: 0.75rem;
  }
}

</style>
