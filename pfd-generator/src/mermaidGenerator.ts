import type { ProcessData } from './types'
import { getEquipmentIconUri } from './equipmentIcons'

function sanitizeId(id: string): string {
  return id.replace(/[^a-zA-Z0-9_]/g, '_')
}

function escapeLabel(text: string): string {
  return text.replace(/"/g, '#quot;')
}

export function generateMermaid(data: ProcessData, showStreamInfo = true): string {
  if (data.steps.length === 0) return ''

  const lines: string[] = ['graph LR']

  // Define nodes with equipment icon images
  for (const step of data.steps) {
    const iconUri = getEquipmentIconUri(step.type)
    let nameText = step.name
    if (step.params) {
      nameText += `<br/><span style='font-size:10px;color:#555'>${step.params}</span>`
    }
    const html = `<div style='text-align:center;padding:2px'><img src='${iconUri}' width='60' height='60' /><br/><b style='font-size:12px'>${nameText}</b></div>`
    lines.push(`    ${sanitizeId(step.id)}["${escapeLabel(html)}"]`)
  }

  lines.push('')

  // Define connections
  for (const conn of data.connections) {
    const stream = data.streams.find(s => s.id === conn.streamId)
    const fromId = sanitizeId(conn.fromStepId)
    const toId = sanitizeId(conn.toStepId)

    if (stream && showStreamInfo) {
      const totalFlow = stream.components.reduce((sum, c) => sum + c.flowRate, 0)
      let linkLabel = stream.label
      if (totalFlow > 0) {
        linkLabel += ` ${totalFlow}kg/h`
      }
      lines.push(`    ${fromId} -->|"${escapeLabel(linkLabel)}"| ${toId}`)
    } else {
      lines.push(`    ${fromId} --> ${toId}`)
    }
  }

  // Style: clean background for nodes
  lines.push('')
  lines.push('    classDef default fill:#fafafa,stroke:#ddd,stroke-width:1px,color:#333')

  return lines.join('\n')
}
