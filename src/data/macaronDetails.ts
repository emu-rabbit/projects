import type { Language, Localized } from '../types/portfolio'

type LocalizedText = Localized<string>

export interface MacaronGalleryImage {
  src: string
  alt: LocalizedText
  caption: LocalizedText
}

export interface MacaronProjectLink {
  href: string
  label: LocalizedText
}

export interface MacaronDetail {
  slug: string
  category: LocalizedText
  title: LocalizedText
  paragraphs: Record<Language, readonly string[]>
  closing: LocalizedText
  galleryLabel: LocalizedText
  gallery: readonly MacaronGalleryImage[]
  links: readonly MacaronProjectLink[]
}

const windowNotesGallery = {
  defaultView: new URL('../../assets/galleries/window-notes/default-view.webp', import.meta.url).href,
  threeViews: new URL('../../assets/galleries/window-notes/three-views.webp', import.meta.url).href,
  homepage: new URL('../../assets/galleries/window-notes/homepage.webp', import.meta.url).href,
  skills: new URL('../../assets/galleries/window-notes/skills.webp', import.meta.url).href,
  mobileStory: new URL('../../assets/galleries/window-notes/mobile-story.webp', import.meta.url).href,
} as const

export const macaronDetails = [
  {
    slug: 'window-notes',
    category: { zh: '個人網頁', en: 'Personal Website' },
    title: { zh: '絵夢羽さ沂的窗邊手記', en: "Emu-Rabbit's Window Notes" },
    paragraphs: {
      zh: [
        '我其實是一個很愛寫自我介紹的人，每一次的撰寫，都可以讓我在不同的時間點回頭審視自己。我是誰，我是怎樣的人，我喜歡什麼，我討厭什麼，還有最重要的——此時此刻我想往哪裡去。',
        '所以，我好好地做了一個真正屬於我自己的個人頁面，向所有人介紹我自己，讓想認識我的人有扇窗口可以靠近。',
        '即使和 AI 一起協作，也不能在這麼重要的專案裡，遺失屬於我的味道，這是我在做這個專案時最在乎的事。',
      ],
      en: [
        'I love writing introductions. Each one lets me meet myself again: who I am, what I love or dislike, and where I want to go next.',
        'So I made a page that is truly mine—a window for anyone who wants to come closer.',
        'Even with AI, I could not let this project lose the smell that is uniquely mine. That mattered most.',
      ],
    },
    closing: {
      zh: '「那麼，此時此刻的你正在看著我嗎？」',
      en: '“So, at this very moment, are you looking at me?”',
    },
    galleryLabel: {
      zh: '窗邊手記作品畫廊',
      en: 'Window Notes project gallery',
    },
    gallery: [
      {
        src: windowNotesGallery.defaultView,
        alt: { zh: '窗邊手記馬卡龍的預設視角插畫', en: 'Default view illustration of the Window Notes macaron' },
        caption: { zh: '紫夜兔耳馬卡龍', en: 'Purple Night Rabbit Macaron' },
      },
      {
        src: windowNotesGallery.threeViews,
        alt: { zh: '窗邊手記馬卡龍的預設、頂面與平放側面視圖', en: 'Default, top, and flat side views of the Window Notes macaron' },
        caption: { zh: '更多角度的我', en: 'More Angles of Me' },
      },
      {
        src: windowNotesGallery.homepage,
        alt: { zh: '窗邊手記個人網頁的桌機首頁截圖', en: 'Desktop homepage of the Window Notes personal website' },
        caption: { zh: '網頁主視覺', en: 'Website Hero' },
      },
      {
        src: windowNotesGallery.skills,
        alt: { zh: '窗邊手記個人網頁的英文版頁面截圖', en: 'English version of the Window Notes personal website' },
        caption: { zh: '支援英文版', en: 'English Version' },
      },
      {
        src: windowNotesGallery.mobileStory,
        alt: { zh: '窗邊手記個人網頁的手機版頁面截圖', en: 'Mobile layout of the Window Notes personal website' },
        caption: { zh: '支援手機版面', en: 'Mobile Layout' },
      },
    ],
    links: [
      {
        label: { zh: '線上展示', en: 'Live Website' },
        href: 'https://emu-rabbit.github.io/',
      },
      {
        label: { zh: 'Github頁面', en: 'GitHub Repo' },
        href: 'https://github.com/emu-rabbit/emu-rabbit.github.io',
      },
    ],
  },
] as const satisfies readonly MacaronDetail[]

export const macaronDetailsBySlug: ReadonlyMap<string, MacaronDetail> = new Map(
  macaronDetails.map((detail) => [detail.slug, detail] as const),
)
