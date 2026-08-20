import { readFile, stat } from 'node:fs/promises'
import { resolve } from 'node:path'

const root = resolve(import.meta.dirname, '..')
const dist = resolve(root, 'dist')
const content = JSON.parse(await readFile(resolve(root, 'src/data/seo.json'), 'utf8'))
const languages = ['zh', 'en']
const siteUrl = content.site.baseUrl.endsWith('/') ? content.site.baseUrl : `${content.site.baseUrl}/`
const failures = []

const expect = (condition, message) => {
  if (!condition) failures.push(message)
}

const count = (value, pattern) => value.match(pattern)?.length ?? 0
const routeUrl = (language, slug = null) => (
  new URL(slug ? `${language}/macarons/${slug}/` : `${language}/`, siteUrl).href
)

const readPngSize = async (path) => {
  const file = await readFile(path)
  expect(file.subarray(1, 4).toString('ascii') === 'PNG', `${path} is not a PNG`)
  return { width: file.readUInt32BE(16), height: file.readUInt32BE(20) }
}

for (const language of languages) {
  for (const project of [null, ...content.projects]) {
    const slug = project?.slug ?? null
    const htmlPath = project
      ? resolve(dist, language, 'macarons', project.slug, 'index.html')
      : resolve(dist, language, 'index.html')
    const html = await readFile(htmlPath, 'utf8')
    const label = `${language}/${slug ?? 'home'}`
    const expectedCanonical = routeUrl(language, slug)
    const expectedXDefault = project ? routeUrl('zh', slug) : siteUrl

    expect(count(html, /<title>/g) === 1, `${label} must have one title`)
    expect(count(html, /name="description"/g) === 1, `${label} must have one description`)
    expect(count(html, /rel="canonical"/g) === 1, `${label} must have one canonical`)
    expect(count(html, /hreflang="zh-Hant"/g) === 1, `${label} must link zh-Hant once`)
    expect(count(html, /hreflang="en"/g) === 1, `${label} must link en once`)
    expect(count(html, /hreflang="x-default"/g) === 1, `${label} must link x-default once`)
    expect(html.includes(`rel="canonical" href="${expectedCanonical}"`), `${label} canonical is incorrect`)
    expect(html.includes(`hreflang="x-default" href="${expectedXDefault}"`), `${label} x-default is incorrect`)
    expect(html.includes('name="robots" content="index, follow'), `${label} must be indexable`)
    expect(html.includes('property="og:image"'), `${label} is missing og:image`)
    expect(html.includes('name="twitter:card" content="summary_large_image"'), `${label} is missing Twitter card metadata`)
    expect(html.includes(`social/${language}/home.png`), `${label} must use the phase-one homepage preview`)
    expect(html.includes('<noscript>'), `${label} is missing a no-JavaScript crawl fallback`)

    const jsonLdMatches = [...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)]
    expect(jsonLdMatches.length === 1, `${label} must have one JSON-LD block`)
    if (jsonLdMatches[0]) {
      try {
        JSON.parse(jsonLdMatches[0][1])
      } catch (error) {
        failures.push(`${label} contains invalid JSON-LD: ${error.message}`)
      }
    }
  }

  const homePreview = resolve(dist, 'social', language, 'home.png')
  await stat(homePreview)
  const size = await readPngSize(homePreview)
  expect(size.width === 1200 && size.height === 630, `${language} homepage preview must be 1200x630`)
}

const sitemap = await readFile(resolve(dist, 'sitemap.xml'), 'utf8')
expect(count(sitemap, /<url>/g) === 22, 'sitemap.xml must contain 22 localized URLs')
expect(count(sitemap, /<loc>/g) === 22, 'sitemap.xml must contain 22 canonical loc entries')

const robots = await readFile(resolve(dist, 'robots.txt'), 'utf8')
expect(robots.includes(`Sitemap: ${new URL('sitemap.xml', siteUrl).href}`), 'robots.txt must reference the canonical sitemap')

const rootHtml = await readFile(resolve(dist, 'index.html'), 'utf8')
expect(rootHtml.includes('name="robots" content="noindex, follow"'), 'root redirect must be noindex, follow')
expect(rootHtml.includes('location.replace('), 'root redirect must choose a localized route')

const notFoundHtml = await readFile(resolve(dist, '404.html'), 'utf8')
expect(notFoundHtml.includes('name="robots" content="noindex, follow"'), '404.html must be noindex, follow')

if (failures.length) {
  console.error(failures.map((failure) => `- ${failure}`).join('\n'))
  process.exitCode = 1
} else {
  console.log('Verified 22 localized SEO routes, sitemap, robots.txt, JSON-LD, and two 1200x630 homepage previews.')
}
