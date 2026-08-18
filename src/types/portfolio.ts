export type Language = 'zh' | 'en'
export type Theme = 'light' | 'dark'
export type Localized<T> = Record<Language, T>
