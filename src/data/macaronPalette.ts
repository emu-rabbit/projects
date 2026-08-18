export interface MacaronPalette {
  color: string
  darkColor: string
}

export const macaronPaletteBySlug = {
  'window-notes': { color: '#d9cddd', darkColor: '#42304f' },
  'boundary-notes': { color: '#e1cfd2', darkColor: '#52303a' },
  'frozen-rabbit-workshop': { color: '#d4dfce', darkColor: '#324d3b' },
  'frozen-rabbit-tome': { color: '#ccdcd4', darkColor: '#2a473d' },
  'link-array': { color: '#ddd8d1', darkColor: '#35322f' },
  'vue-router-rule': { color: '#d7dfd7', darkColor: '#28473f' },
  'dandelifeon': { color: '#e6dfbd', darkColor: '#334f32' },
  'nanb': { color: '#d8d8e4', darkColor: '#313853' },
  '75-alchohol': { color: '#d7e3e5', darkColor: '#294753' },
  '50-hiragana-test': { color: '#ead7dc', darkColor: '#56343f' },
} as const satisfies Readonly<Record<string, MacaronPalette>>
