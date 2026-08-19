<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'

const props = defineProps<{
  accessibleLabel: string
  fallbackAlt: string
  fallbackImage: string
  interactionHint: string
  loadingLabel: string
  loadError: string
  diagnosticLabel: string
  modelUrl: string
  resetLabel: string
  theme: 'light' | 'dark'
}>()

type ViewerFailureCode =
  | 'VIEWER_INITIALIZATION_FAILED'
  | 'VIEWER_RENDER_FAILED'
  | 'WEBGL_CONTEXT_CREATION_FAILED'
  | 'WEBGL_CONTEXT_LOST'
  | 'MODEL_DOWNLOAD_FAILED'
  | 'MODEL_RESOURCE_FAILED'
  | 'MODEL_PARSE_FAILED'
  | 'MODEL_PREPARATION_FAILED'

interface ViewerFailure {
  code: ViewerFailureCode
  detail: string
}

type ModelLoadStage = 'download' | 'parse' | 'prepare'

const canvas = ref<HTMLCanvasElement | null>(null)
const viewer = ref<HTMLElement | null>(null)
const modelReady = ref(false)
const modelFailed = ref(false)
const loadProgress = ref(0)
const viewerFailure = ref<ViewerFailure | null>(null)

let renderer: THREE.WebGLRenderer | null = null
let scene: THREE.Scene | null = null
let camera: THREE.OrthographicCamera | null = null
let controls: OrbitControls | null = null
let model: THREE.Group | null = null
let ground: THREE.Mesh | null = null
let environmentRenderTarget: THREE.WebGLRenderTarget | null = null
let resizeObserver: ResizeObserver | null = null
let animationFrame = 0
let resizeFrame = 0
let renderQueued = false
let isVisible = true
let disposed = false
let contextCreationError = ''
let useMobileRendererBudget = false
let useModelShadows = true

const describeError = (error: unknown) => {
  if (error instanceof ProgressEvent && error.target instanceof XMLHttpRequest) {
    const request = error.target
    const status = request.status ? `HTTP ${request.status}` : 'Network request failed'
    return [status, request.statusText].filter(Boolean).join(' · ')
  }

  if (error instanceof Error) return `${error.name}: ${error.message}`
  if (typeof error === 'string') return error

  try {
    return JSON.stringify(error) || String(error)
  } catch {
    return String(error)
  }
}

const reportFailure = (code: ViewerFailureCode, detail: string, error?: unknown) => {
  if (disposed) return
  if (viewerFailure.value?.code === 'WEBGL_CONTEXT_LOST') return

  renderQueued = false
  modelReady.value = false
  modelFailed.value = true
  viewerFailure.value = { code, detail }
  console.error('[3D macaron viewer]', {
    code,
    detail,
    progress: Math.round(loadProgress.value * 100),
    error,
  })
}

const handleContextCreationError = (event: Event) => {
  const statusMessage = (event as WebGLContextEvent).statusMessage
  contextCreationError = statusMessage || 'The browser rejected the WebGL context.'
}

const handleContextLost = (event: Event) => {
  window.cancelAnimationFrame(animationFrame)
  renderQueued = false
  const statusMessage = (event as WebGLContextEvent).statusMessage
  reportFailure(
    'WEBGL_CONTEXT_LOST',
    statusMessage || 'The browser reported that the WebGL context was lost.',
    event,
  )
}

const handleVisibilityChange = () => {
  isVisible = document.visibilityState === 'visible'
  if (!isVisible) {
    window.cancelAnimationFrame(animationFrame)
    renderQueued = false
    return
  }
  requestRender()
}

const disposeMaterial = (material: THREE.Material) => {
  Object.values(material).forEach((value) => {
    if (value instanceof THREE.Texture) value.dispose()
  })
  material.dispose()
}

const disposeModel = (group: THREE.Group) => {
  group.traverse((object) => {
    if (!(object instanceof THREE.Mesh)) return
    object.geometry.dispose()
    if (Array.isArray(object.material)) object.material.forEach(disposeMaterial)
    else disposeMaterial(object.material)
  })
}

