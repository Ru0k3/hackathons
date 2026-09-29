import { useEffect, useState } from 'react'
import {
  listOutfits,
  createOutfit,
  deleteOutfit,
  generateOutfits,
} from '@/api/outfits'
import { trackEvent } from '@/lib/posthog'

const OCCASIONS = ['casual', 'work', 'date night', 'formal', 'gym', 'weekend']

export default function OutfitsPage() {
  const [outfits,   setOutfits]   = useState([])
  const [loading,   setLoading]   = useState(true)
  const [error,     setError]     = useState('')
  const [generating, setGenerating] = useState(false)
  const [genModal,  setGenModal]  = useState(false)
  const [occasion,  setOccasion]  = useState('casual')
  const [weather,   setWeather]   = useState('')
  const [mood,      setMood]      = useState('')
  const [aiResults, setAiResults] = useState([])

  useEffect(() => {
    listOutfits()
      .then((d) => setOutfits(d.outfits))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  async function handleGenerate() {
    setGenerating(true)
    setError('')
    try {
      const data = await generateOutfits({
        occasion,
        weather: weather || undefined,
        mood:    mood    || undefined,
        n: 3,
      })
      setAiResults(data.outfits)
      trackEvent('outfits_generated', { occasion })
    } catch (err) {
      setError(err.message)
    } finally {
      setGenerating(false)
    }
  }

  async function handleSaveGenerated(outfit) {
    try {
      const saved = await createOutfit({
        name:     outfit.name,
        item_ids: outfit.item_ids,
        occasion,
        notes:    outfit.reasoning,
      })
      setOutfits((prev) => [saved, ...prev])
      setAiResults((prev) => prev.filter((o) => o !== outfit))
      trackEvent('outfit_saved')
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleDelete(id) {
    try {
      await deleteOutfit(id)
      setOutfits((prev) => prev.filter((o) => o.id !== id))
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="page outfits-page">
      <header className="page-header">
        <h1>Outfits</h1>
        <button className="btn-primary" onClick={() => setGenModal(true)}>
          ✦ Generate with AI
        </button>
      </header>

      {error && <p className="page-error">{error}</p>}

      {/* AI generate modal */}
      {genModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Generate outfits</h2>

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
                placeholder="e.g. sunny, 25°C"
                value={weather}
                onChange={(e) => setWeather(e.target.value)}
              />
            </label>

            <label className="auth-label">
              Mood / vibe (optional)
              <input
                type="text"
                className="auth-input"
                placeholder="e.g. relaxed, confident"
                value={mood}
                onChange={(e) => setMood(e.target.value)}
              />
            </label>

            {aiResults.length > 0 && (
              <div className="ai-results">
                {aiResults.map((outfit, i) => (
                  <div key={i} className="ai-outfit-card">
                    <strong>{outfit.name}</strong>
                    <p className="ai-reasoning">{outfit.reasoning}</p>
                    <p className="ai-items">{outfit.item_ids?.length ?? 0} items</p>
                    <button
                      className="btn-primary"
                      onClick={() => handleSaveGenerated(outfit)}
                    >
                      Save this look
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div className="modal-actions">
              <button
                className="btn-secondary"
                onClick={() => { setGenModal(false); setAiResults([]) }}
              >
                Close
              </button>
              <button
                className="btn-primary"
                onClick={handleGenerate}
                disabled={generating}
              >
                {generating ? 'Generating…' : 'Generate'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Saved outfits */}
      {loading ? (
        <div className="grid-loading">
          {[...Array(4)].map((_, i) => <div key={i} className="outfit-card skeleton" />)}
        </div>
      ) : outfits.length === 0 ? (
        <div className="empty-state">
          <p>No saved outfits yet.</p>
          <button className="btn-primary" onClick={() => setGenModal(true)}>
            Generate your first outfit
          </button>
        </div>
      ) : (
        <div className="outfits-grid">
          {outfits.map((outfit) => (
            <div key={outfit.id} className="outfit-card">
              <div className="outfit-card-header">
                <h3>{outfit.name}</h3>
                {outfit.occasion && (
                  <span className="outfit-occasion">{outfit.occasion}</span>
                )}
              </div>
              {outfit.notes && (
                <p className="outfit-notes">{outfit.notes}</p>
              )}
              <p className="outfit-items">{outfit.item_ids?.length ?? 0} items</p>
              <button
                className="outfit-delete"
                onClick={() => handleDelete(outfit.id)}
                aria-label="Delete outfit"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
