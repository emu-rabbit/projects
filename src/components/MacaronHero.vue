<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { boxMacarons } from '../data/portfolio'

defineProps<{
  collectionLabel: string
}>()

const emit = defineEmits<{
  select: [targetId: string]
}>()

const macaronBoxImage = new URL('../../assets/hero/macaron-box-empty.webp', import.meta.url).href
const macaronScene = ref<HTMLElement | null>(null)

let macaronElements: HTMLElement[] = []
let motionFrame = 0
let lastScrollY = 0
let lastWheelTime = 0
let waveStartTime = 0
let waveDirection = 1
let waveLocked = false
let waveUnlockTimer = 0
let lastTouchY: number | null = null
let reducedMotionQuery: MediaQueryList | null = null

const waveLift = 12
const waveLiftDuration = 320
const waveColumnDelay = 70
const waveRowDelay = 35
const waveDuration = waveLiftDuration + waveColumnDelay * 4 + waveRowDelay
const waveCooldown = 500

const clearMotion = () => {
  if (motionFrame) {
    window.cancelAnimationFrame(motionFrame)
    motionFrame = 0
  }

  waveStartTime = 0
  macaronElements.forEach((element) => element.style.removeProperty('--scroll-lift'))
}

const unlockWave = () => {
  if (waveUnlockTimer) {
    window.clearTimeout(waveUnlockTimer)
    waveUnlockTimer = 0
  }

  waveLocked = false
}

const finishWave = () => {
  clearMotion()
  waveUnlockTimer = window.setTimeout(unlockWave, waveCooldown)
}

const animateWave = (time: number) => {
  if (!waveStartTime) {
    waveStartTime = time
  }

  const elapsed = time - waveStartTime

  macaronElements.forEach((element, index) => {
    const column = index % 5
    const row = Math.floor(index / 5)
    const orderedColumn = waveDirection > 0 ? column : 4 - column
    const delay = orderedColumn * waveColumnDelay + row * waveRowDelay
    const progress = (elapsed - delay) / waveLiftDuration
    const lift = progress >= 0 && progress <= 1 ? -Math.sin(Math.PI * progress) * waveLift : 0
    element.style.setProperty('--scroll-lift', `${lift.toFixed(2)}px`)
  })

  if (elapsed < waveDuration) {
    motionFrame = window.requestAnimationFrame(animateWave)
    return
  }

  finishWave()
}

const addWaveImpulse = (delta: number) => {
  if (!delta || waveLocked || reducedMotionQuery?.matches) {
    return
  }

  waveLocked = true
  waveDirection = delta > 0 ? 1 : -1
  motionFrame = window.requestAnimationFrame(animateWave)
}

const handleMotionPreferenceChange = () => {
  clearMotion()
  unlockWave()
}

const handleWheel = (event: WheelEvent) => {
  lastWheelTime = window.performance.now()
  addWaveImpulse(event.deltaY)
}

const handleScroll = () => {
  const nextScrollY = window.scrollY
  const delta = nextScrollY - lastScrollY
  lastScrollY = nextScrollY

  if (window.performance.now() - lastWheelTime > 80) {
    addWaveImpulse(delta)
  }
}

const handleTouchStart = (event: TouchEvent) => {
  lastTouchY = event.touches[0]?.clientY ?? null
}

const handleTouchMove = (event: TouchEvent) => {
  const nextTouchY = event.touches[0]?.clientY

  if (nextTouchY === undefined || lastTouchY === null) {
    return
  }

  addWaveImpulse(lastTouchY - nextTouchY)
  lastTouchY = nextTouchY
}

const handleTouchEnd = () => {
  lastTouchY = null
}

onMounted(() => {
  macaronElements = Array.from(macaronScene.value?.querySelectorAll<HTMLElement>('.macaron') ?? [])
  lastScrollY = window.scrollY
  reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  reducedMotionQuery.addEventListener('change', handleMotionPreferenceChange)
  window.addEventListener('wheel', handleWheel, { passive: true })
  window.addEventListener('scroll', handleScroll, { passive: true })
  window.addEventListener('touchstart', handleTouchStart, { passive: true })
  window.addEventListener('touchmove', handleTouchMove, { passive: true })
  window.addEventListener('touchend', handleTouchEnd, { passive: true })
  window.addEventListener('touchcancel', handleTouchEnd, { passive: true })
})

onBeforeUnmount(() => {
  clearMotion()
  unlockWave()
  reducedMotionQuery?.removeEventListener('change', handleMotionPreferenceChange)
  window.removeEventListener('wheel', handleWheel)
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('touchstart', handleTouchStart)
  window.removeEventListener('touchmove', handleTouchMove)
  window.removeEventListener('touchend', handleTouchEnd)
  window.removeEventListener('touchcancel', handleTouchEnd)
})
</script>

<template>
  <div ref="macaronScene" class="macaron-scene" role="group" :aria-label="collectionLabel">
    <img class="macaron-box-layer macaron-box-back" :src="macaronBoxImage" alt="" draggable="false" />

    <button
      v-for="macaron in boxMacarons"
      :key="macaron.name"
      class="macaron"
      :class="`macaron-row-${macaron.row}`"
      :style="{ left: macaron.left, top: macaron.top }"
      type="button"
      :aria-label="macaron.name"
      @click="emit('select', macaron.targetId)"
    >
      <img class="macaron-art" :src="macaron.src" alt="" draggable="false" />
    </button>

    <img class="macaron-box-layer macaron-box-front" :src="macaronBoxImage" alt="" draggable="false" />
  </div>
</template>
