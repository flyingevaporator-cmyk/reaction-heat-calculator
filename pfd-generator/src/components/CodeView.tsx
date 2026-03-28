import { useState } from 'react'

interface Props {
  code: string
}

export function CodeView({ code }: Props) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="code-view">
      <div className="panel-header">
        <h3>Mermaidコード</h3>
        <button className="btn-small" onClick={handleCopy}>
          {copied ? 'コピー済み!' : 'コピー'}
        </button>
      </div>
      <pre className="code-block">{code || '// テキストまたはフォームから入力してください'}</pre>
    </div>
  )
}
