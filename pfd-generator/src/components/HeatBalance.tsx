import type { HeatBalanceResult } from '../types'

interface Props {
  results: HeatBalanceResult[]
}

export function HeatBalance({ results }: Props) {
  if (results.length === 0) {
    return <div className="empty-message">フロー図を作成するとヒートバランスが表示されます。</div>
  }

  return (
    <div className="balance-table">
      <h3>ヒートバランス（熱収支）</h3>
      <p className="formula-note">Q = m x Cp x T（基準温度: 0°C）</p>

      <table>
        <thead>
          <tr>
            <th>ユニット</th>
            <th>入熱 (kJ/h)</th>
            <th>出熱 (kJ/h)</th>
            <th>反応熱 (kJ/h)</th>
            <th>必要熱量 (kJ/h)</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {results.map(r => (
            <tr key={r.stepId}>
              <td>{r.stepName}</td>
              <td>{r.inputHeat.toFixed(1)}</td>
              <td>{r.outputHeat.toFixed(1)}</td>
              <td>{r.reactionHeat.toFixed(1)}</td>
              <td className={r.requiredHeat > 0 ? 'heat-positive' : r.requiredHeat < 0 ? 'heat-negative' : ''}>
                {r.requiredHeat.toFixed(1)}
              </td>
              <td>
                {r.requiredHeat > 0 ? '加熱' : r.requiredHeat < 0 ? '冷却' : '-'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="heat-summary">
        <div>
          <strong>総必要加熱量:</strong>{' '}
          {results.filter(r => r.requiredHeat > 0).reduce((s, r) => s + r.requiredHeat, 0).toFixed(1)} kJ/h
        </div>
        <div>
          <strong>総必要冷却量:</strong>{' '}
          {Math.abs(results.filter(r => r.requiredHeat < 0).reduce((s, r) => s + r.requiredHeat, 0)).toFixed(1)} kJ/h
        </div>
      </div>
    </div>
  )
}
