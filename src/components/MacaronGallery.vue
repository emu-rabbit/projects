<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

type GalleryImage = {
  src: string
  alt: string
  caption: string
}

type SwipeTransition = {
  surface: 'gallery' | 'lightbox'
  direction: -1 | 1
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
  loadingLabel: string
  loadErrorLabel: string
}>()

const currentIndex = ref(0)
const lightboxOpen = ref(false)
const isSwitching = ref(false)
const loadFailed = ref(false)
const galleryDragging = ref(false)
const galleryDragOffsetX = ref(0)
const galleryRebasing = ref(false)
const lightboxDragging = ref(false)
const lightboxDragOffsetX = ref(0)
const lightboxRebasing = ref(false)
const swipeAnimating = ref(false)
const zoom = ref(1)
const panX = ref(0)
const panY = ref(0)
const dialog = ref<HTMLElement | null>(null)
const openButton = ref<HTMLButtonElement | null>(null)

const pointers = new Map<number, { x: number; y: number }>()
const readySources = new Set<string>()
const pendingLoads = new Map<string, Promise<void>>()
const swipeThreshold = 52
const swipeAxisBias = 1.2
let pinchDistance = 0
let pinchZoom = 1
let previousBodyOverflow = ''
let backgroundRoot: HTMLElement | null = null
let selectionRequest = 0
let gallerySwipeStart: { pointerId: number; x: number; y: number } | null = null
let lightboxSwipeStart: { pointerId: number; x: number; y: number } | null = null
let suppressNextOpen = false
let lastLightboxSwipeAt = 0

const clampZoom = (value: number) => Math.min(5, Math.max(1, value))

const clearLightboxGesture = () => {
  lightboxSwipeStart = null
  lightboxDragOffsetX.value = 0
  lightboxDragging.value = false
  pointers.clear()
  pinchDistance = 0
  pinchZoom = zoom.value
}

const resetTransform = () => {
  zoom.value = 1
  panX.value = 0
  panY.value = 0
  clearLightboxGesture()
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

const normalizedIndex = (index: number) => (
  (index + props.images.length) % props.images.length
)

const imageAtOffset = (offset: number) => {
  if (props.images.length === 0) {
    return undefined
  }

  return props.images[normalizedIndex(currentIndex.value + offset)]
}

const ensureImageReady = (source: string) => {
  if (readySources.has(source)) {
    return Promise.resolve()
  }

  const pendingLoad = pendingLoads.get(source)
  if (pendingLoad) {
    return pendingLoad
  }

  const request = new Promise<void>((resolve, reject) => {
    const image = new Image()
    image.decoding = 'async'
    image.addEventListener('load', async () => {
      try {
        await image.decode()
      } catch {
        // A completed load is still safe to display when decode() is unsupported.
      }
      readySources.add(source)
      resolve()
    }, { once: true })
    image.addEventListener('error', () => reject(new Error(`Unable to load ${source}`)), { once: true })
    image.src = source
  }).finally(() => pendingLoads.delete(source))

  pendingLoads.set(source, request)
  return request
}

const warmGalleryImages = () => {
  props.images.forEach(({ src }) => {
    void ensureImageReady(src).catch(() => undefined)
  })
}

const markDisplayedImageReady = (event: Event) => {
  const image = event.currentTarget as HTMLImageElement
  readySources.add(image.currentSrc || image.src)
}

const animateSwipeToEnd = async ({ surface, direction }: SwipeTransition) => {
  const width = surface === 'gallery'
    ? openButton.value?.clientWidth ?? window.innerWidth
    : dialog.value?.clientWidth ?? window.innerWidth
  const targetOffset = -direction * width

  if (surface === 'gallery') {
    galleryDragOffsetX.value = targetOffset
  } else {
    lightboxDragOffsetX.value = targetOffset
  }

  await nextTick()
  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    await new Promise<void>((resolve) => window.setTimeout(resolve, surface === 'gallery' ? 280 : 220))
  }
}

const completeSwipeRebase = async (surface: SwipeTransition['surface']) => {
  if (surface === 'gallery') {
    galleryRebasing.value = true
    galleryDragOffsetX.value = 0
  } else {
    lightboxRebasing.value = true
    lightboxDragOffsetX.value = 0
  }

  await nextTick()
  await new Promise<void>((resolve) => {
    requestAnimationFrame(() => requestAnimationFrame(() => resolve()))
  })

  if (surface === 'gallery') {
    galleryRebasing.value = false
  } else {
    lightboxRebasing.value = false
  }
}

