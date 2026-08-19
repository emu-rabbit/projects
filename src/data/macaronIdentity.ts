import type { Localized } from '../types/portfolio'

export interface MacaronIdentity {
  name: Localized<string>
  flavor: Localized<string>
}

export type MacaronSlug =
  | 'window-notes'
  | 'boundary-notes'
  | 'frozen-rabbit-workshop'
  | 'frozen-rabbit-tome'
  | 'link-array'
  | 'vue-router-rule'
  | 'dandelifeon'
  | 'nanb'
  | '75-alchohol'
  | '50-hiragana-test'

export const macaronIdentityBySlug = {
  'window-notes': {
    name: { zh: '紫夜兔耳馬卡龍', en: 'Purple Night Rabbit Macaron' },
    flavor: { zh: '暮色杏桃・蜂蜜玫瑰', en: 'Twilight Apricot · Honey Rose' },
  },
  'boundary-notes': {
    name: { zh: '酒紅邊界馬卡龍', en: 'Burgundy Boundary Macaron' },
    flavor: { zh: '黑醋栗・玫瑰伯爵', en: 'Blackcurrant · Rose Earl Grey' },
  },
  'frozen-rabbit-workshop': {
    name: { zh: '薄荷青檸馬卡龍', en: 'Mint Lime Macaron' },
    flavor: { zh: '薄荷・青檸・白巧克力', en: 'Mint · Lime · White Chocolate' },
  },
  'frozen-rabbit-tome': {
    name: { zh: '森林綠柚馬卡龍', en: 'Forest Green Yuzu Macaron' },
    flavor: { zh: '深焙抹茶・柚子金砂', en: 'Roasted Matcha · Yuzu Gold Dust' },
  },
  'link-array': {
    name: { zh: '黑白鏈結馬卡龍', en: 'Black-and-White Linked Macaron' },
    flavor: { zh: '黑白芝麻・鹽焦糖', en: 'Black & White Sesame · Salted Caramel' },
  },
  'vue-router-rule': {
    name: { zh: '綠葡萄荔枝馬卡龍', en: 'Green Grape Lychee Macaron' },
    flavor: { zh: '青葡萄・荔枝・紫羅蘭', en: 'Green Grape · Lychee · Violet' },
  },
  dandelifeon: {
    name: { zh: '蒲公英魔力馬卡龍', en: 'Dandelion Mana Macaron' },
    flavor: { zh: '蒲公英蜜・青蘋果', en: 'Dandelion Honey · Green Apple' },
  },
  nanb: {
    name: { zh: '小倉鼠藍莓馬卡龍', en: 'Hamster Blueberry Macaron' },
    flavor: { zh: '藍莓優格・葵花子', en: 'Blueberry Yogurt · Sunflower Seeds' },
  },
  '75-alchohol': {
    name: { zh: '白葡萄蘇打馬卡龍', en: 'White Grape Soda Macaron' },
    flavor: { zh: '白葡萄・檸檬蘇打', en: 'White Grape · Lemon Soda' },
  },
  '50-hiragana-test': {
    name: { zh: '櫻花紅豆馬卡龍', en: 'Sakura Red Bean Macaron' },
    flavor: { zh: '櫻花牛奶・紅豆', en: 'Sakura Milk · Red Bean' },
  },
} as const satisfies Record<MacaronSlug, MacaronIdentity>
