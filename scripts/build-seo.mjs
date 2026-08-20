import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import process from 'node:process'

const root = resolve(import.meta.dirname, '..')
const distDirectory = resolve(root, 'dist')
const content = JSON.parse(await readFile(resolve(root, 'src/data/seo.json'), 'utf8'))
const template = await readFile(resolve(distDirectory, 'index.html'), 'utf8')
const languages = ['zh', 'en']
const languageTags = { zh: 'zh-Hant', en: 'en' }
const openGraphLocales = { zh: 'zh_TW', en: 'en_US' }
const siteUrl = ensureTrailingSlash(process.env.SITE_URL || content.site.baseUrl)

function ensureTrailingSlash(value) {
  return value.endsWith('/') ? value : `${value}/`
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
}

function escapeXml(value) {
  return escapeHtml(value).replaceAll("'", '&apos;')
}

function routeUrl(language, slug = null) {
  return new URL(slug ? `${language}/macarons/${slug}/` : `${language}/`, siteUrl).href
}

function imageUrl(language, slug = null) {
  void slug
  return new URL(`social/${language}/home.png`, siteUrl).href
}

function imageAlt(language) {
  return content.site.locales[language].imageAlt
}

function projectLocale(project, language) {
  return project.locales[language]
}

function seoEntry(language, project = null) {
  return project ? projectLocale(project, language) : content.site.locales[language]
}

function structuredData(language, project = null) {
  const entry = seoEntry(language, project)
  const canonicalUrl = routeUrl(language, project?.slug)
  const authorId = `${siteUrl}#creator`
  const websiteId = `${siteUrl}#website`
  const person = {
    '@type': 'Person',
    '@id': authorId,
    name: content.site.author.name,
    alternateName: content.site.author.alternateName,
    url: siteUrl,
    sameAs: [content.site.author.githubUrl],
  }
  const website = {
    '@type': 'WebSite',
    '@id': websiteId,
    url: siteUrl,
    name: entry.siteName ?? content.site.locales[language].siteName,
    inLanguage: languageTags[language],
    creator: { '@id': authorId },
  }

  if (!project) {
    return {
      '@context': 'https://schema.org',
      '@graph': [
        person,
        website,
        {
          '@type': 'CollectionPage',
          '@id': `${canonicalUrl}#webpage`,
          url: canonicalUrl,
          name: entry.title,
          description: entry.description,
          inLanguage: languageTags[language],
          isPartOf: { '@id': websiteId },
          author: { '@id': authorId },
          primaryImageOfPage: {
            '@type': 'ImageObject',
            url: imageUrl(language),
            width: 1200,
            height: 630,
            caption: imageAlt(language),
          },
          mainEntity: {
            '@type': 'ItemList',
            numberOfItems: content.projects.length,
            itemListElement: content.projects.map((item, index) => ({
              '@type': 'ListItem',
              position: index + 1,
              name: item.locales[language].heading,
              url: routeUrl(language, item.slug),
              image: imageUrl(language),
            })),
          },
        },
      ],
    }
  }

  const githubUrl = project.sameAs.find((url) => url.includes('github.com/'))
  const liveUrl = project.sameAs.find((url) => !url.includes('github.com/'))
  const software = {
    '@type': project.slug === 'link-array' ? 'SoftwareSourceCode' : 'SoftwareApplication',
    '@id': `${canonicalUrl}#project`,
    name: entry.heading,
    description: entry.description,
    image: imageUrl(language, project.slug),
    url: liveUrl ?? canonicalUrl,
    sameAs: project.sameAs,
    keywords: entry.keywords,
    creator: { '@id': authorId },
    inLanguage: languageTags[language],
  }

  if (software['@type'] === 'SoftwareApplication') {
    Object.assign(software, {
      applicationCategory: project.applicationCategory,
      operatingSystem: 'Web browser',
      offers: {
        '@type': 'Offer',
        price: 0,
        priceCurrency: 'USD',
      },
    })
  } else if (githubUrl) {
    software.codeRepository = githubUrl
    software.programmingLanguage = ['TypeScript', 'JavaScript']
  }

  return {
    '@context': 'https://schema.org',
    '@graph': [
      person,
      website,
      {
        '@type': 'WebPage',
        '@id': `${canonicalUrl}#webpage`,
        url: canonicalUrl,
        name: entry.title,
        description: entry.description,
        inLanguage: languageTags[language],
        isPartOf: { '@id': websiteId },
        author: { '@id': authorId },
        primaryImageOfPage: {
          '@type': 'ImageObject',
          url: imageUrl(language, project.slug),
          width: 1200,
          height: 630,
          caption: imageAlt(language),
        },
        breadcrumb: {
          '@type': 'BreadcrumbList',
          itemListElement: [
            {
              '@type': 'ListItem',
              position: 1,
              name: content.site.locales[language].siteName,
              item: routeUrl(language),
            },
            {
              '@type': 'ListItem',
              position: 2,
              name: entry.heading,
              item: canonicalUrl,
            },
          ],
        },
        mainEntity: { '@id': `${canonicalUrl}#project` },
      },
      software,
    ],
  }
}

