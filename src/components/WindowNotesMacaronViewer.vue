<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
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
  diagnosticReportLabel: string
  copyDiagnosticLabel: string
  diagnosticCopiedLabel: string
  diagnosticCopyFailedLabel: string
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
type DiagnosticCopyState = 'idle' | 'copied' | 'failed'

interface DiagnosticEvent {
  elapsedMs: number
  stage: string
  details?: Record<string, unknown>
}

interface NavigatorConnection {
  effectiveType?: string
  downlink?: number
  rtt?: number
  saveData?: boolean
}

const canvas = ref<HTMLCanvasElement | null>(null)
const viewer = ref<HTMLElement | null>(null)
const modelReady = ref(false)
const modelFailed = ref(false)
const loadProgress = ref(0)
const viewerFailure = ref<ViewerFailure | null>(null)
const diagnosticEvents = ref<DiagnosticEvent[]>([])
const diagnosticEnvironment = ref<Record<string, unknown>>({})
const diagnosticWebgl = ref<Record<string, unknown>>({})
const diagnosticModel = ref<Record<string, unknown>>({})
const diagnosticCopyState = ref<DiagnosticCopyState>('idle')

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
let isVisible = true
let disposed = false
let contextCreationError = ''
let useMobileRendererBudget = false
let useRealtimeShadows = true
let currentDiagnosticStage = 'component-created'
let firstFrameRendered = false
let lastProgressBucket = -1
let lastCanvasSize = ''
const diagnosticStartedAt = performance.now()

const recordDiagnosticEvent = (stage: string, details?: Record<string, unknown>) => {
  currentDiagnosticStage = stage
  const entry: DiagnosticEvent = {
    elapsedMs: Math.round(performance.now() - diagnosticStartedAt),
    stage,
    ...(details ? { details } : {}),
  }
  diagnosticEvents.value = [...diagnosticEvents.value, entry]
  console.info('[3D macaron viewer diagnostic]', entry)
}

const diagnosticReport = computed(() => JSON.stringify({
  reportVersion: 'macaron-viewer-diagnostic-v1',
  generatedAt: new Date().toISOString(),
  page: `${window.location.origin}${window.location.pathname}`,
  failure: viewerFailure.value,
  state: {
    stage: currentDiagnosticStage,
    progressPercent: Math.round(loadProgress.value * 100),
    modelReady: modelReady.value,
    modelFailed: modelFailed.value,
  },
  environment: diagnosticEnvironment.value,
  webgl: diagnosticWebgl.value,
  model: diagnosticModel.value,
  events: diagnosticEvents.value,
}, null, 2))

const diagnosticCopyButtonLabel = computed(() => {
  if (diagnosticCopyState.value === 'copied') return props.diagnosticCopiedLabel
  if (diagnosticCopyState.value === 'failed') return props.diagnosticCopyFailedLabel
  return props.copyDiagnosticLabel
})

const copyDiagnosticReport = async () => {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(diagnosticReport.value)
    } else {
      const textarea = document.createElement('textarea')
      textarea.value = diagnosticReport.value
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      const copied = document.execCommand('copy')
      textarea.remove()
      if (!copied) throw new Error('document.execCommand returned false')
    }
    diagnosticCopyState.value = 'copied'
  } catch (error) {
    diagnosticCopyState.value = 'failed'
    console.error('[3D macaron viewer diagnostic] Copy failed', error)
  }
}

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

const collectEnvironmentDiagnostics = () => {
  const extendedNavigator = navigator as Navigator & {
    deviceMemory?: number
    connection?: NavigatorConnection
  }
  const connection = extendedNavigator.connection

  diagnosticEnvironment.value = {
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    language: navigator.language,
    languages: navigator.languages,
    hardwareConcurrency: navigator.hardwareConcurrency,
    deviceMemoryGiB: extendedNavigator.deviceMemory ?? null,
    maxTouchPoints: navigator.maxTouchPoints,
    viewport: {
      width: window.innerWidth,
      height: window.innerHeight,
    },
    screen: {
      width: window.screen.width,
      height: window.screen.height,
      colorDepth: window.screen.colorDepth,
      orientation: window.screen.orientation?.type ?? null,
    },
    devicePixelRatio: window.devicePixelRatio,
    visibilityState: document.visibilityState,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    mobileRendererBudget: useMobileRendererBudget,
    realtimeShadows: useRealtimeShadows,
    network: connection ? {
      effectiveType: connection.effectiveType ?? null,
      downlinkMbps: connection.downlink ?? null,
      rttMs: connection.rtt ?? null,
      saveData: connection.saveData ?? null,
    } : null,
  }
}

