import type { Language } from '../types/portfolio'

export interface PortfolioRoute {
  language: Language
  slug: string | null
}

const languageSegments = new Set<Language>(['zh', 'en'])

const normalizeBasePath = (basePath: string) => {
  const withLeadingSlash = basePath.startsWith('/') ? basePath : `/${basePath}`
  return withLeadingSlash.endsWith('/') ? withLeadingSlash : `${withLeadingSlash}/`
}

export const portfolioBasePath = normalizeBasePath(import.meta.env.BASE_URL)

export const parsePortfolioRoute = (
  pathname: string,
  basePath = portfolioBasePath,
): PortfolioRoute | null => {
  const normalizedBasePath = normalizeBasePath(basePath)

  if (!pathname.startsWith(normalizedBasePath)) {
    return null
  }

  const segments = pathname.slice(normalizedBasePath.length).split('/').filter(Boolean)
  const language = segments[0]

  if (!languageSegments.has(language as Language)) {
    return null
  }

  if (segments.length === 1) {
    return { language: language as Language, slug: null }
  }

  if (segments.length === 3 && segments[1] === 'macarons') {
    return { language: language as Language, slug: segments[2] }
  }

  return null
}

export const portfolioPath = (language: Language, slug: string | null = null) => (
  slug
    ? `${portfolioBasePath}${language}/macarons/${encodeURIComponent(slug)}/`
    : `${portfolioBasePath}${language}/`
)

export const alternateLanguage = (language: Language): Language => language === 'zh' ? 'en' : 'zh'

export const parseLegacyDetailHash = (hash: string) => {
  const match = hash.match(/^#\/macarons\/([^/?#]+)$/)
  return match?.[1] ? decodeURIComponent(match[1]) : null
}
