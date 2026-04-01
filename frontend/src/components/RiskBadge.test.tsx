import { render, screen } from '@testing-library/react'
import { RiskBadge } from './RiskBadge'

describe('RiskBadge', () => {
  it('renders "High Risk" for high level', () => {
    render(<RiskBadge level="high" />)
    expect(screen.getByText('High Risk')).toBeInTheDocument()
  })

  it('renders "Medium Risk" for medium level', () => {
    render(<RiskBadge level="medium" />)
    expect(screen.getByText('Medium Risk')).toBeInTheDocument()
  })

  it('renders "Low Risk" for low level', () => {
    render(<RiskBadge level="low" />)
    expect(screen.getByText('Low Risk')).toBeInTheDocument()
  })

  it('applies the correct CSS modifier class', () => {
    const { container } = render(<RiskBadge level="high" />)
    expect(container.firstChild).toHaveClass('risk-badge--high')
  })

  it('has an aria-label describing the risk level', () => {
    render(<RiskBadge level="medium" />)
    expect(screen.getByLabelText('Risk level: medium')).toBeInTheDocument()
  })
})