const selectImage = async (index: number, swipeTransition?: SwipeTransition) => {
  if (isSwitching.value || swipeAnimating.value || props.images.length === 0) {
    return
  }

  const nextIndex = normalizedIndex(index)
  if (nextIndex === currentIndex.value) {
    return
  }

  const source = props.images[nextIndex]?.src
  if (!source) {
    return
  }

  const request = ++selectionRequest
  isSwitching.value = true
  loadFailed.value = false

  try {
    await ensureImageReady(source)
    if (request !== selectionRequest) {
      return
    }

    if (swipeTransition) {
      isSwitching.value = false
      swipeAnimating.value = true
      await animateSwipeToEnd(swipeTransition)
      if (request !== selectionRequest) {
        return
      }
    }

    currentIndex.value = nextIndex
    resetTransform()
    warmGalleryImages()

    if (swipeTransition) {
      await completeSwipeRebase(swipeTransition.surface)
    }
  } catch {
    if (request === selectionRequest) {
      loadFailed.value = true
      galleryDragOffsetX.value = 0
      lightboxDragOffsetX.value = 0
    }
  } finally {
    if (request === selectionRequest) {
      isSwitching.value = false
      swipeAnimating.value = false
    }
  }
}

const showPrevious = () => selectImage(currentIndex.value - 1)
const showNext = () => selectImage(currentIndex.value + 1)

const swipeDirection = (startX: number, startY: number, endX: number, endY: number): -1 | 0 | 1 => {
  const deltaX = endX - startX
  const deltaY = endY - startY
  if (Math.abs(deltaX) < swipeThreshold || Math.abs(deltaX) < Math.abs(deltaY) * swipeAxisBias) {
    return 0
  }

  return deltaX > 0 ? -1 : 1
}

const handleGalleryPointerDown = (event: PointerEvent) => {
  if (!event.isPrimary || event.button !== 0 || isSwitching.value || swipeAnimating.value) {
    return
  }

  const target = event.currentTarget as HTMLElement
  target.setPointerCapture(event.pointerId)
  gallerySwipeStart = { pointerId: event.pointerId, x: event.clientX, y: event.clientY }
  galleryDragging.value = true
  galleryDragOffsetX.value = 0
  suppressNextOpen = false
}

const handleGalleryPointerMove = (event: PointerEvent) => {
  if (!gallerySwipeStart || gallerySwipeStart.pointerId !== event.pointerId) {
    return
  }

  const deltaX = event.clientX - gallerySwipeStart.x
  const deltaY = event.clientY - gallerySwipeStart.y
  if (Math.abs(deltaX) >= Math.abs(deltaY)) {
    galleryDragOffsetX.value = deltaX
    event.preventDefault()
  }
}

const handleGalleryPointerUp = (event: PointerEvent) => {
  if (!gallerySwipeStart || gallerySwipeStart.pointerId !== event.pointerId) {
    return
  }

  const direction = swipeDirection(
    gallerySwipeStart.x,
    gallerySwipeStart.y,
    event.clientX,
    event.clientY,
  )
  gallerySwipeStart = null
  galleryDragging.value = false

  if (direction === 0) {
    galleryDragOffsetX.value = 0
    return
  }

  suppressNextOpen = true
  event.preventDefault()
  void selectImage(currentIndex.value + direction, { surface: 'gallery', direction })
}

const handleGalleryPointerCancel = () => {
  gallerySwipeStart = null
  galleryDragging.value = false
  galleryDragOffsetX.value = 0
  suppressNextOpen = false
}

const openLightbox = async () => {
  lightboxOpen.value = true
  await nextTick()
  dialog.value?.focus()
}