function seoBlock(language, project = null) {
  const entry = seoEntry(language, project)
  const canonicalUrl = routeUrl(language, project?.slug)
  const socialImage = imageUrl(language, project?.slug)
  const alternateLanguage = language === 'zh' ? 'en' : 'zh'
  const jsonLd = JSON.stringify(structuredData(language, project)).replaceAll('<', '\\u003c')

  return `<!-- SEO:START -->
    <meta name="description" content="${escapeHtml(entry.description)}" />
    <meta name="keywords" content="${escapeHtml(entry.keywords.join(', '))}" />
    <meta name="author" content="${escapeHtml(`${content.site.author.name} (${content.site.author.alternateName})`)}" />
    <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="${escapeHtml(content.site.locales[language].siteName)}" />
    <meta property="og:title" content="${escapeHtml(entry.title)}" />
    <meta property="og:description" content="${escapeHtml(entry.description)}" />
    <meta property="og:url" content="${escapeHtml(canonicalUrl)}" />
    <meta property="og:locale" content="${openGraphLocales[language]}" />
    <meta property="og:locale:alternate" content="${openGraphLocales[alternateLanguage]}" />
    <meta property="og:image" content="${escapeHtml(socialImage)}" />
    <meta property="og:image:secure_url" content="${escapeHtml(socialImage)}" />
    <meta property="og:image:type" content="image/png" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:image:alt" content="${escapeHtml(imageAlt(language))}" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="${escapeHtml(entry.title)}" />
    <meta name="twitter:description" content="${escapeHtml(entry.description)}" />
    <meta name="twitter:image" content="${escapeHtml(socialImage)}" />
    <meta name="twitter:image:alt" content="${escapeHtml(imageAlt(language))}" />
    <link rel="canonical" href="${escapeHtml(canonicalUrl)}" />
    <link rel="alternate" hreflang="zh-Hant" href="${escapeHtml(routeUrl('zh', project?.slug))}" />
    <link rel="alternate" hreflang="en" href="${escapeHtml(routeUrl('en', project?.slug))}" />
    <link rel="alternate" hreflang="x-default" href="${escapeHtml(project ? routeUrl('zh', project.slug) : siteUrl)}" />
    <link rel="sitemap" type="application/xml" href="${escapeHtml(new URL('sitemap.xml', siteUrl).href)}" />
    <script type="application/ld+json">${jsonLd}</script>
    <!-- SEO:END -->`
}

function noScriptContent(language, project = null) {
  const entry = seoEntry(language, project)
  const homeLabel = language === 'zh' ? '返回作品集首頁' : 'Back to the portfolio home page'

  if (project) {
    return `<noscript><main><article><p>${escapeHtml(entry.category)}</p><h1>${escapeHtml(entry.heading)}</h1><p>${escapeHtml(entry.description)}</p><p><a href="${escapeHtml(routeUrl(language))}">${escapeHtml(homeLabel)}</a></p></article></main></noscript>`
  }

  const links = content.projects.map((item) => (
    `<li><a href="${escapeHtml(routeUrl(language, item.slug))}">${escapeHtml(item.locales[language].heading)}</a></li>`
  )).join('')
  return `<noscript><main><h1>${escapeHtml(entry.heading)}</h1><p>${escapeHtml(entry.description)}</p><ul>${links}</ul></main></noscript>`
}

function renderRoute(language, project = null) {
  const entry = seoEntry(language, project)
  return template
    .replace(/<html lang="[^"]+"/, `<html lang="${languageTags[language]}"`)
    .replace(/<!-- SEO:START -->[\s\S]*?<!-- SEO:END -->/, seoBlock(language, project))
    .replace(/<title>[\s\S]*?<\/title>/, `<title>${escapeHtml(entry.title)}</title>`)
    .replace('<div id="app"></div>', `<div id="app">${noScriptContent(language, project)}</div>`)
}

