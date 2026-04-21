/** Mirrors backend app/schemas.py */

export interface Feature {
  token: string
  weight: number
}

export interface HeaderFlag {
  name: string
  description: string
  severity: 'high' | 'medium' | 'low'
}

export interface HeaderAnalysis {
  from_domain: string | null
  reply_to_domain: string | null
  return_path_domain: string | null
  spf: string | null
  dkim: string | null
  dmarc: string | null
  flags: HeaderFlag[]
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

export interface SiemLogEntry {
  timestamp: string
  event_type: string
  verdict: string
  severity: 'HIGH' | 'MEDIUM' | 'LOW'
  confidence: number
  mitre_technique: string
  iocs: string[]
  header_flags: string[]
  analyst_notes: string
}

export interface AnalyzeRequest {
  subject: string
  body: string
  headers?: string
}

export interface AnalyzeResponse {
  ml: MLResult
  llm: LLMResult | null
  header_analysis: HeaderAnalysis | null
  siem_log: SiemLogEntry
}

export interface SampleEmail {
  id: string
  label: string
  subject: string
  body: string
}
