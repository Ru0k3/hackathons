import { useEffect, useRef, useState } from 'react'
import { checkOutfit, listOutfitChecks } from '@/api/outfitCheck'
import { trackEvent } from '@/lib/posthog'

const OCCASIONS = ['casual', 'work', 'date night', 'formal', 'gym', 'weekend', 'travel']

export default function OutfitCheckPage() {
  const fileRef = useRef()
  const [preview,   setPreview]   = useState(null)
  const [occasion,  setOccasion]  = useState('casual')
  const [weather,   setWeather]   = useState('')
  const [styleGoal, setStyleGoal] = useState('')
  const [result,    setResult]    = useState(null)
  const [loading,   setLoading]   = useState(false)
  const [error,     setError]     = useState('')
  const [history,   setHistory]   = useState([])
  const [histLoading, setHistLoading] = useState(true)

  useEffect(() => {
    listOutfitChecks()
      .then((d) => setHistory(d.items))
      .catch(() => {})
      .finally(() => setHistLoading(false))
  }, [])

  function handleFilePick(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setResult(null)
    setError('')
    setPreview({ file, url: URL.createObjectURL(file) })
  }

  async function handleSubmit() {
    if (!preview?.file) return
    setLoading(true)
    setError('')
    try {
      const ctx = {
        occasion,
        weather:    weather    || undefined,
        style_goal: styleGoal  || undefined,
      }
      const data = await checkOutfit(preview.file, ctx)
      setResult(data)
      setHistory((prev) => [{ id: Date.now(), image_url: preview.url, result: data }, ...prev])
      trackEvent('outfit_checked', { occasion, score: data.score })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function scoreColor(score) {
    if (score >= 75) return 'var(--color-success)'
    if (score >= 50) return 'var(--color-warning)'
    return 'var(--color-error)'
  }

  return (
    <div className="page outfit-check-page">
      <header className="page-header">
        <h1>Outfit Check</h1>
        <p className="page-subtitle">Get honest AI feedback on your look</p>
      </header>

      {/* Upload panel */}
      <div className="check-panel">
        <div
          className="drop-zone"
          onClick={() => fileRef.current?.click()}
        >
          {preview ? (
            <img src={preview.url} alt="Your outfit" className="check-preview-img" />
          ) : (
            <div className="drop-zone-inner">
              <span className="drop-icon">📸</span>
              <p>Tap to upload an outfit photo</p>
            </div>
          )}
        </div>
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          className="visually-hidden"
          onChange={handleFilePick}
        />

        {preview && (
          <div className="check-context">
            <label className="auth-label">
              Occasion
              <select
                className="auth-input"
                value={occasion}
                onChange={(e) => setOccasion(e.target.value)}
              >
                {OCCASIONS.map((o) => (
                  <option key={o} value={o}>{o.charAt(0).toUpperCase() + o.slice(1)}</option>
                ))}
              </select>
            </label>

            <label className="auth-label">
              Weather (optional)
              <input
                type="text"
                className="auth-input"
                placeholder="e.g. hot and sunny"
                value={weather}
                onChange={(e) => setWeather(e.target.value)}
              />
            </label>

            <label className="auth-label">
              Style goal (optional)
              <input
                type="text"
                className="auth-input"
                placeholder="e.g. look polished but relaxed"
                value={styleGoal}
                onChange={(e) => setStyleGoal(e.target.value)}
              />
            </label>

            <button
              className="btn-primary"
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? 'Analysing…' : 'Check this outfit'}
            </button>
          </div>
        )}

        {error && <p className="page-error">{error}</p>}
      </div>

      {/* Result */}
      {result && (
        <div className="check-result">
          <div className="check-score" style={{ color: scoreColor(result.score) }}>
            {result.score}<span>/100</span>
          </div>
          <p className="check-verdict">{result.verdict}</p>

          <div className="check-columns">
            <div className="check-col">
              <h3>What works</h3>
              <ul>{result.pros?.map((p, i) => <li key={i}>{p}</li>)}</ul>
            </div>
            <div className="check-col">
              <h3>What to improve</h3>
              <ul>{result.cons?.map((c, i) => <li key={i}>{c}</li>)}</ul>
            </div>
          </div>

          {result.suggestions?.length > 0 && (
            <div className="check-suggestions">
              <h3>Suggestions</h3>
              <ul>{result.suggestions.map((s, i) => <li key={i}>{s}</li>)}</ul>
            </div>
          )}
        </div>
      )}

      {/* History */}
      {!histLoading && history.length > 0 && (
        <section className="check-history">
          <h2>Recent checks</h2>
          <div className="check-history-grid">
            {history.slice(0, 6).map((item) => (
              <div key={item.id} className="check-history-card">
                <img src={item.image_url} alt="Past outfit" loading="lazy" />
                {item.result?.score != null && (
                  <span
                    className="check-history-score"
                    style={{ color: scoreColor(item.result.score) }}
                  >
                    {item.result.score}
                  </span>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
