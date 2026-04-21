import type { HeaderAnalysis } from '../types'
import { RiskBadge } from './RiskBadge'

interface Props {
  result: HeaderAnalysis | null
}

type AuthStatus = string | null

function authBadgeClass(status: AuthStatus): string {
  if (status === 'pass') return 'auth-badge auth-badge--pass'
  if (status === 'fail' || status === 'softfail') return 'auth-badge auth-badge--fail'
  return 'auth-badge auth-badge--unknown'
}

function authLabel(status: AuthStatus): string {
  return status ?? 'unknown'
}

export function HeaderAnalysisCard({ result }: Props) {
  if (!result) {
    return (
      <div className="result-card result-card--disabled">
        <h2 className="result-card__title">Header Analysis</h2>
        <p className="disabled-text">
          Paste raw email headers above to enable SPF/DKIM/DMARC analysis.
        </p>
      </div>
    )
  }

  return (
    <div className="result-card">
      <h2 className="result-card__title">Header Analysis</h2>

      <div className="auth-row">
        <span className="auth-row__item">
          <span className="auth-row__label">SPF</span>
          <span className={authBadgeClass(result.spf)}>{authLabel(result.spf)}</span>
        </span>
        <span className="auth-row__item">
          <span className="auth-row__label">DKIM</span>
          <span className={authBadgeClass(result.dkim)}>{authLabel(result.dkim)}</span>
        </span>
        <span className="auth-row__item">
          <span className="auth-row__label">DMARC</span>
          <span className={authBadgeClass(result.dmarc)}>{authLabel(result.dmarc)}</span>
        </span>
      </div>

      {(result.from_domain || result.reply_to_domain || result.return_path_domain) && (
        <div className="domain-chain">
          <h3 className="domain-chain__heading">Domain Chain</h3>
          <dl className="domain-chain__list">
            {result.from_domain && (
              <>
                <dt className="domain-chain__term">From</dt>
                <dd className="domain-chain__detail">{result.from_domain}</dd>
              </>
            )}
            {result.reply_to_domain && (
              <>
                <dt className="domain-chain__term">Reply-To</dt>
                <dd className="domain-chain__detail">{result.reply_to_domain}</dd>
              </>
            )}
            {result.return_path_domain && (
              <>
                <dt className="domain-chain__term">Return-Path</dt>
                <dd className="domain-chain__detail">{result.return_path_domain}</dd>
              </>
            )}
          </dl>
        </div>
      )}

      {result.flags.length > 0 && (
        <div className="iocs">
          <h3 className="iocs__heading">Header Flags</h3>
          <ul className="iocs__list">
            {result.flags.map((flag) => (
              <li key={flag.name} className="iocs__item header-flag">
                <RiskBadge level={flag.severity} />
                <span className="header-flag__description">{flag.description}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
