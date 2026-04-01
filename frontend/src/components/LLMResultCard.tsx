import type { LLMResult } from '../types'
import { RiskBadge } from './RiskBadge'

interface Props {
  result: LLMResult | null
  loading: boolean
}

export function LLMResultCard({ result, loading }: Props) {
  if (loading) {
    return (
      <div className="result-card result-card--loading">
        <h2 className="result-card__title">Claude Analysis</h2>
        <p className="loading-text">Analyzing with Claude…</p>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="result-card result-card--disabled">
        <h2 className="result-card__title">Claude Analysis</h2>
        <p className="disabled-text">
          Set <code>ANTHROPIC_API_KEY</code> in the backend to enable LLM analysis.
        </p>
      </div>
    )
  }

  return (
    <div className="result-card">
      <h2 className="result-card__title">Claude Analysis</h2>

      <div className="score-row">
        <RiskBadge level={result.risk_level} />
      </div>

      <p className="reasoning">{result.reasoning}</p>

      {result.iocs.length > 0 && (
        <div className="iocs">
          <h3 className="iocs__heading">Indicators of Compromise</h3>
          <ul className="iocs__list">
            {result.iocs.map((ioc) => (
              <li key={ioc} className="iocs__item">
                {ioc}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
