<script setup lang="ts">
import { computed } from 'vue'
import type { MacaronDetail } from '../data/macaronDetails'
import type { Language, Theme } from '../types/portfolio'
import MacaronGallery from './MacaronGallery.vue'

interface MacaronDetailUiCopy {
  backHome: string
  projectLinksLabel: string
  previousImage: string
  nextImage: string
  openImage: string
  closeImage: string
  zoomIn: string
  zoomOut: string
  resetZoom: string
  loadingImage: string
  imageLoadError: string
}

const props = defineProps<{
  detail: MacaronDetail
  language: Language
  theme: Theme
  ui: MacaronDetailUiCopy
}>()

const emit = defineEmits<{
  back: []
}>()

const content = computed(() => ({
  category: props.detail.category[props.language],
  title: props.detail.title[props.language],
  paragraphs: props.detail.paragraphs[props.language],
  closing: props.detail.closing[props.language],
  galleryLabel: props.detail.galleryLabel[props.language],
  gallery: props.detail.gallery.map((image) => ({
    src: image.src,
    alt: image.alt[props.language],
    caption: image.caption[props.language],
  })),
  links: props.detail.links.map((link) => ({
    href: link.href,
    label: link.label[props.language],
  })),
}))

const galleryPalette = computed(() => ({
  '--gallery-card-background': props.theme === 'dark'
    ? props.detail.palette.darkColor
    : `color-mix(in srgb, ${props.detail.palette.color} 76%, var(--canvas))`,
  '--gallery-card-glow': props.theme === 'dark'
    ? 'rgb(255 255 255 / 8%)'
    : 'rgb(255 255 255 / 68%)',
}))
</script>

<template>
  <main class="detail-main">
    <section class="detail-page" aria-labelledby="detail-title" :style="galleryPalette">
      <button class="detail-back" type="button" @click="emit('back')">
        <span aria-hidden="true">←</span>
        <span>{{ ui.backHome }}</span>
      </button>

      <div class="detail-layout">
        <article class="detail-copy">
          <p class="detail-category">{{ content.category }}</p>
          <h1 id="detail-title" :class="{ 'is-english': language === 'en' }">
            {{ content.title }}
          </h1>
          <div class="detail-prose">
            <p v-for="paragraph in content.paragraphs" :key="paragraph">
              {{ paragraph }}
            </p>
          </div>
          <blockquote>{{ content.closing }}</blockquote>
          <nav class="detail-links" :aria-label="ui.projectLinksLabel">
            <a
              v-for="link in content.links"
              :key="link.href"
              class="detail-link"
              :href="link.href"
              target="_blank"
              rel="noreferrer"
            >
              <span>{{ link.label }}</span>
              <span aria-hidden="true">↗</span>
            </a>
          </nav>
        </article>

        <MacaronGallery
          :images="content.gallery"
          :label="content.galleryLabel"
          :previous-label="ui.previousImage"
          :next-label="ui.nextImage"
          :open-label="ui.openImage"
          :close-label="ui.closeImage"
          :zoom-in-label="ui.zoomIn"
          :zoom-out-label="ui.zoomOut"
          :reset-zoom-label="ui.resetZoom"
          :loading-label="ui.loadingImage"
          :load-error-label="ui.imageLoadError"
        />
      </div>
    </section>
  </main>
</template>

<style scoped>
.detail-main,
.detail-page {
  min-height: 100svh;
}

.detail-page {
  display: flex;
  flex-direction: column;
  padding: clamp(24px, 4vh, 44px) 0 clamp(56px, 8vh, 96px);
}

.detail-back {
  display: inline-flex;
  min-height: 36px;
  align-items: center;
  align-self: flex-start;
  gap: 10px;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--ink);
  cursor: pointer;
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  transition: color 180ms ease, transform 180ms ease;
}

.detail-back [aria-hidden="true"] {
  font-size: 1rem;
  line-height: 1;
}

.detail-layout {
  display: grid;
  width: 100%;
  max-width: 1280px;
  min-height: 0;
  flex: 1;
  grid-template-columns: minmax(380px, 0.95fr) minmax(0, 1.05fr);
  align-items: center;
  gap: clamp(54px, 7vw, 104px);
  margin: clamp(48px, 7vh, 82px) auto 0;
}

.detail-copy {
  min-width: 0;
  max-width: 570px;
}

.detail-category {
  margin: 0 0 18px;
  color: var(--accent);
  font-size: 0.78rem;
  letter-spacing: 0.12em;
}

.detail-copy h1 {
  max-width: 10em;
  margin: 0;
  font-size: clamp(2.5rem, 4.2vw, 4.65rem);
  font-weight: 400;
  letter-spacing: -0.065em;
  line-height: 1.16;
  text-wrap: balance;
}

.detail-copy h1.is-english {
  max-width: 8.5em;
  font-size: clamp(2.35rem, 3.75vw, 4.15rem);
  letter-spacing: -0.04em;
}

.detail-prose {
  margin-top: 38px;
}

.detail-prose p {
  margin: 0;
  color: var(--ink);
  font-size: clamp(0.96rem, 1.08vw, 1.04rem);
  letter-spacing: 0.02em;
  line-height: 2.05;
}

.detail-prose p + p {
  margin-top: 15px;
}

.detail-copy blockquote {
  margin: 31px 0 0;
  padding: 4px 0 4px 19px;
  border-left: 2px solid var(--accent);
  color: var(--ink);
  font-size: clamp(1rem, 1.3vw, 1.18rem);
  letter-spacing: 0.035em;
  line-height: 1.8;
}

.detail-links {
  display: flex;
  flex-wrap: wrap;
  gap: 14px 26px;
  margin-top: 27px;
}

.detail-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid var(--line);
  color: var(--ink-soft);
  font-size: 0.78rem;
  letter-spacing: 0.045em;
  text-decoration: none;
  transition: border-color 180ms ease, color 180ms ease;
}

.detail-link [aria-hidden="true"] {
  transition: transform 180ms ease;
}

@media (hover: hover) and (pointer: fine) {
  .detail-back:hover {
    color: var(--accent);
    transform: translateX(-3px);
  }

  .detail-link:hover {
    border-color: var(--accent);
    color: var(--ink);
  }

  .detail-link:hover [aria-hidden="true"] {
    transform: translate(2px, -2px);
  }
}

@media (max-width: 1100px) {
  .detail-layout {
    max-width: 860px;
    grid-template-columns: minmax(0, 1fr);
    gap: clamp(44px, 7vw, 72px);
  }

  .detail-copy {
    max-width: 720px;
  }

  .detail-copy h1,
  .detail-copy h1.is-english {
    max-width: 12em;
  }
}

@media (max-width: 680px) {
  .detail-page {
    padding: 18px 0 56px;
  }

  .detail-back {
    min-height: 40px;
    font-size: 0.74rem;
  }

  .detail-layout {
    gap: 48px;
    margin-top: 34px;
  }

  .detail-copy h1 {
    max-width: 9em;
    font-size: clamp(2.2rem, 10.5vw, 3rem);
  }

  .detail-copy h1.is-english {
    max-width: 8em;
    font-size: clamp(2.15rem, 9.5vw, 2.8rem);
  }

  .detail-prose p {
    font-size: 0.92rem;
  }

  .detail-copy blockquote {
    margin-top: 27px;
    font-size: 1rem;
  }
}
</style>