const updateLightingForTheme = () => {
  if (!scene) return

  const isDark = props.theme === 'dark'
  const hemisphere = scene.getObjectByName('hemisphere-light') as THREE.HemisphereLight | undefined
  const ambient = scene.getObjectByName('ambient-light') as THREE.AmbientLight | undefined
  const key = scene.getObjectByName('key-light') as THREE.DirectionalLight | undefined
  const fill = scene.getObjectByName('fill-light') as THREE.DirectionalLight | undefined
  const shadowMaterial = ground?.material as THREE.ShadowMaterial | undefined

  scene.environmentIntensity = isDark ? 0.38 : 0.5
  if (renderer) renderer.toneMappingExposure = isDark ? 0.86 : 0.98
  if (hemisphere) {
    hemisphere.color.set(isDark ? '#d8d0f0' : '#fff8ee')
    hemisphere.groundColor.set(isDark ? '#382c45' : '#755268')
    hemisphere.intensity = isDark ? 0.2 : 0.25
  }
  if (ambient) {
    ambient.color.set(isDark ? '#aaa3c7' : '#fff7ef')
    ambient.intensity = isDark ? 0.045 : 0.065
  }
  if (key) {
    key.color.set(isDark ? '#d7d0f3' : '#ffe8cf')
    key.intensity = isDark ? 0.46 : 0.62
  }
  if (fill) {
    fill.color.set(isDark ? '#8f86bd' : '#eadcf2')
    fill.intensity = isDark ? 0.09 : 0.1
  }
  if (shadowMaterial) {
    shadowMaterial.color.set(isDark ? '#160f1d' : '#3f273c')
    shadowMaterial.opacity = isDark ? 0.18 : 0.1
  }
  requestRender()
}

const resize = () => {
  if (!viewer.value || !renderer || !camera) return

  const { width, height } = viewer.value.getBoundingClientRect()
  if (!width || !height) return

  renderer.setSize(width, height, false)
  const aspect = width / height
  const halfHeight = Math.max(2.45, 2.18 / aspect)
  camera.left = -halfHeight * aspect
  camera.right = halfHeight * aspect
  camera.top = halfHeight
  camera.bottom = -halfHeight
  camera.updateProjectionMatrix()
  requestRender()
}

const scheduleResize = () => {
  window.cancelAnimationFrame(resizeFrame)
  resizeFrame = window.requestAnimationFrame(resize)
}

const render = () => {
  renderQueued = false
  if (modelFailed.value) return
  if (!renderer || !scene || !camera || !controls || !isVisible) return

  try {
    controls.update()
    renderer.render(scene, camera)
  } catch (error) {
    window.cancelAnimationFrame(animationFrame)
    renderQueued = false
    reportFailure('VIEWER_RENDER_FAILED', describeError(error), error)
  }
}

const requestRender = () => {
  if (renderQueued || disposed || modelFailed.value || !isVisible) return
  renderQueued = true
  animationFrame = window.requestAnimationFrame(render)
}

const resetView = () => {
  if (!controls || !model) return
  controls.reset()
  model.rotation.y = 0
  controls.update()
  requestRender()
}

