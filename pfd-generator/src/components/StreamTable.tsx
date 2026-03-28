import type { ProcessData, StreamComponent } from '../types'

interface Props {
  data: ProcessData
  onUpdate: (data: ProcessData) => void
}

export function StreamTable({ data, onUpdate }: Props) {
  const updateStream = (streamIdx: number, field: string, value: number) => {
    const streams = [...data.streams]
    streams[streamIdx] = { ...streams[streamIdx], [field]: value }
    onUpdate({ ...data, streams })
  }

  const updateComponent = (streamIdx: number, compIdx: number, field: keyof StreamComponent, value: string | number) => {
    const streams = [...data.streams]
    const components = [...streams[streamIdx].components]
    components[compIdx] = { ...components[compIdx], [field]: value }
    streams[streamIdx] = { ...streams[streamIdx], components }
    onUpdate({ ...data, streams })
  }

  const addComponent = (streamIdx: number) => {
    const streams = [...data.streams]
    streams[streamIdx] = {
      ...streams[streamIdx],
      components: [...streams[streamIdx].components, { name: '', flowRate: 0, unit: 'kg/h' }],
    }
    onUpdate({ ...data, streams })
  }

  const removeComponent = (streamIdx: number, compIdx: number) => {
    const streams = [...data.streams]
    const components = streams[streamIdx].components.filter((_, i) => i !== compIdx)
    streams[streamIdx] = { ...streams[streamIdx], components }
    onUpdate({ ...data, streams })
  }

  if (data.streams.length === 0) {
    return <div className="empty-message">ストリームがありません。フロー図を作成してください。</div>
  }

  return (
    <div className="stream-table">
      <h3>ストリーム詳細</h3>
      <div className="streams-grid">
        {data.streams.map((stream, sIdx) => {
          const fromConn = data.connections.find(c => c.streamId === stream.id)
          const fromStep = fromConn ? data.steps.find(s => s.id === fromConn.fromStepId) : null
          const toStep = fromConn ? data.steps.find(s => s.id === fromConn.toStepId) : null

          return (
            <div key={stream.id} className="stream-card">
              <div className="stream-header">
                <strong>{stream.label}</strong>
                <span className="stream-route">
                  {fromStep?.name || '?'} → {toStep?.name || '?'}
                </span>
              </div>

              <div className="stream-props">
                <label>
                  温度 (°C)
                  <input
                    type="number"
                    value={stream.temperature}
                    onChange={e => updateStream(sIdx, 'temperature', parseFloat(e.target.value) || 0)}
                    className="input-sm"
                  />
                </label>
                <label>
                  圧力 (atm)
                  <input
                    type="number"
                    value={stream.pressure}
                    step="0.1"
                    onChange={e => updateStream(sIdx, 'pressure', parseFloat(e.target.value) || 0)}
                    className="input-sm"
                  />
                </label>
                <label>
                  比熱 (kJ/kg°C)
                  <input
                    type="number"
                    value={stream.specificHeat}
                    step="0.01"
                    onChange={e => updateStream(sIdx, 'specificHeat', parseFloat(e.target.value) || 0)}
                    className="input-sm"
                  />
                </label>
                <label>
                  反応熱 (kJ/h)
                  <input
                    type="number"
                    value={stream.reactionHeat}
                    onChange={e => updateStream(sIdx, 'reactionHeat', parseFloat(e.target.value) || 0)}
                    className="input-sm"
                  />
                </label>
              </div>

              <div className="components-section">
                <div className="components-header">
                  <span>成分</span>
                  <button className="btn-small" onClick={() => addComponent(sIdx)}>+ 成分追加</button>
                </div>
                {stream.components.map((comp, cIdx) => (
                  <div key={cIdx} className="component-row">
                    <input
                      type="text"
                      placeholder="成分名"
                      value={comp.name}
                      onChange={e => updateComponent(sIdx, cIdx, 'name', e.target.value)}
                      className="input-sm"
                    />
                    <input
                      type="number"
                      placeholder="流量"
                      value={comp.flowRate}
                      onChange={e => updateComponent(sIdx, cIdx, 'flowRate', parseFloat(e.target.value) || 0)}
                      className="input-sm"
                    />
                    <span className="unit">kg/h</span>
                    <button className="btn-small btn-danger" onClick={() => removeComponent(sIdx, cIdx)}>×</button>
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