const collectWebglDiagnostics = () => {
  if (!renderer) return

  try {
    const gl = renderer.getContext()
    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info') as {
      UNMASKED_VENDOR_WEBGL: number
      UNMASKED_RENDERER_WEBGL: number
    } | null
    const maxViewportDimensions = gl.getParameter(gl.MAX_VIEWPORT_DIMS) as Int32Array
    const maxSamples = 'MAX_SAMPLES' in gl
      ? gl.getParameter((gl as WebGL2RenderingContext).MAX_SAMPLES)
      : null

    diagnosticWebgl.value = {
      threeRevision: THREE.REVISION,
      version: gl.getParameter(gl.VERSION),
      shadingLanguageVersion: gl.getParameter(gl.SHADING_LANGUAGE_VERSION),
      vendor: gl.getParameter(gl.VENDOR),
      renderer: gl.getParameter(gl.RENDERER),
      unmaskedVendor: debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : null,
      unmaskedRenderer: debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : null,
      contextAttributes: gl.getContextAttributes(),
      isContextLost: gl.isContextLost(),
      drawingBuffer: {
        width: gl.drawingBufferWidth,
        height: gl.drawingBufferHeight,
      },
      limits: {
        maxTextureSize: gl.getParameter(gl.MAX_TEXTURE_SIZE),
        maxCubeMapTextureSize: gl.getParameter(gl.MAX_CUBE_MAP_TEXTURE_SIZE),
        maxRenderbufferSize: gl.getParameter(gl.MAX_RENDERBUFFER_SIZE),
        maxViewportDimensions: Array.from(maxViewportDimensions),
        maxSamples,
        maxCombinedTextureImageUnits: gl.getParameter(gl.MAX_COMBINED_TEXTURE_IMAGE_UNITS),
        maxVertexAttribs: gl.getParameter(gl.MAX_VERTEX_ATTRIBS),
      },
      maxAnisotropy: renderer.capabilities.getMaxAnisotropy(),
      supportedExtensions: gl.getSupportedExtensions(),
      rendererSettings: {
        pixelRatio: renderer.getPixelRatio(),
        antialias: !useMobileRendererBudget,
        powerPreference: useMobileRendererBudget ? 'default' : 'high-performance',
        shadowMapEnabled: renderer.shadowMap.enabled,
        shadowMapSize: useRealtimeShadows ? 1024 : 0,
        transmissionDisabled: useMobileRendererBudget,
      },
    }
  } catch (error) {
    recordDiagnosticEvent('webgl-diagnostics-failed', { error: describeError(error) })
  }
}

const collectModelDiagnostics = (root: THREE.Group) => {
  const geometries = new Set<THREE.BufferGeometry>()
  const materials = new Set<THREE.Material>()
  const textures = new Set<THREE.Texture>()
  const materialDetails: Record<string, unknown>[] = []
  let nodeCount = 0
  let meshCount = 0
  let vertexCount = 0
  let triangleCount = 0

  root.traverse((object) => {
    nodeCount += 1
    if (!(object instanceof THREE.Mesh)) return

    meshCount += 1
    if (!geometries.has(object.geometry)) {
      geometries.add(object.geometry)
      const position = object.geometry.getAttribute('position')
      vertexCount += position?.count ?? 0
      triangleCount += object.geometry.index
        ? object.geometry.index.count / 3
        : (position?.count ?? 0) / 3
    }

    const meshMaterials = Array.isArray(object.material) ? object.material : [object.material]
    meshMaterials.forEach((material) => {
      if (materials.has(material)) return

      materials.add(material)
      Object.values(material).forEach((value) => {
        if (value instanceof THREE.Texture) textures.add(value)
      })

      materialDetails.push({
        name: material.name || null,
        type: material.type,
        side: material.side,
        transparent: material.transparent,
        opacity: material.opacity,
        transmission: material instanceof THREE.MeshPhysicalMaterial ? material.transmission : null,
        clearcoat: material instanceof THREE.MeshPhysicalMaterial ? material.clearcoat : null,
        ior: material instanceof THREE.MeshPhysicalMaterial ? material.ior : null,
      })
    })
  })

  diagnosticModel.value = {
    nodes: nodeCount,
    meshes: meshCount,
    uniqueGeometries: geometries.size,
    vertices: vertexCount,
    triangles: Math.round(triangleCount),
    uniqueMaterials: materials.size,
    textures: textures.size,
    materials: materialDetails,
  }
}

