import { analyzeEmail, fetchSamples } from './client'

describe('fetchSamples', () => {
  it('calls /api/samples and returns parsed data', async () => {
    const mockData = [{ id: '1', label: 'phishing', subject: 'Test', body: 'Body' }]
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify(mockData), { status: 200 })
    )
    const result = await fetchSamples()
    expect(result).toEqual(mockData)
    expect(fetch).toHaveBeenCalledWith('/api/samples')
  })

  it('throws when response is not ok', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(new Response('', { status: 500 }))
    await expect(fetchSamples()).rejects.toThrow('Failed to fetch samples: 500')
  })
})

describe('analyzeEmail', () => {
  it('posts to /api/analyze and returns response', async () => {
    const mockResponse = { ml: { score: 0.9, risk_level: 'high', top_features: [] }, llm: null }
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify(mockResponse), { status: 200 })
    )
    const result = await analyzeEmail({ subject: 'Test', body: 'Body' })
    expect(result).toEqual(mockResponse)
    expect(fetch).toHaveBeenCalledWith(
      '/api/analyze',
      expect.objectContaining({ method: 'POST' })
    )
  })

  it('sends Content-Type: application/json', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({ ml: { score: 0, risk_level: 'low', top_features: [] }, llm: null }), { status: 200 })
    )
    await analyzeEmail({ subject: 'S', body: 'B' })
    expect(fetch).toHaveBeenCalledWith(
      '/api/analyze',
      expect.objectContaining({ headers: { 'Content-Type': 'application/json' } })
    )
  })

  it('throws when response is not ok', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(new Response('', { status: 422 }))
    await expect(analyzeEmail({ subject: 'S', body: 'B' })).rejects.toThrow('Analysis failed: 422')
  })
})
