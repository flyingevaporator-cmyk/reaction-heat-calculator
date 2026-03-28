import { useState, useRef, useMemo } from 'react'
import type { ProcessData } from './types'
import { parseText } from './parser'
import { generateMermaid } from './mermaidGenerator'
import { calcMaterialBalance, calcHeatBalance } from './balanceCalc'
import { TextInput } from './components/TextInput'
import { FormInput } from './components/FormInput'
import { MermaidPreview } from './components/MermaidPreview'
import { CodeView } from './components/CodeView'
import { StreamTable } from './components/StreamTable'
import { MaterialBalance } from './components/MaterialBalance'
import { HeatBalance } from './components/HeatBalance'
import { ExportPanel } from './components/ExportPanel'

type InputMode = 'text' | 'form'
type MainTab = 'flow' | 'material' | 'heat'

const EMPTY_DATA: ProcessData = { steps: [], streams: [], connections: [] }

export function App() {
  const [inputMode, setInputMode] = useState<InputMode>('text')
  const [mainTab, setMainTab] = useState<MainTab>('flow')
  const [textValue, setTextValue] = useState('')
  const [formData, setFormData] = useState<ProcessData>(EMPTY_DATA)
  const svgRef = useRef<SVGSVGElement | null>(null)

  // Current process data based on input mode
  const processData = useMemo(() => {
    if (inputMode === 'text') {
      return textValue.trim() ? parseText(textValue) : EMPTY_DATA
    }
    return formData
  }, [inputMode, textValue, formData])

  // Generate mermaid code
  const mermaidCode = useMemo(() => generateMermaid(processData), [processData])

  // Calculate balances
  const materialResults = useMemo(() => calcMaterialBalance(processData), [processData])
  const heatResults = useMemo(() => calcHeatBalance(processData), [processData])

  // For stream table - update the active data source
  const handleStreamUpdate = (updated: ProcessData) => {
    if (inputMode === 'form') {
      setFormData(updated)
    }
    // In text mode, stream edits update a separate overlay
    // For simplicity, we show stream table only in form mode
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>PFD Generator</h1>
        <p>プロセスフロー図 + マテリアルバランス + ヒートバランス</p>
      </header>

      <div className="app-layout">
        {/* Left panel - Input */}
        <div className="input-panel">
          <div className="mode-tabs">
            <button
              className={`tab ${inputMode === 'text' ? 'active' : ''}`}
              onClick={() => setInputMode('text')}
            >
              テキスト入力
            </button>
            <button
              className={`tab ${inputMode === 'form' ? 'active' : ''}`}
              onClick={() => setInputMode('form')}
            >
              フォーム入力
            </button>
          </div>

          {inputMode === 'text' ? (
            <TextInput value={textValue} onChange={setTextValue} />
          ) : (
            <FormInput data={formData} onUpdate={setFormData} />
          )}

          <CodeView code={mermaidCode} />

          <ExportPanel
            mermaidCode={mermaidCode}
            svgRef={svgRef}
            materialResults={materialResults}
            heatResults={heatResults}
          />
        </div>

        {/* Right panel - Output */}
        <div className="output-panel">
          <div className="main-tabs">
            <button
              className={`tab ${mainTab === 'flow' ? 'active' : ''}`}
              onClick={() => setMainTab('flow')}
            >
              フロー図
            </button>
            <button
              className={`tab ${mainTab === 'material' ? 'active' : ''}`}
              onClick={() => setMainTab('material')}
            >
              マテリアルバランス
            </button>
            <button
              className={`tab ${mainTab === 'heat' ? 'active' : ''}`}
              onClick={() => setMainTab('heat')}
            >
              ヒートバランス
            </button>
          </div>

          {mainTab === 'flow' && (
            <>
              <MermaidPreview code={mermaidCode} svgRef={svgRef} />
              {inputMode === 'form' && (
                <StreamTable data={processData} onUpdate={handleStreamUpdate} />
              )}
              {inputMode === 'text' && processData.streams.length > 0 && (
                <div className="stream-info">
                  <h4>ストリーム一覧</h4>
                  <table>
                    <thead>
                      <tr>
                        <th>No.</th>
                        <th>経路</th>
                        <th>成分</th>
                        <th>流量合計</th>
                      </tr>
                    </thead>
                    <tbody>
                      {processData.streams.map(s => {
                        const conn = processData.connections.find(c => c.streamId === s.id)
                        const from = conn ? processData.steps.find(st => st.id === conn.fromStepId) : null
                        const to = conn ? processData.steps.find(st => st.id === conn.toStepId) : null
                        const total = s.components.reduce((sum, c) => sum + c.flowRate, 0)
                        return (
                          <tr key={s.id}>
                            <td>{s.label}</td>
                            <td>{from?.name} → {to?.name}</td>
                            <td>{s.components.map(c => `${c.name}: ${c.flowRate}`).join(', ') || '-'}</td>
                            <td>{total > 0 ? `${total} kg/h` : '-'}</td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}

          {mainTab === 'material' && <MaterialBalance results={materialResults} />}
          {mainTab === 'heat' && <HeatBalance results={heatResults} />}
        </div>
      </div>
    </div>
  )
}
