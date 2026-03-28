export type UnitType =
  | 'raw'        // 原料
  | 'reactor'    // 反応器
  | 'distillation' // 蒸留塔
  | 'mixer'      // 混合器
  | 'heatExchanger' // 熱交換器
  | 'pump'       // ポンプ
  | 'tank'       // タンク
  | 'filter'     // フィルター
  | 'dryer'      // 乾燥機
  | 'compressor' // 圧縮機
  | 'separator'  // 分離器
  | 'product'    // 製品
  | 'waste'      // 廃棄物
  | 'custom'     // カスタム

export interface StreamComponent {
  name: string
  flowRate: number // kg/h
  unit: string
}

export interface StreamData {
  id: string
  label: string
  components: StreamComponent[]
  temperature: number  // °C
  pressure: number     // atm
  specificHeat: number // kJ/(kg·°C)
  reactionHeat: number // kJ/h (正=発熱, 負=吸熱)
}

export interface ProcessStep {
  id: string
  name: string
  type: UnitType
  params: string  // 条件（温度、圧力等）
  inputStreams: string[]  // stream IDs
  outputStreams: string[] // stream IDs
}

export interface ProcessConnection {
  fromStepId: string
  toStepId: string
  streamId: string
}

export interface ProcessData {
  steps: ProcessStep[]
  streams: StreamData[]
  connections: ProcessConnection[]
}

export interface MaterialBalanceResult {
  stepId: string
  stepName: string
  inputTotal: number
  outputTotal: number
  difference: number
  balanced: boolean
  componentDetails: {
    component: string
    input: number
    output: number
    diff: number
  }[]
}

export interface HeatBalanceResult {
  stepId: string
  stepName: string
  inputHeat: number   // kJ/h
  outputHeat: number  // kJ/h
  reactionHeat: number // kJ/h
  requiredHeat: number // kJ/h (正=加熱必要, 負=冷却必要)
}

export const UNIT_TYPE_LABELS: Record<UnitType, string> = {
  raw: '原料',
  reactor: '反応器',
  distillation: '蒸留塔',
  mixer: '混合器',
  heatExchanger: '熱交換器',
  pump: 'ポンプ',
  tank: 'タンク',
  filter: 'フィルター',
  dryer: '乾燥機',
  compressor: '圧縮機',
  separator: '分離器',
  product: '製品',
  waste: '廃棄物',
  custom: 'カスタム',
}

export const UNIT_TYPE_SHAPES: Record<UnitType, { open: string; close: string }> = {
  raw: { open: '([', close: '])' },         // stadium
  reactor: { open: '{{', close: '}}' },     // hexagon
  distillation: { open: '[/', close: '\\]' }, // parallelogram
  mixer: { open: '((', close: '))' },        // circle
  heatExchanger: { open: '[/', close: '/]' }, // lean right
  pump: { open: '>', close: ']' },           // flag
  tank: { open: '[(', close: ')]' },         // cylinder
  filter: { open: '{', close: '}' },         // rhombus
  dryer: { open: '[[', close: ']]' },        // subroutine
  compressor: { open: '((', close: '))' },   // circle
  separator: { open: '{', close: '}' },      // rhombus
  product: { open: '([', close: '])' },      // stadium
  waste: { open: '([', close: '])' },        // stadium
  custom: { open: '[', close: ']' },         // rectangle
}