const handleOpenClick = () => {
  if (suppressNextOpen) {
    suppressNextOpen = false
    return
  }

  void openLightbox()
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
  if (event.button !== 0 || isSwitching.value || swipeAnimating.value) {
    return
  }

  const target = event.target
  if (!(target instanceof Element) || !target.closest('.gallery-lightbox-stage')) {
    return
  }

  if (event.isPrimary) {
    clearLightboxGesture()
  }

  dialog.value?.setPointerCapture(event.pointerId)
  pointers.set(event.pointerId, { x: event.clientX, y: event.clientY })
  lightboxDragging.value = true

  if (pointers.size === 1) {
    lightboxSwipeStart = { pointerId: event.pointerId, x: event.clientX, y: event.clientY }
    lightboxDragOffsetX.value = 0
  }

  if (pointers.size === 2) {
    lightboxSwipeStart = null
    lightboxDragOffsetX.value = 0
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

  if (
    zoom.value === 1
    && lightboxSwipeStart?.pointerId === event.pointerId
  ) {
    lightboxDragOffsetX.value = event.clientX - lightboxSwipeStart.x
    event.preventDefault()
    return
  }

  if (pointers.size === 2 && pinchDistance > 0) {
    lightboxDragOffsetX.value = 0
    zoom.value = clampZoom(pinchZoom * (pointerDistance() / pinchDistance))
    constrainPan()
    return
  }

  if (pointers.size === 1 && zoom.value === 1 && lightboxSwipeStart) {
    lightboxDragOffsetX.value = event.clientX - lightboxSwipeStart.x
    return
  }

  if (pointers.size === 1 && zoom.value > 1) {
    const deltaX = event.clientX - previous.x
    const deltaY = event.clientY - previous.y
    const width = dialog.value?.clientWidth ?? window.innerWidth
    const height = dialog.value?.clientHeight ?? window.innerHeight
    const maximumX = width * (zoom.value - 1) * 0.5
    const maximumY = height * (zoom.value - 1) * 0.5
    panY.value = Math.min(maximumY, Math.max(-maximumY, panY.value + deltaY))

    let remainingX = deltaX
    if (lightboxDragOffsetX.value !== 0) {
      const combinedOffset = lightboxDragOffsetX.value + remainingX
      if (Math.sign(combinedOffset) === Math.sign(lightboxDragOffsetX.value) || combinedOffset === 0) {
        lightboxDragOffsetX.value = combinedOffset
        return
      }

      lightboxDragOffsetX.value = 0
      remainingX = combinedOffset
    }

    const intendedPanX = panX.value + remainingX
    const constrainedPanX = Math.min(maximumX, Math.max(-maximumX, intendedPanX))
    panX.value = constrainedPanX

    const edgeOverflow = intendedPanX - constrainedPanX
    if (Math.abs(deltaX) >= Math.abs(deltaY)) {
      lightboxDragOffsetX.value = edgeOverflow
    }
  }
}

const handlePointerEnd = (event: PointerEvent) => {
  if (!pointers.has(event.pointerId)) {
    return
  }

  let direction: -1 | 0 | 1 = 0
  if (
    lightboxSwipeStart?.pointerId === event.pointerId
  ) {
    if (zoom.value === 1) {
      direction = swipeDirection(
        lightboxSwipeStart.x,
        lightboxSwipeStart.y,
        event.clientX,
        event.clientY,
      )
    } else if (Math.abs(lightboxDragOffsetX.value) >= swipeThreshold) {
      direction = lightboxDragOffsetX.value > 0 ? -1 : 1
    }
  }

  pointers.delete(event.pointerId)
  lightboxSwipeStart = null
  lightboxDragging.value = pointers.size > 0
  pinchDistance = 0
  pinchZoom = zoom.value

  if (direction !== 0 && !isSwitching.value && !swipeAnimating.value) {
    lastLightboxSwipeAt = Date.now()
    event.preventDefault()
    void selectImage(currentIndex.value + direction, { surface: 'lightbox', direction })
  } else {
    lightboxDragOffsetX.value = 0
  }
}

const handlePointerCancel = (event: PointerEvent) => {
  if (!pointers.has(event.pointerId)) {
    return
  }

  pointers.delete(event.pointerId)
  lightboxSwipeStart = null
  lightboxDragOffsetX.value = 0
  lightboxDragging.value = pointers.size > 0
  pinchDistance = 0
  pinchZoom = zoom.value
}

const handleStageDoubleClick = () => {
  if (Date.now() - lastLightboxSwipeAt < 450) {
    return
  }

  setZoom(zoom.value === 1 ? 2.5 : 1)
}

onMounted(warmGalleryImages)

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
  selectionRequest += 1
  document.body.style.overflow = previousBodyOverflow
  if (backgroundRoot) {
    backgroundRoot.inert = false
  }
})
</script>

