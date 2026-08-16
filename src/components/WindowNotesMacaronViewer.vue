<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js'

const props = defineProps<{
  accessibleLabel: string
  fallbackAlt: string
  fallbackImage: string
  modelName: string
  modelUrl: string
  theme: 'light' | 'dark'
}>()

const canvas = ref<HTMLCanvasElement | null>(null)
const viewer = ref<HTMLElement | null>(null)
const modelReady = ref(false)
const modelFailed = ref(false)
const loadProgress = ref(0)

let renderer: THREE.WebGLRenderer | null = null
let scene: THREE.Scene | null = null
let camera: THREE.OrthographicCamera | null = null
let controls: OrbitControls | null = null
let model: THREE.Group | null = null
let ground: THREE.Mesh | null = null
let environmentRenderTarget: THREE.WebGLRenderTarget | null = null
let resizeObserver: ResizeObserver | null = null
let motionQuery: MediaQueryList | null = null
let animationFrame = 0
let resizeFrame = 0
let isVisible = true
let disposed = false

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
  animationFrame = window.requestAnimationFrame(render)
  if (!renderer || !scene || !camera || !controls || !isVisible) return
  controls.update()
  renderer.render(scene, camera)
}

const handleVisibilityChange = () => {
  isVisible = document.visibilityState === 'visible'
}

const handleMotionChange = () => {
  if (controls) controls.autoRotate = false
}

const resetView = () => {
  if (!camera || !controls || !model) return

  controls.reset()
  model.rotation.y = 0
  controls.update()
}

const disposeMaterial = (material: THREE.Material) => {
  Object.values(material).forEach((value) => {
    if (value instanceof THREE.Texture) value.dispose()
  })
  material.dispose()
}

const loadModel = async () => {
  if (!scene || !renderer) return

  const loader = new GLTFLoader()

  try {
    const gltf = await loader.loadAsync(props.modelUrl, (event) => {
      if (event.total > 0) loadProgress.value = Math.min(1, event.loaded / event.total)
    })

    if (disposed || !scene) return

    model = gltf.scene
    model.name = props.modelName
    const maxAnisotropy = renderer.capabilities.getMaxAnisotropy()

    model.traverse((object) => {
      if (!(object instanceof THREE.Mesh)) return

      object.castShadow = true
      object.receiveShadow = true
      const meshMaterials = Array.isArray(object.material) ? object.material : [object.material]
      meshMaterials.forEach((material) => {
        const standardMaterial = material as THREE.MeshStandardMaterial
        if (standardMaterial.map) standardMaterial.map.anisotropy = Math.min(8, maxAnisotropy)
      })
    })

    const bounds = new THREE.Box3().setFromObject(model)
    model.position.sub(bounds.getCenter(new THREE.Vector3()))
    model.rotation.y = 0
    scene.add(model)

    if (ground) ground.position.y = new THREE.Box3().setFromObject(model).min.y - 0.08

    loadProgress.value = 1
    modelReady.value = true
    handleMotionChange()
  } catch {
    modelFailed.value = true
  }
}

onMounted(() => {
  if (!canvas.value || !viewer.value) return

  try {
    renderer = new THREE.WebGLRenderer({
      canvas: canvas.value,
      alpha: true,
      antialias: true,
      powerPreference: 'high-performance',
    })
  } catch {
    modelFailed.value = true
    return
  }

  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75))
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.shadowMap.enabled = true
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
  keyLight.castShadow = true
  keyLight.shadow.mapSize.set(1024, 1024)
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
  ground.receiveShadow = true
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
  controls.autoRotateSpeed = 0.42
  controls.saveState()
  controls.addEventListener('start', () => {
    if (controls) controls.autoRotate = false
  })

  motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  motionQuery.addEventListener('change', handleMotionChange)
  updateLightingForTheme()

  resizeObserver = new ResizeObserver(scheduleResize)
  resizeObserver.observe(viewer.value)
  document.addEventListener('visibilitychange', handleVisibilityChange)
  resize()
  controls.update()
  render()
  void loadModel()
})

onBeforeUnmount(() => {
  disposed = true
  window.cancelAnimationFrame(animationFrame)
  window.cancelAnimationFrame(resizeFrame)
  resizeObserver?.disconnect()
  motionQuery?.removeEventListener('change', handleMotionChange)
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  controls?.dispose()

  model?.traverse((object) => {
    if (!(object instanceof THREE.Mesh)) return
    object.geometry.dispose()
    if (Array.isArray(object.material)) object.material.forEach(disposeMaterial)
    else disposeMaterial(object.material)
  })

  ground?.geometry.dispose()
  if (ground) disposeMaterial(ground.material as THREE.Material)
  environmentRenderTarget?.dispose()
  renderer?.dispose()
  renderer?.forceContextLoss()
})

watch(() => props.theme, updateLightingForTheme)
</script>

<template>
  <div ref="viewer" class="model-viewer" :class="{ 'is-ready': modelReady }">
    <canvas
      v-show="!modelFailed"
      ref="canvas"
      class="model-viewer-canvas"
      :aria-label="accessibleLabel"
    />

    <div v-if="!modelReady" class="model-viewer-fallback">
      <img :src="fallbackImage" :alt="fallbackAlt" />
      <span
        v-if="!modelFailed"
        class="model-viewer-progress"
        :style="{ '--load-progress': `${loadProgress * 100}%` }"
        aria-hidden="true"
      />
    </div>

    <div v-if="modelReady" class="model-viewer-toolbar">
      <p>拖曳旋轉・滾輪縮放</p>
      <button type="button" aria-label="重設 3D 模型視角" title="重設視角" @click="resetView">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M20 11a8 8 0 1 0-2.34 5.66M20 5v6h-6" />
        </svg>
      </button>
    </div>
  </div>
</template>