const rendererRuntimeDetails = () => renderer ? {
  memory: { ...renderer.info.memory },
  render: { ...renderer.info.render },
  programs: renderer.info.programs?.length ?? 0,
} : {}

const reportFailure = (code: ViewerFailureCode, detail: string, error?: unknown) => {
  if (disposed) return
  if (viewerFailure.value?.code === 'WEBGL_CONTEXT_LOST') return

  const failureStage = currentDiagnosticStage
  recordDiagnosticEvent('viewer-failure', {
    code,
    detail,
    failureStage,
    progressPercent: Math.round(loadProgress.value * 100),
  })
  modelReady.value = false
  modelFailed.value = true
  viewerFailure.value = { code, detail }
  console.error('[3D macaron viewer]', {
    code,
    detail,
    progress: Math.round(loadProgress.value * 100),
    error,
    report: JSON.parse(diagnosticReport.value),
  })
}

const handleContextCreationError = (event: Event) => {
  const statusMessage = (event as WebGLContextEvent).statusMessage
  contextCreationError = statusMessage || 'The browser rejected the WebGL context.'
  recordDiagnosticEvent('webgl-context-creation-error', {
    statusMessage: contextCreationError,
  })
}

const handleContextLost = (event: Event) => {
  window.cancelAnimationFrame(animationFrame)
  const statusMessage = (event as WebGLContextEvent).statusMessage
  const stageBeforeContextLoss = currentDiagnosticStage
  let isContextLost: boolean | null = null
  try {
    isContextLost = renderer?.getContext().isContextLost() ?? null
  } catch {
    isContextLost = null
  }
  recordDiagnosticEvent('webgl-context-lost', {
    stageBeforeContextLoss,
    statusMessage: statusMessage || null,
    isContextLost,
    progressPercent: Math.round(loadProgress.value * 100),
    rendererInfo: rendererRuntimeDetails(),
  })
  reportFailure(
    'WEBGL_CONTEXT_LOST',
    statusMessage || 'The browser reported that the WebGL context was lost.',
    event,
  )
}

const handleContextRestored = () => {
  recordDiagnosticEvent('webgl-context-restored')
}

const handleVisibilityChange = () => {
  isVisible = document.visibilityState === 'visible'
  recordDiagnosticEvent(`visibility-${document.visibilityState}`)
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
}

const resize = () => {
  if (!viewer.value || !renderer || !camera) return

  const { width, height } = viewer.value.getBoundingClientRect()
  if (!width || !height) return

  renderer.setSize(width, height, false)
  const canvasSize = `${Math.round(width)}x${Math.round(height)}@${renderer.getPixelRatio()}`
  if (canvasSize !== lastCanvasSize) {
    lastCanvasSize = canvasSize
    recordDiagnosticEvent('canvas-resized', {
      cssWidth: Math.round(width),
      cssHeight: Math.round(height),
      drawingBufferWidth: renderer.getContext().drawingBufferWidth,
      drawingBufferHeight: renderer.getContext().drawingBufferHeight,
      pixelRatio: renderer.getPixelRatio(),
    })
  }
  const aspect = width / height
  const halfHeight = Math.max(2.45, 2.18 / aspect)
  camera.left = -halfHeight * aspect
  camera.right = halfHeight * aspect
  camera.top = halfHeight
  camera.bottom = -halfHeight
  camera.updateProjectionMatrix()
}

const scheduleResize = () => {
  window.cancelAnimationFrame(resizeFrame)
  resizeFrame = window.requestAnimationFrame(resize)
}

