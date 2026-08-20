<script setup lang="ts">
import { macaronDetailsBySlug } from '../data/macaronDetails'
import type { FlavorSection } from '../data/portfolio'
import { portfolioPath } from '../routing/portfolioRoute'
import type { Language } from '../types/portfolio'

defineProps<{
  section: FlavorSection
  language: Language
  cta: string
  highlightedFlavorId: string | null
}>()

const emit = defineEmits<{
  openDetail: [slug: string]
}>()
</script>

<template>
  <section
    class="signature-section"
    :class="`signature-section-${section.id}`"
    :aria-labelledby="`${section.id}-title`"
  >
    <header class="signature-heading">
      <h2 :id="`${section.id}-title`">{{ section.title }}</h2>
    </header>

    <div class="signature-grid" :class="`signature-grid-${section.layout}`">
      <article
        v-for="flavor in section.flavors"
        :id="flavor.id"
        :key="flavor.id"
        class="signature-card"
        :class="{
          'is-scroll-highlighted': highlightedFlavorId === flavor.id,
          'is-clickable': macaronDetailsBySlug.has(flavor.id),
        }"
      >
        <div
          class="signature-art"
          :style="{ '--card-color': flavor.color, '--card-color-dark': flavor.darkColor }"
        >
          <img :src="flavor.src" :alt="flavor.imageAlt[language]" loading="lazy" draggable="false" />
        </div>

        <div class="signature-card-body">
          <p class="signature-category">{{ flavor.category[language] }}</p>
          <h3 :class="{ 'is-english': language === 'en' }">{{ flavor.title[language] }}</h3>
          <p class="signature-flavor">{{ flavor.flavor[language] }}</p>
          <p class="signature-description">
            <span class="signature-description-layout signature-description-layout-desktop">
              <span v-for="line in flavor.description[language]" :key="line" class="signature-description-line">
                {{ line }}
              </span>
            </span>
            <span class="signature-description-layout signature-description-layout-mobile">
              <span v-for="line in flavor.mobileDescription[language]" :key="line" class="signature-description-line">
                {{ line }}
              </span>
            </span>
          </p>
          <a
            v-if="macaronDetailsBySlug.has(flavor.id)"
            class="signature-cta signature-cta-link"
            :href="portfolioPath(language, flavor.id)"
            @click.prevent="emit('openDetail', flavor.id)"
          >
            <span>{{ cta }}</span>
            <span aria-hidden="true">→</span>
          </a>
          <p v-else class="signature-cta">
            <span>{{ cta }}</span>
            <span aria-hidden="true">→</span>
          </p>
        </div>
      </article>
    </div>
  </section>
</template>
