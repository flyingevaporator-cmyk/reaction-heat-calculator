import type { MaterialBalanceResult, HeatBalanceResult } from '../types'
import {
  exportMermaidCode,
  exportSVG,
  exportPNG,
  exportPDF,
  exportMaterialBalanceCSV,
  exportHeatBalanceCSV,
} from '../exportUtils'

interface Props {
  mermaidCode: string
  svgRef: React.RefObject<SVGSVGElement | null>
  materialResults: MaterialBalanceResult[]
  heatResults: HeatBalanceResult[]
}

export function ExportPanel({ mermaidCode, svgRef, materialResults, heatResults }: Props) {
  return (
    <div className="export-panel">
      <h3>エクスポート</h3>
      <div className="export-buttons">
        <div className="export-group">
          <h4>フロー図</h4>
          <button className="btn-export" onClick={() => exportPNG(svgRef.current)} disabled={!mermaidCode}>
            PNG
          </button>
          <button className="btn-export" onClick={() => exportSVG(svgRef.current)} disabled={!mermaidCode}>
            SVG
          </button>
          <button className="btn-export" onClick={() => exportPDF(svgRef.current)} disabled={!mermaidCode}>
            PDF
          </button>
          <button className="btn-export" onClick={() => exportMermaidCode(mermaidCode)} disabled={!mermaidCode}>
            Mermaid (.md)
          </button>
        </div>

        <div className="export-group">
          <h4>バランス計算</h4>
          <button
            className="btn-export"
            onClick={() => exportMaterialBalanceCSV(materialResults)}
            disabled={materialResults.length === 0}
          >
            マテバラ CSV
          </button>
          <button
            className="btn-export"
            onClick={() => exportHeatBalanceCSV(heatResults)}
            disabled={heatResults.length === 0}
          >
            ヒートバランス CSV
          </button>
        </div>
      </div>
    </div>
  )
}