const loadModel = async () => {
  if (!scene || !renderer || modelFailed.value) return

  const loadState: { stage: ModelLoadStage } = { stage: 'download' }
  let failedResourceUrl = ''
  const loadingManager = new THREE.LoadingManager()
  loadingManager.onError = (url) => {
    failedResourceUrl = url
  }

  try {
    const gltf = await new GLTFLoader(loadingManager).loadAsync(props.modelUrl, (event) => {
      if (event.total <= 0) return

      loadProgress.value = Math.min(1, event.loaded / event.total)
      if (event.loaded >= event.total) loadState.stage = 'parse'
    })

    loadState.stage = 'prepare'

    if (disposed || modelFailed.value || !scene) {
      disposeModel(gltf.scene)
      return
    }

    model = gltf.scene
    model.name = 'window-notes-macaron'
    const maxAnisotropy = renderer.capabilities.getMaxAnisotropy()

    model.traverse((object) => {
      if (!(object instanceof THREE.Mesh)) return
      object.castShadow = useModelShadows
      object.receiveShadow = useModelShadows
      const materials = Array.isArray(object.material) ? object.material : [object.material]
      materials.forEach((material) => {
        const standardMaterial = material as THREE.MeshStandardMaterial
        if (standardMaterial.map) standardMaterial.map.anisotropy = Math.min(8, maxAnisotropy)
        if (
          useMobileRendererBudget &&
          material instanceof THREE.MeshPhysicalMaterial &&
          material.transmission > 0
        ) {
          material.transmission = 0
          material.needsUpdate = true
        }
      })
    })

    const bounds = new THREE.Box3().setFromObject(model)
    model.position.sub(bounds.getCenter(new THREE.Vector3()))
    model.rotation.y = 0
    scene.add(model)

    if (useModelShadows) {
      const keyLight = scene.getObjectByName('key-light') as THREE.DirectionalLight | undefined
      if (keyLight) keyLight.shadow.needsUpdate = true
    }

    if (ground) ground.position.y = new THREE.Box3().setFromObject(model).min.y - 0.08

    loadProgress.value = 1
    modelReady.value = true
    requestRender()
  } catch (error) {
    const detail = describeError(error)

    if (failedResourceUrl && failedResourceUrl !== props.modelUrl) {
      const resource = failedResourceUrl.startsWith('blob:')
        ? 'An embedded model texture failed to decode.'
        : `Resource failed: ${failedResourceUrl}`
      reportFailure('MODEL_RESOURCE_FAILED', `${resource} ${detail}`.trim(), error)
      return
    }

    const code: ViewerFailureCode =
      loadState.stage === 'download'
        ? 'MODEL_DOWNLOAD_FAILED'
        : loadState.stage === 'parse'
          ? 'MODEL_PARSE_FAILED'
          : 'MODEL_PREPARATION_FAILED'
    reportFailure(code, detail, error)
  }
}

onMounted(() => {
  if (!canvas.value || !viewer.value) return

  useMobileRendererBudget =
    window.matchMedia('(max-width: 680px)').matches ||
    window.matchMedia('(pointer: coarse)').matches
  useModelShadows = !useMobileRendererBudget

  canvas.value.addEventListener('webglcontextcreationerror', handleContextCreationError)
  canvas.value.addEventListener('webglcontextlost', handleContextLost)

  try {
    renderer = new THREE.WebGLRenderer({
      canvas: canvas.value,
      alpha: true,
      antialias: !useMobileRendererBudget,
      powerPreference: useMobileRendererBudget ? 'default' : 'high-performance',
    })
  } catch (error) {
    reportFailure(
      'WEBGL_CONTEXT_CREATION_FAILED',
      contextCreationError || describeError(error),
      error,
    )
    return
  }

  try {
    renderer.setPixelRatio(
      useMobileRendererBudget ? 1 : Math.min(window.devicePixelRatio, 1.75),
    )
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.shadowMap.enabled = useModelShadows
    renderer.shadowMap.type = THREE.PCFShadowMap

    scene = new THREE.Scene()
    camera = new THREE.OrthographicCamera(-2.5, 2.5, 2.5, -2.5, 0.1, 100)
    camera.position.set(5.8, 4.2, 3.35)

    const pmremGenerator = new THREE.PMREMGenerator(renderer)
    const roomEnvironment = new RoomEnvironment()
    environmentRenderTarget = pmremGenerator.fromScene(roomEnvironment, 0.035)
    scene.environment = environmentRenderTarget.texture
    roomEnvironment.dispose()
    pmremGenerator.dispose()

    const hemisphere = new THREE.HemisphereLight('#fff8ee', '#755268', 0.25)
    hemisphere.name = 'hemisphere-light'
    scene.add(hemisphere)

    const ambientLight = new THREE.AmbientLight('#fff7ef', 0.065)
    ambientLight.name = 'ambient-light'
    scene.add(ambientLight)

    const keyLight = new THREE.DirectionalLight('#ffe8cf', 0.62)
    keyLight.name = 'key-light'
    keyLight.position.set(4.2, 7.5, 5.6)
    keyLight.castShadow = useModelShadows
    keyLight.shadow.autoUpdate = false
    if (useModelShadows) keyLight.shadow.mapSize.set(1024, 1024)
    keyLight.shadow.camera.near = 0.1
    keyLight.shadow.camera.far = 18
    keyLight.shadow.camera.left = -5
    keyLight.shadow.camera.right = 5
    keyLight.shadow.camera.top = 5
    keyLight.shadow.camera.bottom = -5
    keyLight.shadow.bias = -0.00015
    keyLight.shadow.normalBias = 0.045
    scene.add(keyLight)

    const fillLight = new THREE.DirectionalLight('#eadcf2', 0.1)
    fillLight.name = 'fill-light'
    fillLight.position.set(-5, 3.5, -2.5)
    scene.add(fillLight)

    const shadowMaterial = new THREE.ShadowMaterial({ color: '#3f273c', opacity: 0.1 })
    ground = new THREE.Mesh(new THREE.PlaneGeometry(12, 12), shadowMaterial)
    ground.name = 'ground-shadow'
    ground.position.y = -1.65
    ground.rotation.x = -Math.PI / 2
    ground.receiveShadow = useModelShadows
    ground.visible = useModelShadows
    scene.add(ground)

    controls = new OrbitControls(camera, canvas.value)
    controls.target.set(0, 0.04, 0)
    controls.enableDamping = true
    controls.dampingFactor = 0.065
    controls.enablePan = false
    controls.minZoom = 0.72
    controls.maxZoom = 1.9
    controls.minPolarAngle = Math.PI * 0.16
    controls.maxPolarAngle = Math.PI * 0.78
    controls.saveState()
    controls.addEventListener('change', requestRender)

    updateLightingForTheme()
    resizeObserver = new ResizeObserver(scheduleResize)
    resizeObserver.observe(viewer.value)
    document.addEventListener('visibilitychange', handleVisibilityChange)
    resize()
    controls.update()
    void loadModel()
  } catch (error) {
    reportFailure('VIEWER_INITIALIZATION_FAILED', describeError(error), error)
  }
})