async function writeRoute(language, project = null) {
  const routeDirectory = project
    ? resolve(distDirectory, language, 'macarons', project.slug)
    : resolve(distDirectory, language)
  await mkdir(routeDirectory, { recursive: true })
  await writeFile(resolve(routeDirectory, 'index.html'), renderRoute(language, project))
}

function rootRedirect() {
  const targetRoot = JSON.stringify(siteUrl)
  return template
    .replace(/<html lang="[^"]+"/, '<html lang="zh-Hant"')
    .replace(/<!-- SEO:START -->[\s\S]*?<!-- SEO:END -->/, `<!-- SEO:START -->
    <meta name="robots" content="noindex, follow" />
    <meta name="description" content="Choose the Chinese or English version of Emu Rabbit Portfolio." />
    <link rel="canonical" href="${escapeHtml(routeUrl('zh'))}" />
    <link rel="alternate" hreflang="zh-Hant" href="${escapeHtml(routeUrl('zh'))}" />
    <link rel="alternate" hreflang="en" href="${escapeHtml(routeUrl('en'))}" />
    <link rel="alternate" hreflang="x-default" href="${escapeHtml(siteUrl)}" />
    <script>
      (() => {
        const root = ${targetRoot};
        const saved = (() => { try { return localStorage.getItem('portfolio-language'); } catch { return null; } })();
        const language = saved === 'en' || (saved !== 'zh' && navigator.language.toLowerCase().startsWith('en')) ? 'en' : 'zh';
        const match = location.hash.match(/^#\\/macarons\\/([^/?#]+)$/);
        const suffix = match ? 'macarons/' + encodeURIComponent(decodeURIComponent(match[1])) + '/' : '';
        location.replace(root + language + '/' + suffix);
      })();
    </script>
    <!-- SEO:END -->`)
    .replace(/<title>[\s\S]*?<\/title>/, '<title>Emu Rabbit Portfolio</title>')
    .replace('<div id="app"></div>', `<div id="app"><noscript><p><a href="${escapeHtml(routeUrl('zh'))}">中文</a> · <a href="${escapeHtml(routeUrl('en'))}">English</a></p></noscript></div>`)
}

function notFoundPage() {
  return `<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="robots" content="noindex, follow" />
  <title>找不到頁面 | Page not found</title>
</head>
<body>
  <main>
    <h1>找不到頁面</h1>
    <p>The page you requested could not be found.</p>
    <p><a href="${escapeHtml(siteUrl)}">返回作品集首頁 · Back to the portfolio</a></p>
  </main>
</body>
</html>`
}

function sitemap() {
  const entries = []
  for (const project of [null, ...content.projects]) {
    for (const language of languages) {
      const entry = seoEntry(language, project)
      const slug = project?.slug ?? null
      entries.push(`  <url>
    <loc>${escapeXml(routeUrl(language, slug))}</loc>
    <xhtml:link rel="alternate" hreflang="zh-Hant" href="${escapeXml(routeUrl('zh', slug))}" />
    <xhtml:link rel="alternate" hreflang="en" href="${escapeXml(routeUrl('en', slug))}" />
    <xhtml:link rel="alternate" hreflang="x-default" href="${escapeXml(project ? routeUrl('zh', slug) : siteUrl)}" />
    <image:image>
      <image:loc>${escapeXml(imageUrl(language, slug))}</image:loc>
      <image:title>${escapeXml(entry.title)}</image:title>
      <image:caption>${escapeXml(imageAlt(language))}</image:caption>
    </image:image>
  </url>`)
    }
  }
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
${entries.join('\n')}
</urlset>
`
}

for (const language of languages) {
  await writeRoute(language)
  for (const project of content.projects) {
    await writeRoute(language, project)
  }
}

await writeFile(resolve(distDirectory, 'index.html'), rootRedirect())
await writeFile(resolve(distDirectory, '404.html'), notFoundPage())
await writeFile(resolve(distDirectory, 'sitemap.xml'), sitemap())
await writeFile(resolve(distDirectory, 'robots.txt'), `User-agent: *\nAllow: /\n\nSitemap: ${new URL('sitemap.xml', siteUrl).href}\n`)

console.log(`Generated ${languages.length * (content.projects.length + 1)} localized SEO routes for ${siteUrl}`)