<template>
  <section class="gallery" :aria-label="label">
    <div class="gallery-stage" :aria-busy="isSwitching">
      <button
        ref="openButton"
        class="gallery-open"
        type="button"
        :aria-label="openLabel"
        :class="{ 'is-dragging': galleryDragging, 'is-rebasing': galleryRebasing }"
        :style="{ '--gallery-drag-x': `${galleryDragOffsetX}px` }"
        @click="handleOpenClick"
        @pointerdown="handleGalleryPointerDown"
        @pointermove="handleGalleryPointerMove"
        @pointerup="handleGalleryPointerUp"
        @pointercancel="handleGalleryPointerCancel"
      >
        <span class="gallery-slide gallery-slide-previous" aria-hidden="true">
          <img :src="imageAtOffset(-1)?.src" alt="" draggable="false" @load="markDisplayedImageReady" />
        </span>
        <span class="gallery-slide gallery-slide-current">
          <img
            :src="imageAtOffset(0)?.src"
            :alt="imageAtOffset(0)?.alt"
            draggable="false"
            @load="markDisplayedImageReady"
          />
        </span>
        <span class="gallery-slide gallery-slide-next" aria-hidden="true">
          <img :src="imageAtOffset(1)?.src" alt="" draggable="false" @load="markDisplayedImageReady" />
        </span>
      </button>

      <button class="gallery-arrow gallery-arrow-previous" type="button" :aria-label="previousLabel" :disabled="isSwitching || swipeAnimating" @click="showPrevious">
        <span aria-hidden="true">←</span>
      </button>
      <button class="gallery-arrow gallery-arrow-next" type="button" :aria-label="nextLabel" :disabled="isSwitching || swipeAnimating" @click="showNext">
        <span aria-hidden="true">→</span>
      </button>

      <span v-if="isSwitching && !lightboxOpen" class="gallery-loading" role="status">
        <span aria-hidden="true" />
        <span class="visually-hidden">{{ loadingLabel }}</span>
      </span>
      <p v-else-if="loadFailed && !lightboxOpen" class="gallery-load-error" role="alert">
        {{ loadErrorLabel }}
      </p>
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
        @pointerdown.capture="handlePointerDown"
        @pointermove.capture="handlePointerMove"
        @pointerup.capture="handlePointerEnd"
        @pointercancel.capture="handlePointerCancel"
        @dragstart.capture.prevent
      >
        <div
          class="gallery-lightbox-stage"
          :class="{ 'is-dragging': lightboxDragging, 'is-rebasing': lightboxRebasing }"
          :style="{ '--lightbox-drag-x': `${lightboxDragOffsetX}px` }"
          :aria-busy="isSwitching"
          @wheel="handleWheel"
          @dblclick="handleStageDoubleClick"
        >
          <div class="gallery-lightbox-slide gallery-lightbox-slide-previous" aria-hidden="true">
            <img :src="imageAtOffset(-1)?.src" alt="" draggable="false" @load="markDisplayedImageReady" />
          </div>
          <div class="gallery-lightbox-slide gallery-lightbox-slide-current">
            <img
              :src="imageAtOffset(0)?.src"
              :alt="imageAtOffset(0)?.alt"
              :style="{ transform: `translate3d(${panX}px, ${panY}px, 0) scale(${zoom})` }"
              draggable="false"
              @load="markDisplayedImageReady"
            />
          </div>
          <div class="gallery-lightbox-slide gallery-lightbox-slide-next" aria-hidden="true">
            <img :src="imageAtOffset(1)?.src" alt="" draggable="false" @load="markDisplayedImageReady" />
          </div>
          <span v-if="isSwitching" class="gallery-loading gallery-lightbox-loading" role="status">
            <span aria-hidden="true" />
            <span class="visually-hidden">{{ loadingLabel }}</span>
          </span>
          <p v-else-if="loadFailed" class="gallery-load-error gallery-lightbox-load-error" role="alert">
            {{ loadErrorLabel }}
          </p>
        </div>

        <button class="gallery-lightbox-close" type="button" :aria-label="closeLabel" @click="closeLightbox">
          <span aria-hidden="true">×</span>
        </button>

        <div class="gallery-lightbox-toolbar">
          <button type="button" :aria-label="previousLabel" :disabled="isSwitching || swipeAnimating" @click="showPrevious">
            <span aria-hidden="true">←</span>
          </button>
          <span class="gallery-lightbox-count" aria-live="polite">
            {{ currentIndex + 1 }} / {{ images.length }}
          </span>
          <button type="button" :aria-label="nextLabel" :disabled="isSwitching || swipeAnimating" @click="showNext">
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
    radial-gradient(circle at 50% 43%, var(--gallery-card-glow, var(--gallery-glow)) 0 8%, transparent 58%),
    var(--gallery-card-background, var(--gallery-surface));
}

.gallery-open {
  position: absolute;
  inset: 0;
  display: grid;
  width: 100%;
  height: 100%;
  padding: 0;
  border: 0;
  background: transparent;
  cursor: grab;
  touch-action: pan-y;
}