onBeforeUnmount(() => {
  disposed = true
  window.cancelAnimationFrame(animationFrame)
  window.cancelAnimationFrame(resizeFrame)
  resizeObserver?.disconnect()
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  canvas.value?.removeEventListener('webglcontextcreationerror', handleContextCreationError)
  canvas.value?.removeEventListener('webglcontextlost', handleContextLost)
  controls?.removeEventListener('change', requestRender)
  controls?.dispose()
  if (model) disposeModel(model)
  ground?.geometry.dispose()
  if (ground) disposeMaterial(ground.material as THREE.Material)
  environmentRenderTarget?.dispose()
  renderer?.dispose()
  renderer?.forceContextLoss()
})

watch(() => props.theme, updateLightingForTheme)
</script>

<template>
  <div
    ref="viewer"
    class="model-viewer"
    :class="{ 'is-ready': modelReady }"
    :aria-busy="!modelReady && !modelFailed"
  >
    <canvas
      v-show="!modelFailed"
      ref="canvas"
      class="model-viewer-canvas"
      :aria-label="accessibleLabel"
      tabindex="0"
    />

    <div v-if="!modelReady" class="model-viewer-fallback">
      <img :src="fallbackImage" :alt="fallbackAlt" />
      <div v-if="modelFailed" class="model-viewer-error" role="alert">
        <p>{{ loadError }}</p>
        <p v-if="viewerFailure" class="model-viewer-diagnostic-code">
          {{ diagnosticLabel }}：<code>{{ viewerFailure.code }}</code>
        </p>
        <p v-if="viewerFailure?.detail" class="model-viewer-diagnostic-detail">
          {{ viewerFailure.detail }}
        </p>
      </div>
      <div v-else class="model-viewer-loading" role="status">
        <span>{{ loadingLabel }}</span>
        <span
          class="model-viewer-progress"
          :style="{ '--load-progress': `${loadProgress * 100}%` }"
          aria-hidden="true"
        />
      </div>
    </div>

    <div v-if="modelReady" class="model-viewer-toolbar">
      <p>{{ interactionHint }}</p>
      <button type="button" :aria-label="resetLabel" :title="resetLabel" @click="resetView">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M20 11a8 8 0 1 0-2.34 5.66M20 5v6h-6" />
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.model-viewer {
  position: relative;
  min-height: clamp(420px, 58vw, 690px);
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 30px;
  background:
    radial-gradient(circle at 50% 38%, var(--gallery-glow), transparent 46%),
    var(--gallery-surface);
  box-shadow: 0 20px 56px var(--card-shadow);
}

