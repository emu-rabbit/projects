<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'

type GalleryImage = {
  src: string
  alt: string
  caption: string
}

const props = defineProps<{
  images: readonly GalleryImage[]
  label: string
  previousLabel: string
  nextLabel: string
  openLabel: string
  closeLabel: string
  zoomInLabel: string
  zoomOutLabel: string
  resetZoomLabel: string
}>()

const currentIndex = ref(0)
const lightboxOpen = ref(false)
const zoom = ref(1)
const panX = ref(0)
const panY = ref(0)
const dialog = ref<HTMLElement | null>(null)
const openButton = ref<HTMLButtonElement | null>(null)

const pointers = new Map<number, { x: number; y: number }>()
let pinchDistance = 0
let pinchZoom = 1
let previousBodyOverflow = ''
let backgroundRoot: HTMLElement | null = null

const clampZoom = (value: number) => Math.min(5, Math.max(1, value))

const resetTransform = () => {
  zoom.value = 1
  panX.value = 0
  panY.value = 0
  pointers.clear()
  pinchDistance = 0
  pinchZoom = 1
}

const constrainPan = () => {
  if (zoom.value <= 1) {
    panX.value = 0
    panY.value = 0
    return
  }

  const width = dialog.value?.clientWidth ?? window.innerWidth
  const height = dialog.value?.clientHeight ?? window.innerHeight
  const maximumX = width * (zoom.value - 1) * 0.5
  const maximumY = height * (zoom.value - 1) * 0.5
  panX.value = Math.min(maximumX, Math.max(-maximumX, panX.value))
  panY.value = Math.min(maximumY, Math.max(-maximumY, panY.value))
}

const setZoom = (value: number) => {
  zoom.value = clampZoom(value)
  constrainPan()
}

const selectImage = (index: number) => {
  currentIndex.value = (index + props.images.length) % props.images.length
  resetTransform()
}

const showPrevious = () => selectImage(currentIndex.value - 1)
const showNext = () => selectImage(currentIndex.value + 1)

const openLightbox = async () => {
  lightboxOpen.value = true
  await nextTick()
  dialog.value?.focus()
}

const closeLightbox = () => {
  lightboxOpen.value = false
  resetTransform()
  nextTick(() => openButton.value?.focus())
}

const handleDialogKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    closeLightbox()
  } else if (event.key === 'ArrowLeft') {
    showPrevious()
  } else if (event.key === 'ArrowRight') {
    showNext()
  } else if (event.key === '+' || event.key === '=') {
    setZoom(zoom.value + 0.25)
  } else if (event.key === '-') {
    setZoom(zoom.value - 0.25)
  } else if (event.key === 'Tab') {
    const focusable = Array.from(
      dialog.value?.querySelectorAll<HTMLElement>('button, [href], [tabindex]:not([tabindex="-1"])') ?? [],
    ).filter((element) => !element.hasAttribute('disabled'))
    const first = focusable[0]
    const last = focusable.at(-1)

    if (event.shiftKey && (document.activeElement === first || document.activeElement === dialog.value)) {
      event.preventDefault()
      last?.focus()
    } else if (!event.shiftKey && (document.activeElement === last || document.activeElement === dialog.value)) {
      event.preventDefault()
      first?.focus()
    }
  }
}

const handleWheel = (event: WheelEvent) => {
  event.preventDefault()
  setZoom(zoom.value + (event.deltaY < 0 ? 0.25 : -0.25))
}

const pointerDistance = () => {
  const [first, second] = [...pointers.values()]
  if (!first || !second) {
    return 0
  }

  return Math.hypot(second.x - first.x, second.y - first.y)
}

const handlePointerDown = (event: PointerEvent) => {
  const target = event.currentTarget as HTMLElement
  target.setPointerCapture(event.pointerId)
  pointers.set(event.pointerId, { x: event.clientX, y: event.clientY })

  if (pointers.size === 2) {
    pinchDistance = pointerDistance()
    pinchZoom = zoom.value
  }
}

const handlePointerMove = (event: PointerEvent) => {
  const previous = pointers.get(event.pointerId)
  if (!previous) {
    return
  }

  pointers.set(event.pointerId, { x: event.clientX, y: event.clientY })

  if (pointers.size === 2 && pinchDistance > 0) {
    zoom.value = clampZoom(pinchZoom * (pointerDistance() / pinchDistance))
    constrainPan()
    return
  }

  if (pointers.size === 1 && zoom.value > 1) {
    panX.value += event.clientX - previous.x
    panY.value += event.clientY - previous.y
    constrainPan()
  }
}

const handlePointerEnd = (event: PointerEvent) => {
  pointers.delete(event.pointerId)
  pinchDistance = 0
  pinchZoom = zoom.value
}