const render = () => {
  if (modelFailed.value) return

  animationFrame = window.requestAnimationFrame(render)
  if (!renderer || !scene || !camera || !controls || !isVisible) return

  try {
    if (!firstFrameRendered) {
      recordDiagnosticEvent('first-render-start', {
        rendererInfo: rendererRuntimeDetails(),
      })
    }
    controls.update()
    renderer.render(scene, camera)
    if (!firstFrameRendered) {
      firstFrameRendered = true
      recordDiagnosticEvent('first-render-complete', {
        rendererInfo: rendererRuntimeDetails(),
      })
      recordDiagnosticEvent('render-loop-active')
    }
  } catch (error) {
    window.cancelAnimationFrame(animationFrame)
    reportFailure('VIEWER_RENDER_FAILED', describeError(error), error)
  }
}

const resetView = () => {
  if (!controls || !model) return
  recordDiagnosticEvent('view-reset')
  controls.reset()
  model.rotation.y = 0
  controls.update()
}

const loadModel = async () => {
  if (!scene || !renderer || modelFailed.value) return

  const loadState: { stage: ModelLoadStage } = { stage: 'download' }
  let failedResourceUrl = ''
  let disabledTransmissionMaterials = 0
  let shadowCasterMeshes = 0
  let shadowReceiverMeshes = 0
  const loadingManager = new THREE.LoadingManager()
  loadingManager.onLoad = () => {
    recordDiagnosticEvent('model-resources-loaded')
  }
  loadingManager.onError = (url) => {
    failedResourceUrl = url
    recordDiagnosticEvent('model-resource-error', {
      resource: url.startsWith('blob:') ? 'embedded-model-resource' : url,
    })
  }

  try {
    recordDiagnosticEvent('model-download-start', {
      asset: props.modelUrl.split('/').pop() ?? 'model.glb',
    })
    const gltf = await new GLTFLoader(loadingManager).loadAsync(props.modelUrl, (event) => {
      if (event.total <= 0) return

      loadProgress.value = Math.min(1, event.loaded / event.total)
      const progressBucket = Math.min(100, Math.floor(loadProgress.value * 10) * 10)
      if (progressBucket !== lastProgressBucket) {
        lastProgressBucket = progressBucket
        recordDiagnosticEvent('model-download-progress', {
          percent: progressBucket,
          loadedBytes: event.loaded,
          totalBytes: event.total,
        })
      }
      if (event.loaded >= event.total) {
        loadState.stage = 'parse'
        recordDiagnosticEvent('model-download-complete', {
          loadedBytes: event.loaded,
          totalBytes: event.total,
        })
      }
    })

    loadState.stage = 'prepare'
    recordDiagnosticEvent('model-loader-resolved')

    if (disposed || modelFailed.value || !scene) {
      disposeModel(gltf.scene)
      return
    }

    model = gltf.scene
    model.name = 'window-notes-macaron'
    collectModelDiagnostics(model)
    const maxAnisotropy = renderer.capabilities.getMaxAnisotropy()

    model.traverse((object) => {
      if (!(object instanceof THREE.Mesh)) return
      object.castShadow = useRealtimeShadows
      object.receiveShadow = useRealtimeShadows
      if (object.castShadow) shadowCasterMeshes += 1
      if (object.receiveShadow) shadowReceiverMeshes += 1
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
          disabledTransmissionMaterials += 1
        }
      })
    })

    const bounds = new THREE.Box3().setFromObject(model)
    model.position.sub(bounds.getCenter(new THREE.Vector3()))
    model.rotation.y = 0
    scene.add(model)

    if (ground) ground.position.y = new THREE.Box3().setFromObject(model).min.y - 0.08

    loadProgress.value = 1
    modelReady.value = true
    recordDiagnosticEvent('model-prepared', {
      disabledTransmissionMaterials,
      shadowCasterMeshes,
      shadowReceiverMeshes,
      rendererInfo: rendererRuntimeDetails(),
    })
    render()
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
  useRealtimeShadows = !useMobileRendererBudget
  collectEnvironmentDiagnostics()
  recordDiagnosticEvent('component-mounted', {
    mobileRendererBudget: useMobileRendererBudget,
    realtimeShadows: useRealtimeShadows,
  })
  recordDiagnosticEvent('shadow-policy-configured', {
    policy: useRealtimeShadows ? 'desktop-realtime' : 'mobile-disabled-ab-test',
    enabled: useRealtimeShadows,
  })

  canvas.value.addEventListener('webglcontextcreationerror', handleContextCreationError)
  canvas.value.addEventListener('webglcontextlost', handleContextLost)
  canvas.value.addEventListener('webglcontextrestored', handleContextRestored)

  try {
    recordDiagnosticEvent('renderer-create-start')
    renderer = new THREE.WebGLRenderer({
      canvas: canvas.value,
      alpha: true,
      antialias: !useMobileRendererBudget,
      powerPreference: useMobileRendererBudget ? 'default' : 'high-performance',
    })
    recordDiagnosticEvent('renderer-created')
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
    renderer.shadowMap.enabled = useRealtimeShadows
    renderer.shadowMap.type = THREE.PCFShadowMap
    collectWebglDiagnostics()

    scene = new THREE.Scene()
    camera = new THREE.OrthographicCamera(-2.5, 2.5, 2.5, -2.5, 0.1, 100)
    camera.position.set(5.8, 4.2, 3.35)

    recordDiagnosticEvent('environment-map-create-start')
    const pmremGenerator = new THREE.PMREMGenerator(renderer)
    const roomEnvironment = new RoomEnvironment()
    environmentRenderTarget = pmremGenerator.fromScene(roomEnvironment, 0.035)
    scene.environment = environmentRenderTarget.texture
    roomEnvironment.dispose()
    pmremGenerator.dispose()
    recordDiagnosticEvent('environment-map-created', {
      rendererInfo: rendererRuntimeDetails(),
    })

    const hemisphere = new THREE.HemisphereLight('#fff8ee', '#755268', 0.25)
    hemisphere.name = 'hemisphere-light'
    scene.add(hemisphere)

    const ambientLight = new THREE.AmbientLight('#fff7ef', 0.065)
    ambientLight.name = 'ambient-light'
    scene.add(ambientLight)

    const keyLight = new THREE.DirectionalLight('#ffe8cf', 0.62)
    keyLight.name = 'key-light'
    keyLight.position.set(4.2, 7.5, 5.6)
    keyLight.castShadow = useRealtimeShadows
    if (useRealtimeShadows) keyLight.shadow.mapSize.set(1024, 1024)
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
    ground.receiveShadow = useRealtimeShadows
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

    updateLightingForTheme()
    resizeObserver = new ResizeObserver(scheduleResize)
    resizeObserver.observe(viewer.value)
    document.addEventListener('visibilitychange', handleVisibilityChange)
    resize()
    collectWebglDiagnostics()
    controls.update()
    recordDiagnosticEvent('viewer-initialized', {
      rendererInfo: rendererRuntimeDetails(),
    })
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
  canvas.value?.removeEventListener('webglcontextrestored', handleContextRestored)
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
        <details v-if="viewerFailure" class="model-viewer-diagnostic-report">
          <summary>{{ diagnosticReportLabel }}</summary>
          <button type="button" @click="copyDiagnosticReport">
            {{ diagnosticCopyButtonLabel }}
          </button>
          <pre tabindex="0">{{ diagnosticReport }}</pre>
        </details>
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
  max-height: min(64%, 480px);
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

.model-viewer-diagnostic-report {
  margin-top: 4px;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: var(--header-surface);
  text-align: left;
}

.model-viewer-diagnostic-report summary {
  padding: 9px 12px;
  color: var(--ink);
  font-size: 0.68rem;
  font-weight: 700;
  cursor: pointer;
}

.model-viewer-diagnostic-report button {
  width: calc(100% - 20px);
  margin: 0 10px 10px;
  padding: 8px 10px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--gallery-surface);
  color: var(--ink);
  font: inherit;
  font-size: 0.66rem;
  cursor: pointer;
}

.model-viewer-diagnostic-report pre {
  max-height: 220px;
  margin: 0;
  overflow: auto;
  padding: 11px;
  border-top: 1px solid var(--line);
  color: var(--ink-soft);
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 0.55rem;
  line-height: 1.45;
  overscroll-behavior: contain;
  user-select: text;
  white-space: pre;
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

  .model-viewer-error {
    right: 16px;
    bottom: 18px;
    left: 16px;
    max-height: 68%;
  }
}
</style>
