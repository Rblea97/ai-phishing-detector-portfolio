import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'

// fetchSamples is called on mount — silence it in all tests
beforeEach(() => {
  vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify([]), { status: 200 }))
})

afterEach(() => {
  vi.restoreAllMocks()
})

it('renders the app title', async () => {
  render(<App />)
  await act(async () => {})
  expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('AI Phishing Detector')
})

it('renders subject and body inputs', async () => {
  render(<App />)
  await act(async () => {})
  expect(screen.getByLabelText('Subject')).toBeInTheDocument()
  expect(screen.getByLabelText('Body')).toBeInTheDocument()
})

it('analyze button is disabled when inputs are empty', async () => {
  render(<App />)
  await act(async () => {})
  expect(screen.getByRole('button', { name: 'Analyze' })).toBeDisabled()
})

it('analyze button enables when subject is filled', async () => {
  const user = userEvent.setup()
  render(<App />)
  await user.type(screen.getByLabelText('Subject'), 'Verify your account')
  expect(screen.getByRole('button', { name: 'Analyze' })).toBeEnabled()
})

it('shows results after successful analysis', async () => {
  const user = userEvent.setup()
  const mockResponse = {
    ml: { score: 0.92, risk_level: 'high', top_features: [{ token: 'verify', weight: 1.5 }] },
    llm: null,
  }
  vi.spyOn(globalThis, 'fetch')
    .mockResolvedValueOnce(new Response(JSON.stringify([]), { status: 200 })) // samples
    .mockResolvedValueOnce(new Response(JSON.stringify(mockResponse), { status: 200 })) // analyze

  render(<App />)
  await user.type(screen.getByLabelText('Subject'), 'Verify your account')
  await user.type(screen.getByLabelText('Body'), 'Click here to confirm.')
  await user.click(screen.getByRole('button', { name: 'Analyze' }))

  expect(await screen.findByText('92%')).toBeInTheDocument()
  expect(screen.getByText('High Risk')).toBeInTheDocument()
})

it('shows error message when API call fails', async () => {
  const user = userEvent.setup()
  vi.spyOn(globalThis, 'fetch')
    .mockResolvedValueOnce(new Response(JSON.stringify([]), { status: 200 })) // samples
    .mockResolvedValueOnce(new Response('', { status: 500 })) // analyze fails

  render(<App />)
  await user.type(screen.getByLabelText('Subject'), 'Test')
  await user.click(screen.getByRole('button', { name: 'Analyze' }))

  expect(await screen.findByRole('alert')).toBeInTheDocument()
})