watch(lightboxOpen, (isOpen) => {
  if (isOpen) {
    previousBodyOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    backgroundRoot = document.querySelector<HTMLElement>('.site-shell')
    if (backgroundRoot) {
      backgroundRoot.inert = true
    }
  } else {
    document.body.style.overflow = previousBodyOverflow
    if (backgroundRoot) {
      backgroundRoot.inert = false
      backgroundRoot = null
    }
  }
})

onBeforeUnmount(() => {
  document.body.style.overflow = previousBodyOverflow
  if (backgroundRoot) {
    backgroundRoot.inert = false
  }
})
</script>

<template>
  <section class="gallery" :aria-label="label">
    <div class="gallery-stage">
      <button
        ref="openButton"
        class="gallery-open"
        type="button"
        :aria-label="openLabel"
        @click="openLightbox"
      >
        <img
          :src="images[currentIndex]?.src"
          :alt="images[currentIndex]?.alt"
          draggable="false"
        />
      </button>

      <button class="gallery-arrow gallery-arrow-previous" type="button" :aria-label="previousLabel" @click="showPrevious">
        <span aria-hidden="true">←</span>
      </button>
      <button class="gallery-arrow gallery-arrow-next" type="button" :aria-label="nextLabel" @click="showNext">
        <span aria-hidden="true">→</span>
      </button>
    </div>

    <div class="gallery-meta" aria-live="polite">
      <p>{{ images[currentIndex]?.caption }}</p>
      <span>{{ currentIndex + 1 }} / {{ images.length }}</span>
    </div>

    <Teleport to="body">
      <div
        v-if="lightboxOpen"
        ref="dialog"
        class="gallery-lightbox"
        role="dialog"
        aria-modal="true"
        :aria-label="images[currentIndex]?.caption"
        tabindex="-1"
        @keydown="handleDialogKeydown"
      >
        <div
          class="gallery-lightbox-stage"
          @wheel="handleWheel"
          @pointerdown="handlePointerDown"
          @pointermove="handlePointerMove"
          @pointerup="handlePointerEnd"
          @pointercancel="handlePointerEnd"
          @dblclick="setZoom(zoom === 1 ? 2.5 : 1)"
        >
          <img
            :src="images[currentIndex]?.src"
            :alt="images[currentIndex]?.alt"
            :style="{ transform: `translate3d(${panX}px, ${panY}px, 0) scale(${zoom})` }"
            draggable="false"
          />
        </div>

        <button class="gallery-lightbox-close" type="button" :aria-label="closeLabel" @click="closeLightbox">
          <span aria-hidden="true">×</span>
        </button>

        <div class="gallery-lightbox-toolbar">
          <button type="button" :aria-label="previousLabel" @click="showPrevious">
            <span aria-hidden="true">←</span>
          </button>
          <span class="gallery-lightbox-count" aria-live="polite">
            {{ currentIndex + 1 }} / {{ images.length }}
          </span>
          <button type="button" :aria-label="nextLabel" @click="showNext">
            <span aria-hidden="true">→</span>
          </button>
          <span class="gallery-lightbox-divider" aria-hidden="true" />
          <button type="button" :aria-label="zoomOutLabel" @click="setZoom(zoom - 0.25)">−</button>
          <button class="gallery-lightbox-reset" type="button" :aria-label="resetZoomLabel" @click="resetTransform">
            {{ Math.round(zoom * 100) }}%
          </button>
          <button type="button" :aria-label="zoomInLabel" @click="setZoom(zoom + 0.25)">＋</button>
        </div>
      </div>
    </Teleport>
  </section>
</template>

<style scoped>
.gallery {
  min-width: 0;
}

.gallery-stage {
  position: relative;
  min-height: clamp(390px, 42vw, 560px);
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: clamp(22px, 2vw, 30px);
  background:
    radial-gradient(circle at 50% 42%, var(--gallery-glow), transparent 48%),
    var(--gallery-surface);
}

.gallery-open {
  position: absolute;
  inset: 0;
  display: grid;
  width: 100%;
  height: 100%;
  padding: clamp(26px, 4vw, 60px);
  place-items: center;
  border: 0;
  background: transparent;
  cursor: zoom-in;
}

.gallery-open img {
  display: block;
  width: 100%;
  height: 100%;
  min-width: 0;
  min-height: 0;
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 18px 16px rgb(62 37 55 / 13%));
  transition: transform 280ms cubic-bezier(0.22, 0.72, 0.25, 1);
  user-select: none;
}