.model-viewer-canvas {
  position: absolute;
  inset: 0;
  display: block;
  width: 100%;
  height: 100%;
  cursor: grab;
  opacity: 0;
  touch-action: none;
  transition: opacity 320ms ease;
}

.model-viewer.is-ready .model-viewer-canvas {
  opacity: 1;
}

.model-viewer-canvas:active {
  cursor: grabbing;
}

.model-viewer-fallback {
  position: absolute;
  z-index: 2;
  inset: 0;
  display: grid;
  place-items: center;
  padding: clamp(30px, 6vw, 76px);
  background:
    radial-gradient(circle at 50% 38%, var(--gallery-glow), transparent 46%),
    var(--gallery-surface);
}

.model-viewer-fallback img {
  display: block;
  width: min(80%, 580px);
  height: auto;
  filter: drop-shadow(0 16px 14px rgb(62 37 55 / 14%));
}

.model-viewer-loading {
  position: absolute;
  right: clamp(20px, 4vw, 48px);
  bottom: clamp(20px, 4vw, 42px);
  left: clamp(20px, 4vw, 48px);
  color: var(--ink-soft);
  font-size: 0.75rem;
  letter-spacing: 0.05em;
}

.model-viewer-progress {
  display: block;
  height: 3px;
  margin-top: 10px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--line);
}

.model-viewer-progress::after {
  display: block;
  width: var(--load-progress);
  height: 100%;
  border-radius: inherit;
  background: var(--accent);
  content: '';
  transition: width 140ms ease;
}

.model-viewer-error {
  position: absolute;
  right: 24px;
  bottom: 28px;
  left: 24px;
  display: grid;
  max-height: 42%;
  gap: 7px;
  overflow: auto;
  color: var(--ink-soft);
  text-align: center;
}

.model-viewer-error p {
  margin: 0;
}

.model-viewer-diagnostic-code,
.model-viewer-diagnostic-detail {
  font-size: 0.68rem;
  line-height: 1.5;
}

.model-viewer-diagnostic-code code {
  color: var(--ink);
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  font-weight: 700;
  overflow-wrap: anywhere;
}

.model-viewer-diagnostic-detail {
  opacity: 0.82;
  overflow-wrap: anywhere;
}

.model-viewer-toolbar {
  position: absolute;
  z-index: 3;
  right: clamp(14px, 2vw, 22px);
  bottom: clamp(14px, 2vw, 22px);
  left: clamp(14px, 2vw, 22px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  pointer-events: none;
}

.model-viewer-toolbar p {
  margin: 0;
  padding: 8px 12px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--header-surface);
  box-shadow: 0 4px 16px var(--control-shadow);
  color: var(--ink-soft);
  font-size: 0.68rem;
  letter-spacing: 0.045em;
  backdrop-filter: blur(12px);
}

.model-viewer-toolbar button {
  display: grid;
  width: 42px;
  height: 42px;
  flex: 0 0 auto;
  place-items: center;
  padding: 0;
  border: 1px solid var(--line);
  border-radius: 50%;
  background: var(--header-surface);
  box-shadow: 0 4px 16px var(--control-shadow);
  color: var(--ink);
  cursor: pointer;
  pointer-events: auto;
  backdrop-filter: blur(12px);
}

.model-viewer-toolbar svg {
  width: 19px;
  height: 19px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.7;
}

@media (max-width: 680px) {
  .model-viewer {
    min-height: min(116vw, 560px);
    border-radius: 24px;
  }

  .model-viewer-toolbar p {
    font-size: 0.62rem;
  }
}
</style>
