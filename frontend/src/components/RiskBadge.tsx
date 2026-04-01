interface Props {
  level: 'high' | 'medium' | 'low'
}

const LABELS: Record<Props['level'], string> = {
  high: 'High Risk',
  medium: 'Medium Risk',
  low: 'Low Risk',
}

export function RiskBadge({ level }: Props) {
  return (
    <span className={`risk-badge risk-badge--${level}`} aria-label={`Risk level: ${level}`}>
      {LABELS[level]}
    </span>
  )
}
