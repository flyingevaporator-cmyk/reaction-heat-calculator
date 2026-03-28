import type { MaterialBalanceResult, HeatBalanceResult } from './types'

export function downloadFile(content: string, filename: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export function exportMermaidCode(code: string) {
  downloadFile(code, 'pfd-diagram.md', 'text/markdown')
}

export function exportSVG(svgElement: SVGElement | null) {
  if (!svgElement) return
  const svgData = new XMLSerializer().serializeToString(svgElement)
  downloadFile(svgData, 'pfd-diagram.svg', 'image/svg+xml')
}

export async function exportPNG(svgElement: SVGElement | null) {
  if (!svgElement) return

  const svgData = new XMLSerializer().serializeToString(svgElement)
  const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(svgBlob)

  const img = new Image()
  img.onload = () => {
    const scale = 2
    const canvas = document.createElement('canvas')
    canvas.width = img.width * scale
    canvas.height = img.height * scale
    const ctx = canvas.getContext('2d')!
    ctx.scale(scale, scale)
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, img.width, img.height)
    ctx.drawImage(img, 0, 0)

    canvas.toBlob(blob => {
      if (blob) {
        const a = document.createElement('a')
        a.href = URL.createObjectURL(blob)
        a.download = 'pfd-diagram.png'
        a.click()
      }
    }, 'image/png')

    URL.revokeObjectURL(url)
  }
  img.src = url
}

export async function exportPDF(svgElement: SVGElement | null) {
  if (!svgElement) return

  const { jsPDF } = await import('jspdf')

  const svgData = new XMLSerializer().serializeToString(svgElement)
  const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
  const url = URL.createObjectURL(svgBlob)

  const img = new Image()
  img.onload = () => {
    const scale = 2
    const canvas = document.createElement('canvas')
    canvas.width = img.width * scale
    canvas.height = img.height * scale
    const ctx = canvas.getContext('2d')!
    ctx.scale(scale, scale)
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, img.width, img.height)
    ctx.drawImage(img, 0, 0)

    const imgData = canvas.toDataURL('image/png')
    const orientation = img.width > img.height ? 'landscape' : 'portrait'
    const pdf = new jsPDF({ orientation, unit: 'px', format: [img.width, img.height] })
    pdf.addImage(imgData, 'PNG', 0, 0, img.width, img.height)
    pdf.save('pfd-diagram.pdf')

    URL.revokeObjectURL(url)
  }
  img.src = url
}

export function exportMaterialBalanceCSV(results: MaterialBalanceResult[]) {
  const headers = ['ユニット', '入力合計 (kg/h)', '出力合計 (kg/h)', '差分 (kg/h)', 'バランス']
  const rows = results.map(r => [
    r.stepName,
    r.inputTotal.toFixed(2),
    r.outputTotal.toFixed(2),
    r.difference.toFixed(2),
    r.balanced ? 'OK' : 'NG',
  ])
  const bom = '\uFEFF'
  const csv = bom + [headers, ...rows].map(r => r.join(',')).join('\n')
  downloadFile(csv, 'material-balance.csv', 'text/csv')
}

export function exportHeatBalanceCSV(results: HeatBalanceResult[]) {
  const headers = ['ユニット', '入熱 (kJ/h)', '出熱 (kJ/h)', '反応熱 (kJ/h)', '必要熱量 (kJ/h)']
  const rows = results.map(r => [
    r.stepName,
    r.inputHeat.toFixed(2),
    r.outputHeat.toFixed(2),
    r.reactionHeat.toFixed(2),
    r.requiredHeat.toFixed(2),
  ])
  const bom = '\uFEFF'
  const csv = bom + [headers, ...rows].map(r => r.join(',')).join('\n')
  downloadFile(csv, 'heat-balance.csv', 'text/csv')
}
