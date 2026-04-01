import type { AnalyzeRequest, AnalyzeResponse, SampleEmail } from '../types'

const API_BASE = '/api'

export async function fetchSamples(): Promise<SampleEmail[]> {
  const resp = await fetch(`${API_BASE}/samples`)
  if (!resp.ok) throw new Error(`Failed to fetch samples: ${resp.status}`)
  return resp.json() as Promise<SampleEmail[]>
}

export async function analyzeEmail(req: AnalyzeRequest): Promise<AnalyzeResponse> {
  const resp = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!resp.ok) throw new Error(`Analysis failed: ${resp.status}`)
  return resp.json() as Promise<AnalyzeResponse>
}
