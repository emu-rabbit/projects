import seoContent from './seo.json'
import type { Language } from '../types/portfolio'

interface LocalizedSeoEntry {
  siteName?: string
  title: string
  heading: string
  category: string
  description: string
  keywords: readonly string[]
  imageAlt: string
}

interface ProjectSeoEntry {
  slug: string
  locales: Record<Language, LocalizedSeoEntry>
}

const projects = seoContent.projects as readonly ProjectSeoEntry[]
const projectBySlug = new Map(projects.map((project) => [project.slug, project]))

const ensureTrailingSlash = (value: string) => value.endsWith('/') ? value : `${value}/`
const configuredSiteUrl = import.meta.env.VITE_SITE_URL || seoContent.site.baseUrl
export const portfolioSiteUrl = ensureTrailingSlash(configuredSiteUrl)

export const getSeoEntry = (language: Language, slug: string | null) => {
  const project = slug ? projectBySlug.get(slug) : null
  return project?.locales[language] ?? seoContent.site.locales[language]
}

export const absolutePortfolioUrl = (language: Language, slug: string | null = null) => (
  new URL(slug ? `${language}/macarons/${slug}/` : `${language}/`, portfolioSiteUrl).href
)

export const socialImageUrl = (language: Language, _slug: string | null = null) => (
  new URL(`social/${language}/home.png`, portfolioSiteUrl).href
)

const setMeta = (selector: string, content: string) => {
  document.head.querySelector<HTMLMetaElement>(selector)?.setAttribute('content', content)
}

const setLink = (selector: string, href: string) => {
  document.head.querySelector<HTMLLinkElement>(selector)?.setAttribute('href', href)
}

export const syncDocumentSeo = (language: Language, slug: string | null) => {
  const entry = getSeoEntry(language, slug)
  const socialImageAlt = seoContent.site.locales[language].imageAlt
  const canonicalUrl = absolutePortfolioUrl(language, slug)
  const imageUrl = socialImageUrl(language, slug)

  document.documentElement.lang = language === 'zh' ? 'zh-Hant' : 'en'
  document.title = entry.title
  setMeta('meta[name="description"]', entry.description)
  setMeta('meta[name="keywords"]', entry.keywords.join(', '))
  setMeta('meta[property="og:title"]', entry.title)
  setMeta('meta[property="og:description"]', entry.description)
  setMeta('meta[property="og:url"]', canonicalUrl)
  setMeta('meta[property="og:image"]', imageUrl)
  setMeta('meta[property="og:image:alt"]', socialImageAlt)
  setMeta('meta[property="og:site_name"]', seoContent.site.locales[language].siteName)
  setMeta('meta[property="og:locale"]', language === 'zh' ? 'zh_TW' : 'en_US')
  setMeta('meta[name="twitter:title"]', entry.title)
  setMeta('meta[name="twitter:description"]', entry.description)
  setMeta('meta[name="twitter:image"]', imageUrl)
  setMeta('meta[name="twitter:image:alt"]', socialImageAlt)
  setLink('link[rel="canonical"]', canonicalUrl)
  setLink('link[rel="alternate"][hreflang="zh-Hant"]', absolutePortfolioUrl('zh', slug))
  setLink('link[rel="alternate"][hreflang="en"]', absolutePortfolioUrl('en', slug))
  setLink(
    'link[rel="alternate"][hreflang="x-default"]',
    slug ? absolutePortfolioUrl('zh', slug) : portfolioSiteUrl,
  )
}
