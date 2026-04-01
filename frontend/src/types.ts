/** Mirrors backend app/schemas.py */

export interface Feature {
  token: string
  weight: number
}

export interface MLResult {
  score: number
  risk_level: 'high' | 'medium' | 'low'
  top_features: Feature[]
}

export interface LLMResult {
  risk_level: 'high' | 'medium' | 'low'
  reasoning: string
  iocs: string[]
}

export interface AnalyzeRequest {
  subject: string
  body: string
  headers?: string
}

export interface AnalyzeResponse {
  ml: MLResult
  llm: LLMResult | null
}

export interface SampleEmail {
  id: string
  label: string
  subject: string
  body: string
}
