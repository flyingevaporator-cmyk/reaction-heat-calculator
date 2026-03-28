import type { UnitType } from './types'

const W = 60
const H = 60

function svgToDataUri(content: string, w = W, h = H): string {
  const svgStr = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${content}</svg>`
  const encoded = btoa(unescape(encodeURIComponent(svgStr)))
  return `data:image/svg+xml;base64,${encoded}`
}

const ICONS: Record<UnitType, string> = {
  // 原料: ドラム缶
  raw: svgToDataUri(`
    <ellipse cx="30" cy="14" rx="18" ry="7" fill="#c8f0c8" stroke="#4a8c4a" stroke-width="2"/>
    <rect x="12" y="14" width="36" height="30" fill="#b8e6b8" stroke="none"/>
    <ellipse cx="30" cy="44" rx="18" ry="7" fill="#a0d8a0" stroke="#4a8c4a" stroke-width="2"/>
    <line x1="12" y1="14" x2="12" y2="44" stroke="#4a8c4a" stroke-width="2"/>
    <line x1="48" y1="14" x2="48" y2="44" stroke="#4a8c4a" stroke-width="2"/>
    <ellipse cx="30" cy="14" rx="18" ry="7" fill="#c8f0c8" stroke="#4a8c4a" stroke-width="2"/>
  `),

  // 反応器: 攪拌機付き縦型容器
  reactor: svgToDataUri(`
    <rect x="14" y="16" width="32" height="34" rx="3" fill="#ffcc99" stroke="none"/>
    <ellipse cx="30" cy="16" rx="16" ry="5" fill="#ffe0b8" stroke="#cc6633" stroke-width="2"/>
    <ellipse cx="30" cy="50" rx="16" ry="5" fill="#f0b880" stroke="#cc6633" stroke-width="2"/>
    <line x1="14" y1="16" x2="14" y2="50" stroke="#cc6633" stroke-width="2"/>
    <line x1="46" y1="16" x2="46" y2="50" stroke="#cc6633" stroke-width="2"/>
    <line x1="30" y1="6" x2="30" y2="32" stroke="#cc6633" stroke-width="2"/>
    <line x1="22" y1="30" x2="38" y2="26" stroke="#cc6633" stroke-width="2.5"/>
    <line x1="22" y1="36" x2="38" y2="32" stroke="#cc6633" stroke-width="2.5"/>
    <rect x="26" y="3" width="8" height="6" rx="1" fill="#999" stroke="#666" stroke-width="1.5"/>
  `),

  // 蒸留塔: 段付きカラム
  distillation: svgToDataUri(`
    <rect x="20" y="4" width="20" height="52" rx="10" fill="#99ccff" stroke="#3366cc" stroke-width="2"/>
    <line x1="20" y1="16" x2="40" y2="16" stroke="#3366cc" stroke-width="1.5"/>
    <line x1="20" y1="24" x2="40" y2="24" stroke="#3366cc" stroke-width="1.5"/>
    <line x1="20" y1="32" x2="40" y2="32" stroke="#3366cc" stroke-width="1.5"/>
    <line x1="20" y1="40" x2="40" y2="40" stroke="#3366cc" stroke-width="1.5"/>
    <line x1="10" y1="12" x2="20" y2="12" stroke="#3366cc" stroke-width="2"/>
    <line x1="40" y1="8" x2="50" y2="8" stroke="#3366cc" stroke-width="2"/>
    <line x1="40" y1="48" x2="50" y2="48" stroke="#3366cc" stroke-width="2"/>
  `),

  // 混合器: 円にM
  mixer: svgToDataUri(`
    <circle cx="30" cy="30" r="22" fill="#e6ccff" stroke="#7733cc" stroke-width="2"/>
    <text x="30" y="37" text-anchor="middle" font-size="20" font-weight="bold" fill="#7733cc" font-family="Arial">M</text>
  `),

  // 熱交換器: シェルアンドチューブ (円+横線)
  heatExchanger: svgToDataUri(`
    <circle cx="30" cy="30" r="22" fill="#ffccdd" stroke="#cc3366" stroke-width="2"/>
    <line x1="8" y1="22" x2="52" y2="22" stroke="#cc3366" stroke-width="2"/>
    <line x1="8" y1="38" x2="52" y2="38" stroke="#cc3366" stroke-width="2"/>
    <path d="M8 22 Q4 30 8 38" fill="none" stroke="#cc3366" stroke-width="2"/>
    <path d="M52 22 Q56 30 52 38" fill="none" stroke="#cc3366" stroke-width="2"/>
  `),

  // ポンプ: 円+三角 (遠心ポンプ記号)
  pump: svgToDataUri(`
    <circle cx="30" cy="30" r="20" fill="#cce6ff" stroke="#336699" stroke-width="2"/>
    <polygon points="20,18 42,30 20,42" fill="#336699" opacity="0.5"/>
    <line x1="50" y1="30" x2="56" y2="30" stroke="#336699" stroke-width="2.5"/>
    <line x1="30" y1="10" x2="30" y2="4" stroke="#336699" stroke-width="2.5"/>
  `),

  // タンク: 縦型貯槽
  tank: svgToDataUri(`
    <ellipse cx="30" cy="14" rx="20" ry="8" fill="#e6ccff" stroke="#7733aa" stroke-width="2"/>
    <rect x="10" y="14" width="40" height="28" fill="#d9b3ff" stroke="none"/>
    <ellipse cx="30" cy="42" rx="20" ry="8" fill="#c899ee" stroke="#7733aa" stroke-width="2"/>
    <line x1="10" y1="14" x2="10" y2="42" stroke="#7733aa" stroke-width="2"/>
    <line x1="50" y1="14" x2="50" y2="42" stroke="#7733aa" stroke-width="2"/>
    <ellipse cx="30" cy="14" rx="20" ry="8" fill="#e6ccff" stroke="#7733aa" stroke-width="2"/>
  `),

  // フィルター: 漏斗型
  filter: svgToDataUri(`
    <polygon points="10,10 50,10 36,36 24,36" fill="#ffffcc" stroke="#999933" stroke-width="2"/>
    <rect x="24" y="36" width="12" height="14" fill="#ffffcc" stroke="#999933" stroke-width="2"/>
    <line x1="15" y1="18" x2="45" y2="18" stroke="#999933" stroke-width="1" stroke-dasharray="3,2"/>
    <line x1="18" y1="24" x2="42" y2="24" stroke="#999933" stroke-width="1" stroke-dasharray="3,2"/>
  `),

  // 乾燥機: 横型回転ドラム
  dryer: svgToDataUri(`
    <ellipse cx="12" cy="30" rx="7" ry="18" fill="#ffe6cc" stroke="#cc8833" stroke-width="2"/>
    <rect x="12" y="12" width="36" height="36" fill="#ffe6cc" stroke="none"/>
    <ellipse cx="48" cy="30" rx="7" ry="18" fill="#ffd9b3" stroke="#cc8833" stroke-width="2"/>
    <line x1="12" y1="12" x2="48" y2="12" stroke="#cc8833" stroke-width="2"/>
    <line x1="12" y1="48" x2="48" y2="48" stroke="#cc8833" stroke-width="2"/>
    <path d="M18 22 Q30 30 42 22" fill="none" stroke="#cc8833" stroke-width="1.5"/>
    <path d="M18 34 Q30 42 42 34" fill="none" stroke="#cc8833" stroke-width="1.5"/>
  `),

  // 圧縮機: ファン/タービン記号
  compressor: svgToDataUri(`
    <polygon points="14,10 46,22 46,38 14,50" fill="#cce6cc" stroke="#338833" stroke-width="2"/>
    <line x1="4" y1="30" x2="14" y2="30" stroke="#338833" stroke-width="2.5"/>
    <line x1="46" y1="30" x2="56" y2="30" stroke="#338833" stroke-width="2.5"/>
  `),

  // 分離器: 縦型容器+仕切り
  separator: svgToDataUri(`
    <rect x="14" y="8" width="32" height="44" rx="4" fill="#cce6ff" stroke="#336699" stroke-width="2"/>
    <line x1="14" y1="30" x2="46" y2="30" stroke="#336699" stroke-width="2" stroke-dasharray="4,3"/>
    <circle cx="30" cy="20" r="3" fill="#99ccff" stroke="#336699" stroke-width="1"/>
    <circle cx="24" cy="22" r="2" fill="#99ccff" stroke="#336699" stroke-width="1"/>
    <circle cx="36" cy="18" r="2.5" fill="#99ccff" stroke="#336699" stroke-width="1"/>
    <rect x="20" y="36" width="20" height="8" rx="1" fill="#88bbee" stroke="#336699" stroke-width="1"/>
  `),

  // 製品: ドラム缶 (金色)
  product: svgToDataUri(`
    <ellipse cx="30" cy="14" rx="18" ry="7" fill="#fff2cc" stroke="#cc9933" stroke-width="2"/>
    <rect x="12" y="14" width="36" height="30" fill="#ffe599" stroke="none"/>
    <ellipse cx="30" cy="44" rx="18" ry="7" fill="#ffd966" stroke="#cc9933" stroke-width="2"/>
    <line x1="12" y1="14" x2="12" y2="44" stroke="#cc9933" stroke-width="2"/>
    <line x1="48" y1="14" x2="48" y2="44" stroke="#cc9933" stroke-width="2"/>
    <ellipse cx="30" cy="14" rx="18" ry="7" fill="#fff2cc" stroke="#cc9933" stroke-width="2"/>
    <text x="30" y="34" text-anchor="middle" font-size="14" font-weight="bold" fill="#cc9933" font-family="Arial">P</text>
  `),

  // 廃棄物: ドラム缶+×
  waste: svgToDataUri(`
    <ellipse cx="30" cy="14" rx="18" ry="7" fill="#f8d0d0" stroke="#993333" stroke-width="2"/>
    <rect x="12" y="14" width="36" height="30" fill="#f0c0c0" stroke="none"/>
    <ellipse cx="30" cy="44" rx="18" ry="7" fill="#e0a0a0" stroke="#993333" stroke-width="2"/>
    <line x1="12" y1="14" x2="12" y2="44" stroke="#993333" stroke-width="2"/>
    <line x1="48" y1="14" x2="48" y2="44" stroke="#993333" stroke-width="2"/>
    <ellipse cx="30" cy="14" rx="18" ry="7" fill="#f8d0d0" stroke="#993333" stroke-width="2"/>
    <line x1="22" y1="22" x2="38" y2="38" stroke="#993333" stroke-width="2.5"/>
    <line x1="38" y1="22" x2="22" y2="38" stroke="#993333" stroke-width="2.5"/>
  `),

  // カスタム: シンプル四角
  custom: svgToDataUri(`
    <rect x="6" y="6" width="48" height="48" rx="6" fill="#e8e8e8" stroke="#888" stroke-width="2"/>
  `),
}

export function getEquipmentIconUri(type: UnitType): string {
  return ICONS[type] || ICONS.custom
}
