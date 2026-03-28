import type { MaterialBalanceResult } from '../types'

interface Props {
  results: MaterialBalanceResult[]
}

export function MaterialBalance({ results }: Props) {
  if (results.length === 0) {
    return <div className="empty-message">フロー図を作成するとマテリアルバランスが表示されます。</div>
  }

  const hasAnyComponents = results.some(r => r.componentDetails.length > 0)

  return (
    <div className="balance-table">
      <h3>マテリアルバランス（物質収支）</h3>

      <table>
        <thead>
          <tr>
            <th>ユニット</th>
            <th>入力合計 (kg/h)</th>
            <th>出力合計 (kg/h)</th>
            <th>差分 (kg/h)</th>
            <th>状態</th>
          </tr>
        </thead>
        <tbody>
          {results.map(r => (
            <tr key={r.stepId} className={r.balanced ? '' : 'warning-row'}>
              <td>{r.stepName}</td>
              <td>{r.inputTotal.toFixed(2)}</td>
              <td>{r.outputTotal.toFixed(2)}</td>
              <td>{r.difference.toFixed(2)}</td>
              <td>
                <span className={`badge ${r.balanced ? 'badge-ok' : 'badge-ng'}`}>
                  {r.balanced ? 'OK' : 'NG'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {hasAnyComponents && (
        <>
          <h4>成分別詳細</h4>
          {results.filter(r => r.componentDetails.length > 0).map(r => (
            <div key={r.stepId} className="component-detail">
              <h5>{r.stepName}</h5>
              <table>
                <thead>
                  <tr>
                    <th>成分</th>
                    <th>入力 (kg/h)</th>
                    <th>出力 (kg/h)</th>
                    <th>差分 (kg/h)</th>
                  </tr>
                </thead>
                <tbody>
                  {r.componentDetails.map(d => (
                    <tr key={d.component} className={Math.abs(d.diff) > 0.01 ? 'warning-row' : ''}>
                      <td>{d.component}</td>
                      <td>{d.input.toFixed(2)}</td>
                      <td>{d.output.toFixed(2)}</td>
                      <td>{d.diff.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </>
      )}
    </div>
  )
}