.gallery-open:active {
  cursor: grabbing;
}

.gallery-slide {
  position: absolute;
  inset: 0;
  display: grid;
  padding: clamp(26px, 4vw, 60px);
  place-items: center;
  pointer-events: none;
  transition: transform 280ms cubic-bezier(0.22, 0.72, 0.25, 1);
  will-change: transform;
}

.gallery-slide-previous {
  transform: translate3d(calc(-100% + var(--gallery-drag-x, 0px)), 0, 0);
}

.gallery-slide-current {
  transform: translate3d(var(--gallery-drag-x, 0px), 0, 0);
}

.gallery-slide-next {
  transform: translate3d(calc(100% + var(--gallery-drag-x, 0px)), 0, 0);
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

.gallery-open.is-dragging .gallery-slide,
.gallery-open.is-rebasing .gallery-slide {
  transition: none;
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

.gallery-arrow:disabled,
.gallery-lightbox-toolbar button:disabled {
  cursor: wait;
  opacity: 0.48;
}

.gallery-loading,
.gallery-load-error {
  position: absolute;
  z-index: 4;
  top: 50%;
  left: 50%;
  pointer-events: none;
  transform: translate(-50%, -50%);
}

.gallery-loading {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border: 1px solid var(--line);
  border-radius: 50%;
  background: var(--header-surface);
  box-shadow: 0 5px 18px var(--control-shadow);
  backdrop-filter: blur(12px);
}

.gallery-loading > [aria-hidden="true"] {
  width: 17px;
  height: 17px;
  border: 2px solid color-mix(in srgb, var(--ink-soft) 34%, transparent);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: gallery-loading-spin 720ms linear infinite;
}

.gallery-load-error {
  width: max-content;
  max-width: calc(100% - 48px);
  margin: 0;
  padding: 9px 13px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--header-surface);
  box-shadow: 0 5px 18px var(--control-shadow);
  color: var(--ink);
  font-size: 0.72rem;
  text-align: center;
  backdrop-filter: blur(12px);
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
  user-select: none;
  -webkit-user-select: none;
}

.gallery-lightbox-stage {
  position: absolute;
  inset: 0;
  overflow: hidden;
  cursor: grab;
  touch-action: none;
}

.gallery-lightbox-stage:active {
  cursor: grabbing;
}

.gallery-lightbox-slide {
  position: absolute;
  inset: 0;
  display: grid;
  padding: 64px 24px 94px;
  place-items: center;
  pointer-events: none;
  transition: transform 220ms cubic-bezier(0.22, 0.72, 0.25, 1);
  will-change: transform;
}

.gallery-lightbox-slide-previous {
  transform: translate3d(calc(-100% + var(--lightbox-drag-x, 0px)), 0, 0);
}

.gallery-lightbox-slide-current {
  transform: translate3d(var(--lightbox-drag-x, 0px), 0, 0);
}

.gallery-lightbox-slide-next {
  transform: translate3d(calc(100% + var(--lightbox-drag-x, 0px)), 0, 0);
}

.gallery-lightbox-slide img {
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
  transition: transform 220ms cubic-bezier(0.22, 0.72, 0.25, 1);
  user-select: none;
  -webkit-user-drag: none;
  will-change: transform;
}

.gallery-lightbox-stage.is-dragging img {
  transition: none;
}

.gallery-lightbox-stage.is-dragging .gallery-lightbox-slide,
.gallery-lightbox-stage.is-rebasing .gallery-lightbox-slide {
  transition: none;
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

.gallery-lightbox-loading,
.gallery-lightbox-load-error {
  color: #f7eee7;
  background: rgb(44 38 41 / 82%);
  border-color: rgb(255 255 255 / 18%);
}

@keyframes gallery-loading-spin {
  to {
    transform: rotate(1turn);
  }
}

@media (hover: hover) and (pointer: fine) {
  .gallery-open:not(.is-dragging):hover .gallery-slide-current img {
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

  .gallery-slide {
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

  .gallery-lightbox-slide {
    padding: 62px 14px 90px;
  }

  .gallery-lightbox-toolbar {
    max-width: calc(100vw - 24px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .gallery-slide,
  .gallery-open img,
  .gallery-lightbox-slide,
  .gallery-lightbox-slide img {
    transition: none;
  }

  .gallery-loading > [aria-hidden="true"] {
    animation-duration: 1.4s;
  }
}
</style>
