import type { ProcessData, ProcessStep, ProcessConnection, StreamData, UnitType } from './types'

let idCounter = 0
function nextId(prefix: string): string {
  return `${prefix}_${++idCounter}`
}

export function resetParser() {
  idCounter = 0
}

const TYPE_KEYWORDS: Record<string, UnitType> = {
  '原料': 'raw',
  'raw': 'raw',
  '反応器': 'reactor',
  '反応': 'reactor',
  'reactor': 'reactor',
  '蒸留塔': 'distillation',
  '蒸留': 'distillation',
  'distillation': 'distillation',
  '混合器': 'mixer',
  '混合': 'mixer',
  'mixer': 'mixer',
  '熱交換器': 'heatExchanger',
  '熱交換': 'heatExchanger',
  'heat exchanger': 'heatExchanger',
  'ポンプ': 'pump',
  'pump': 'pump',
  'タンク': 'tank',
  'tank': 'tank',
  'フィルター': 'filter',
  '濾過': 'filter',
  'filter': 'filter',
  '乾燥機': 'dryer',
  '乾燥': 'dryer',
  'dryer': 'dryer',
  '圧縮機': 'compressor',
  '圧縮': 'compressor',
  'compressor': 'compressor',
  '分離器': 'separator',
  '分離': 'separator',
  'separator': 'separator',
  '製品': 'product',
  'product': 'product',
  '廃棄物': 'waste',
  '廃棄': 'waste',
  'waste': 'waste',
}

function guessType(name: string): UnitType {
  const lower = name.toLowerCase()
  for (const [keyword, type] of Object.entries(TYPE_KEYWORDS)) {
    if (lower.includes(keyword)) return type
  }
  return 'custom'
}

interface ParsedNode {
  name: string
  params: string
  components: { name: string; amount: number }[]
}

function parseNode(raw: string): ParsedNode {
  let name = raw.trim()
  let params = ''
  const components: { name: string; amount: number }[] = []

  // Extract components: 原料(水:100kg, エタノール:50kg)
  const compMatch = name.match(/^(.+?)\((.+?)\)$/)
  if (compMatch) {
    name = compMatch[1].trim()
    const compStr = compMatch[2]
    for (const part of compStr.split(',')) {
      const m = part.trim().match(/^(.+?)\s*:\s*([\d.]+)\s*(\w*)$/)
      if (m) {
        components.push({ name: m[1].trim(), amount: parseFloat(m[2]) })
      }
    }
  }

  // Extract params: 反応器[加熱,200℃]
  const paramMatch = name.match(/^(.+?)\[(.+?)\]$/)
  if (paramMatch) {
    name = paramMatch[1].trim()
    params = paramMatch[2].trim()
  }

  return { name, params, components }
}

export function parseText(text: string): ProcessData {
  resetParser()
  const steps: ProcessStep[] = []
  const streams: StreamData[] = []
  const connections: ProcessConnection[] = []
  const stepMap = new Map<string, string>() // name -> step id

  function getOrCreateStep(parsed: ParsedNode): string {
    if (stepMap.has(parsed.name)) {
      return stepMap.get(parsed.name)!
    }
    const id = nextId('step')
    const step: ProcessStep = {
      id,
      name: parsed.name,
      type: guessType(parsed.name),
      params: parsed.params,
      inputStreams: [],
      outputStreams: [],
    }
    steps.push(step)
    stepMap.set(parsed.name, id)
    return id
  }

  const lines = text.split('\n').filter(l => l.trim())

  for (const line of lines) {
    // Split by ->
    const parts = line.split('->').map(s => s.trim()).filter(Boolean)
    if (parts.length < 2) continue

    for (let i = 0; i < parts.length - 1; i++) {
      const fromParsed = parseNode(parts[i])
      const toParsed = parseNode(parts[i + 1])

      const fromId = getOrCreateStep(fromParsed)
      const toId = getOrCreateStep(toParsed)

      const streamId = nextId('stream')
      const stream: StreamData = {
        id: streamId,
        label: `S${streams.length + 1}`,
        components: fromParsed.components.map(c => ({
          name: c.name,
          flowRate: c.amount,
          unit: 'kg/h',
        })),
        temperature: 25,
        pressure: 1,
        specificHeat: 4.18,
        reactionHeat: 0,
      }
      streams.push(stream)

      // Update step streams
      const fromStep = steps.find(s => s.id === fromId)!
      const toStep = steps.find(s => s.id === toId)!
      fromStep.outputStreams.push(streamId)
      toStep.inputStreams.push(streamId)

      connections.push({ fromStepId: fromId, toStepId: toId, streamId })
    }
  }

  return { steps, streams, connections }
}
