import type { ProcessData, ProcessStep, UnitType } from '../types'
import { UNIT_TYPE_LABELS } from '../types'

interface Props {
  data: ProcessData
  onUpdate: (data: ProcessData) => void
}

let formIdCounter = 100

export function FormInput({ data, onUpdate }: Props) {
  const addStep = () => {
    const id = `step_f${++formIdCounter}`
    const newStep: ProcessStep = {
      id,
      name: '',
      type: 'custom',
      params: '',
      inputStreams: [],
      outputStreams: [],
    }
    onUpdate({ ...data, steps: [...data.steps, newStep] })
  }

  const updateStep = (index: number, field: keyof ProcessStep, value: string) => {
    const steps = [...data.steps]
    steps[index] = { ...steps[index], [field]: value }
    onUpdate({ ...data, steps })
  }

  const removeStep = (index: number) => {
    const stepId = data.steps[index].id
    const steps = data.steps.filter((_, i) => i !== index)
    const connections = data.connections.filter(
      c => c.fromStepId !== stepId && c.toStepId !== stepId
    )
    const usedStreamIds = new Set(connections.map(c => c.streamId))
    const streams = data.streams.filter(s => usedStreamIds.has(s.id))
    onUpdate({ steps, streams, connections })
  }

  const addConnection = (fromIdx: number, toIdx: number) => {
    if (fromIdx === toIdx || fromIdx < 0 || toIdx < 0) return
    const fromStep = data.steps[fromIdx]
    const toStep = data.steps[toIdx]

    const exists = data.connections.some(
      c => c.fromStepId === fromStep.id && c.toStepId === toStep.id
    )
    if (exists) return

    const streamId = `stream_f${++formIdCounter}`
    const stream = {
      id: streamId,
      label: `S${data.streams.length + 1}`,
      components: [],
      temperature: 25,
      pressure: 1,
      specificHeat: 4.18,
      reactionHeat: 0,
    }

    const steps = [...data.steps]
    steps[fromIdx] = { ...steps[fromIdx], outputStreams: [...steps[fromIdx].outputStreams, streamId] }
    steps[toIdx] = { ...steps[toIdx], inputStreams: [...steps[toIdx].inputStreams, streamId] }

    onUpdate({
      steps,
      streams: [...data.streams, stream],
      connections: [...data.connections, { fromStepId: fromStep.id, toStepId: toStep.id, streamId }],
    })
  }

  const removeConnection = (connIdx: number) => {
    const conn = data.connections[connIdx]
    const connections = data.connections.filter((_, i) => i !== connIdx)
    const streams = data.streams.filter(s => s.id !== conn.streamId)

    const steps = data.steps.map(step => ({
      ...step,
      inputStreams: step.inputStreams.filter(id => id !== conn.streamId),
      outputStreams: step.outputStreams.filter(id => id !== conn.streamId),
    }))

    onUpdate({ steps, streams, connections })
  }

  return (
    <div className="form-input-panel">
      <div className="panel-header">
        <h3>フォーム入力</h3>
        <button className="btn-primary" onClick={addStep}>+ ステップ追加</button>
      </div>

      <div className="steps-list">
        {data.steps.map((step, idx) => (
          <div key={step.id} className="step-card">
            <div className="step-row">
              <input
                type="text"
                placeholder="ステップ名"
                value={step.name}
                onChange={e => updateStep(idx, 'name', e.target.value)}
                className="input"
              />
              <select
                value={step.type}
                onChange={e => updateStep(idx, 'type', e.target.value as UnitType)}
                className="select"
              >
                {Object.entries(UNIT_TYPE_LABELS).map(([val, label]) => (
                  <option key={val} value={val}>{label}</option>
                ))}
              </select>
              <input
                type="text"
                placeholder="条件 (例: 加熱,200℃)"
                value={step.params}
                onChange={e => updateStep(idx, 'params', e.target.value)}
                className="input"
              />
              <button className="btn-danger" onClick={() => removeStep(idx)}>削除</button>
            </div>
          </div>
        ))}
      </div>

      {data.steps.length >= 2 && (
        <div className="connections-section">
          <h4>接続の追加</h4>
          <div className="connection-add">
            <select id="conn-from" className="select">
              {data.steps.map((s, i) => (
                <option key={s.id} value={i}>{s.name || `ステップ${i + 1}`}</option>
              ))}
            </select>
            <span className="arrow">→</span>
            <select id="conn-to" className="select">
              {data.steps.map((s, i) => (
                <option key={s.id} value={i}>{s.name || `ステップ${i + 1}`}</option>
              ))}
            </select>
            <button
              className="btn-primary"
              onClick={() => {
                const from = parseInt((document.getElementById('conn-from') as HTMLSelectElement).value)
                const to = parseInt((document.getElementById('conn-to') as HTMLSelectElement).value)
                addConnection(from, to)
              }}
            >
              接続
            </button>
          </div>

          {data.connections.length > 0 && (
            <div className="connections-list">
              {data.connections.map((conn, i) => {
                const from = data.steps.find(s => s.id === conn.fromStepId)
                const to = data.steps.find(s => s.id === conn.toStepId)
                return (
                  <div key={i} className="connection-item">
                    <span>{from?.name || '?'} → {to?.name || '?'}</span>
                    <button className="btn-small btn-danger" onClick={() => removeConnection(i)}>×</button>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
