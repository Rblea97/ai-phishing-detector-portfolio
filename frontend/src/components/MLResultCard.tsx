import type { MLResult } from '../types'
import { RiskBadge } from './RiskBadge'

interface Props {
  result: MLResult
}

export function MLResultCard({ result }: Props) {
  const pct = Math.round(result.score * 100)

  return (
    <div className="result-card">
      <h2 className="result-card__title">ML Baseline</h2>

      <div className="score-row">
        <RiskBadge level={result.risk_level} />
        <span className="score-value">{pct}%</span>
      </div>

      <div className="score-bar" aria-label={`Phishing probability: ${pct}%`}>
        <div
          className={`score-bar__fill score-bar__fill--${result.risk_level}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="score-label">Phishing probability</p>

      {result.top_features.length > 0 && (
        <div className="features">
          <h3 className="features__heading">Top signals</h3>
          <ul className="features__list">
            {result.top_features.slice(0, 8).map((f) => (
              <li key={f.token} className="features__item">
                <code className="features__token">{f.token}</code>
                <span className="features__weight">{f.weight.toFixed(2)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
