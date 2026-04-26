import { useEffect, useState } from 'react'
import {
  getLaundryStatus,
  updateLaundryStatus,
  markAllClean,
  getCleanOutfitSuggestions,
} from '@/api/laundry'
import { trackEvent } from '@/lib/posthog'

const STATUS_LABELS = { clean: 'Clean', dirty: 'Dirty', washing: 'Washing' }
const STATUS_CYCLE  = { clean: 'dirty', dirty: 'washing', washing: 'clean' }

export default function LaundryPage() {
  const [items,    setItems]    = useState([])
  const [loading,  setLoading]  = useState(true)
  const [error,    setError]    = useState('')
  const [filter,   setFilter]   = useState('all')
  const [outfits,  setOutfits]  = useState([])
  const [sugLoading, setSugLoading] = useState(false)
  const [resetting,  setResetting]  = useState(false)

  useEffect(() => {
    getLaundryStatus()
      .then((d) => setItems(d.items))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  async function handleCycleStatus(item) {
    const nextStatus = STATUS_CYCLE[item.laundry_status ?? 'clean']
    try {
      await updateLaundryStatus([{ item_id: item.id, status: nextStatus }])
      setItems((prev) =>
        prev.map((i) => (i.id === item.id ? { ...i, laundry_status: nextStatus } : i))
      )
      trackEvent('laundry_status_changed', { status: nextStatus })
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleReset() {
    setResetting(true)
    try {
      await markAllClean()
      setItems((prev) => prev.map((i) => ({ ...i, laundry_status: 'clean' })))
      trackEvent('laundry_reset')
    } catch (err) {
      setError(err.message)
    } finally {
      setResetting(false)
    }
  }

  async function handleSuggestions() {
    setSugLoading(true)
    setError('')
    try {
      const data = await getCleanOutfitSuggestions()
      setOutfits(data.outfits)
    } catch (err) {
      setError(err.message)
    } finally {
      setSugLoading(false)
    }
  }

  const counts = {
    clean:   items.filter((i) => (i.laundry_status ?? 'clean') === 'clean').length,
    dirty:   items.filter((i) => i.laundry_status === 'dirty').length,
    washing: items.filter((i) => i.laundry_status === 'washing').length,
  }

  const visible = filter === 'all'
    ? items
    : items.filter((i) => (i.laundry_status ?? 'clean') === filter)

  return (
    <div className="page laundry-page">
      <header className="page-header">
        <h1>Laundry Tracker</h1>
        <div className="page-header-actions">
          <button
            className="btn-secondary"
            onClick={handleSuggestions}
            disabled={sugLoading || counts.clean === 0}
          >
            {sugLoading ? 'Thinking…' : '✦ What can I wear?'}
          </button>
          <button
            className="btn-primary"
            onClick={handleReset}
            disabled={resetting || counts.dirty + counts.washing === 0}
          >
            {resetting ? 'Resetting…' : '✓ All clean'}
          </button>
        </div>
      </header>

      {/* Stats */}
      <div className="laundry-stats">
        {Object.entries(counts).map(([status, count]) => (
          <div key={status} className={`laundry-stat laundry-stat--${status}`}>
            <span className="laundry-stat-count">{count}</span>
            <span className="laundry-stat-label">{STATUS_LABELS[status]}</span>
          </div>
        ))}
      </div>

      {error && <p className="page-error">{error}</p>}

      {/* Clean outfit suggestions */}
      {outfits.length > 0 && (
        <section className="laundry-suggestions">
          <h2>Outfits from clean items</h2>
          <div className="laundry-outfits-grid">
            {outfits.map((outfit, i) => (
              <div key={i} className="laundry-outfit-card">
                <strong>{outfit.name}</strong>
                <p>{outfit.reasoning}</p>
                <span>{outfit.item_ids?.length ?? 0} items</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Filter tabs */}
      <div className="filter-bar">
        {['all', 'clean', 'dirty', 'washing'].map((f) => (
          <button
            key={f}
            className={`filter-chip ${filter === f ? 'active' : ''}`}
            onClick={() => setFilter(f)}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
            {f !== 'all' && <span className="filter-count">{counts[f]}</span>}
          </button>
        ))}
      </div>

      {/* Items grid */}
      {loading ? (
        <div className="grid-loading">
          {[...Array(6)].map((_, i) => <div key={i} className="wardrobe-card skeleton" />)}
        </div>
      ) : visible.length === 0 ? (
        <div className="empty-state">
          <p>{filter === 'all' ? 'No wardrobe items found.' : `No ${filter} items.`}</p>
        </div>
      ) : (
        <div className="wardrobe-grid">
          {visible.map((item) => {
            const status = item.laundry_status ?? 'clean'
            return (
              <div key={item.id} className={`wardrobe-card wardrobe-card--${status}`}>
                <img src={item.image_url} alt={item.category} loading="lazy" />
                <div className="wardrobe-card-body">
                  <span className="wardrobe-card-category">{item.category}</span>
                </div>
                <button
                  className={`laundry-status-btn laundry-status-btn--${status}`}
                  onClick={() => handleCycleStatus(item)}
                  title={`Currently ${status}. Click to change.`}
                >
                  {STATUS_LABELS[status]}
                </button>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
