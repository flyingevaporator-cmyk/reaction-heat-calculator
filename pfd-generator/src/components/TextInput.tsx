import { useState } from 'react'

interface Props {
  value: string
  onChange: (text: string) => void
}

const EXAMPLES = [
  '原料(水:100, NaOH:50) -> 反応器[加熱,80℃] -> 蒸留塔[減圧] -> 製品タンク\n蒸留塔 -> 残渣タンク',
  '原料A -> 混合器 -> 反応器[触媒反応,150℃] -> 分離器 -> 製品\n原料B -> 混合器\n分離器 -> 廃棄物',
  'メタノール(メタノール:200) -> 熱交換器[予熱,60℃] -> 反応器[酸化反応,250℃] -> 蒸留塔 -> ホルムアルデヒド\n蒸留塔 -> 廃水処理',
]

export function TextInput({ value, onChange }: Props) {
  const [showHelp, setShowHelp] = useState(false)

  return (
    <div className="text-input-panel">
      <div className="panel-header">
        <h3>テキスト入力</h3>
        <button className="btn-small" onClick={() => setShowHelp(!showHelp)}>
          {showHelp ? '閉じる' : '記法ヘルプ'}
        </button>
      </div>

      {showHelp && (
        <div className="help-box">
          <h4>記法ガイド</h4>
          <ul>
            <li><code>ユニット名 -&gt; ユニット名</code> で接続</li>
            <li><code>ユニット名[条件]</code> でパラメータ指定</li>
            <li><code>ユニット名(成分:流量, 成分:流量)</code> で組成指定</li>
            <li>改行で複数経路（分岐・合流）を定義</li>
            <li>同じユニット名は自動的に同一ノードとして扱います</li>
          </ul>
          <h4>自動認識されるユニット名</h4>
          <p>原料, 反応器, 蒸留塔, 混合器, 熱交換器, ポンプ, タンク, フィルター, 乾燥機, 圧縮機, 分離器, 製品, 廃棄物</p>
        </div>
      )}

      <textarea
        className="text-area"
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder="原料(水:100, NaOH:50) -> 反応器[加熱,80℃] -> 蒸留塔 -> 製品タンク"
        rows={8}
      />

      <div className="examples">
        <span>サンプル:</span>
        {EXAMPLES.map((ex, i) => (
          <button key={i} className="btn-small" onClick={() => onChange(ex)}>
            例{i + 1}
          </button>
        ))}
      </div>
    </div>
  )
}
