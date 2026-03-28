import { useEffect, useRef, useCallback } from 'react'
import mermaid from 'mermaid'

interface Props {
  code: string
  svgRef: React.RefObject<SVGSVGElement | null>
}

mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true,
    curve: 'basis',
  },
  securityLevel: 'loose',
})

export function MermaidPreview({ code, svgRef }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)

  const render = useCallback(async () => {
    if (!containerRef.current || !code.trim()) {
      if (containerRef.current) {
        containerRef.current.innerHTML = '<p class="placeholder">フロー図がここに表示されます</p>'
      }
      return
    }

    try {
      const id = `mermaid-${Date.now()}`
      const { svg } = await mermaid.render(id, code)
      containerRef.current.innerHTML = svg

      const svgEl = containerRef.current.querySelector('svg')
      if (svgEl && svgRef.current !== svgEl) {
        (svgRef as React.MutableRefObject<SVGSVGElement | null>).current = svgEl
      }
    } catch (e) {
      containerRef.current.innerHTML = `<p class="error">Mermaid描画エラー: ${(e as Error).message}</p>`
    }
  }, [code, svgRef])

  useEffect(() => {
    render()
  }, [render])

  return (
    <div className="mermaid-preview">
      <h3>プロセスフロー図</h3>
      <div ref={containerRef} className="mermaid-container" />
    </div>
  )
}
