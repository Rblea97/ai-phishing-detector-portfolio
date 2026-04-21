import { useEffect, useRef, useState } from 'react'
import { analyzeEmail, fetchSamples } from './api/client'
import { MLResultCard } from './components/MLResultCard'
import { LLMResultCard } from './components/LLMResultCard'
import { HeaderAnalysisCard } from './components/HeaderAnalysisCard'
import type { AnalyzeResponse, SampleEmail } from './types'
import './App.css'

type AppState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'done'; result: AnalyzeResponse }
  | { status: 'error'; message: string }

export default function App() {
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [headers, setHeaders] = useState('')
  const [samples, setSamples] = useState<SampleEmail[]>([])
  const [state, setState] = useState<AppState>({ status: 'idle' })
  const resultRef = useRef<HTMLElement>(null)

  useEffect(() => {
    fetchSamples()
      .then(setSamples)
      .catch(() => {/* samples are optional for demo */})
  }, [])

  function loadSample(sample: SampleEmail) {
    setSubject(sample.subject)
    setBody(sample.body)
    setHeaders('')
    setState({ status: 'idle' })
  }

  async function handleAnalyze(e: React.FormEvent) {
    e.preventDefault()
    if (!subject.trim() && !body.trim()) return
    setState({ status: 'loading' })
    try {
      const result = await analyzeEmail({ subject, body, headers: headers || undefined })
      setState({ status: 'done', result })
      setTimeout(() => resultRef.current?.scrollIntoView({ behavior: 'smooth' }), 50)
    } catch (err) {
      setState({ status: 'error', message: err instanceof Error ? err.message : 'Unknown error' })
    }
  }

  const phishingSamples = samples.filter((s) => s.label === 'phishing')
  const legitSamples = samples.filter((s) => s.label === 'legitimate')

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">AI Phishing Detector</h1>
        <p className="app-subtitle">
          Defensive ML + LLM analysis — TF-IDF baseline with Claude reasoning
        </p>
      </header>

      <main className="app-main">
        <section className="form-panel">
          {samples.length > 0 && (
            <div className="sample-picker">
              <p className="sample-picker__label">Load a sample</p>
              <div className="sample-picker__groups">
                <div className="sample-group">
                  <span className="sample-group__heading risk-high">Phishing</span>
                  <div className="sample-group__buttons">
                    {phishingSamples.map((s) => (
                      <button
                        key={s.id}
                        type="button"
                        className="sample-btn sample-btn--phishing"
                        onClick={() => loadSample(s)}
                      >
                        {s.subject.length > 32 ? s.subject.slice(0, 32) + '…' : s.subject}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="sample-group">
                  <span className="sample-group__heading risk-low">Legitimate</span>
                  <div className="sample-group__buttons">
                    {legitSamples.map((s) => (
                      <button
                        key={s.id}
                        type="button"
                        className="sample-btn sample-btn--legit"
                        onClick={() => loadSample(s)}
                      >
                        {s.subject.length > 32 ? s.subject.slice(0, 32) + '…' : s.subject}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          <form className="email-form" onSubmit={handleAnalyze}>
            <label className="field-label" htmlFor="subject">
              Subject
            </label>
            <input
              id="subject"
              className="field-input"
              type="text"
              placeholder="Email subject line"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
            />

            <label className="field-label" htmlFor="body">
              Body
            </label>
            <textarea
              id="body"
              className="field-textarea"
              rows={12}
              placeholder="Paste email body here…"
              value={body}
              onChange={(e) => setBody(e.target.value)}
            />

            <details className="headers-toggle">
              <summary className="headers-toggle__summary">
                Add raw email headers{' '}
                <span className="headers-toggle__hint">
                  (optional — enables SPF/DKIM/DMARC analysis)
                </span>
              </summary>
              <label className="field-label" htmlFor="headers">
                Raw Headers
              </label>
              <textarea
                id="headers"
                className="field-textarea"
                rows={6}
                placeholder="Paste raw email headers here…"
                value={headers}
                onChange={(e) => setHeaders(e.target.value)}
              />
            </details>

            <button
              type="submit"
              className="analyze-btn"
              disabled={state.status === 'loading' || (!subject.trim() && !body.trim())}
            >
              {state.status === 'loading' ? 'Analyzing…' : 'Analyze'}
            </button>

            {state.status === 'error' && (
              <p className="error-msg" role="alert">
                {state.message}
              </p>
            )}
          </form>
        </section>

        <section className="result-panel" ref={resultRef} aria-live="polite">
          {state.status === 'idle' && (
            <div className="empty-state">
              <p>Results will appear here after analysis.</p>
            </div>
          )}

          {(state.status === 'loading' || state.status === 'done') && (
            <div className="result-grid">
              <MLResultCard
                result={
                  state.status === 'done'
                    ? state.result.ml
                    : { score: 0, risk_level: 'low', top_features: [] }
                }
              />
              <LLMResultCard
                result={state.status === 'done' ? state.result.llm : null}
                loading={state.status === 'loading'}
              />
              <HeaderAnalysisCard
                result={state.status === 'done' ? state.result.header_analysis : null}
              />
            </div>
          )}
        </section>
      </main>

      <footer className="app-footer">
        <p>Defensive use only · Dataset: SpamAssassin public corpus (Apache 2.0)</p>
      </footer>
    </div>
  )
}