.gallery-arrow {
  position: absolute;
  z-index: 2;
  top: 50%;
  display: grid;
  width: 44px;
  height: 44px;
  place-items: center;
  padding: 0;
  border: 1px solid var(--line);
  border-radius: 50%;
  background: var(--header-surface);
  box-shadow: 0 5px 18px var(--control-shadow);
  color: var(--ink);
  cursor: pointer;
  transform: translateY(-50%);
  backdrop-filter: blur(12px);
}

.gallery-arrow-previous {
  left: 18px;
}

.gallery-arrow-next {
  right: 18px;
}

.gallery-meta {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 18px;
  min-height: 30px;
  margin-top: 18px;
  color: var(--ink-soft);
  font-size: 0.78rem;
  letter-spacing: 0.045em;
}

.gallery-meta p {
  margin: 0;
}

.gallery-meta span {
  flex: 0 0 auto;
  font-variant-numeric: tabular-nums;
}

.gallery-lightbox {
  position: fixed;
  z-index: 100;
  inset: 0;
  overflow: hidden;
  background: #111011;
  color: #f7eee7;
  outline: none;
}

.gallery-lightbox-stage {
  position: absolute;
  inset: 0;
  display: grid;
  padding: 64px 24px 94px;
  place-items: center;
  cursor: grab;
  touch-action: none;
}

.gallery-lightbox-stage:active {
  cursor: grabbing;
}

.gallery-lightbox-stage img {
  display: block;
  width: auto;
  height: auto;
  min-width: 0;
  min-height: 0;
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 24px 24px rgb(0 0 0 / 28%));
  transform-origin: center;
  user-select: none;
  will-change: transform;
}

.gallery-lightbox-close {
  position: absolute;
  z-index: 3;
  top: max(18px, env(safe-area-inset-top));
  right: max(18px, env(safe-area-inset-right));
  display: grid;
  width: 46px;
  height: 46px;
  place-items: center;
  padding: 0 0 4px;
  border: 1px solid rgb(255 255 255 / 22%);
  border-radius: 50%;
  background: rgb(44 38 41 / 82%);
  color: inherit;
  cursor: pointer;
  font-size: 1.7rem;
  line-height: 1;
  backdrop-filter: blur(12px);
}

.gallery-lightbox-toolbar {
  position: absolute;
  z-index: 3;
  bottom: max(18px, env(safe-area-inset-bottom));
  left: 50%;
  display: flex;
  overflow: hidden;
  align-items: center;
  border: 1px solid rgb(255 255 255 / 18%);
  border-radius: 999px;
  background: rgb(44 38 41 / 82%);
  transform: translateX(-50%);
  backdrop-filter: blur(12px);
}

.gallery-lightbox-toolbar button {
  min-width: 44px;
  height: 42px;
  padding: 0 12px;
  border: 0;
  border-left: 1px solid rgb(255 255 255 / 15%);
  background: transparent;
  color: inherit;
  cursor: pointer;
  font-size: 0.78rem;
  font-variant-numeric: tabular-nums;
}

.gallery-lightbox-toolbar button:first-child,
.gallery-lightbox-divider + button {
  border-left: 0;
}

.gallery-lightbox-count {
  min-width: 58px;
  padding-inline: 8px;
  color: rgb(255 246 240 / 76%);
  font-size: 0.72rem;
  text-align: center;
  font-variant-numeric: tabular-nums;
}

.gallery-lightbox-divider {
  width: 1px;
  height: 24px;
  margin-inline: 2px;
  background: rgb(255 255 255 / 18%);
}

.gallery-lightbox-reset {
  min-width: 68px !important;
}

@media (hover: hover) and (pointer: fine) {
  .gallery-open:hover img {
    transform: scale(1.018);
  }

  .gallery-arrow:hover,
  .gallery-lightbox-close:hover,
  .gallery-lightbox-toolbar button:hover {
    background: var(--control-active);
    color: var(--ink);
  }
}

@media (min-width: 681px) and (max-width: 1100px) {
  .gallery-stage {
    min-height: clamp(460px, 62vw, 560px);
  }
}

@media (max-width: 680px) {
  .gallery-stage {
    min-height: min(112vw, 480px);
    border-radius: 24px;
  }

  .gallery-open {
    padding: 34px 24px;
  }

  .gallery-arrow {
    top: auto;
    bottom: 12px;
    width: 40px;
    height: 40px;
    transform: none;
  }

  .gallery-arrow-previous {
    left: 12px;
  }

  .gallery-arrow-next {
    right: 12px;
  }

  .gallery-meta {
    margin-top: 14px;
    font-size: 0.72rem;
  }

  .gallery-lightbox-stage {
    padding: 62px 14px 90px;
  }

  .gallery-lightbox-toolbar {
    max-width: calc(100vw - 24px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .gallery-open img {
    transition: none;
  }
}
</style>
