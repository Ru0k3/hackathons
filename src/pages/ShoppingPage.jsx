import { useEffect, useRef, useState } from 'react'
import {
  getShoppingList,
  addShoppingItem,
  updateShoppingItem,
  deleteShoppingItem,
  uploadShoppingImage,
  getShoppingRecommendations,
} from '@/api/shopping'
import { trackEvent } from '@/lib/posthog'

export default function ShoppingPage() {
  const fileRef = useRef()
  const [items,   setItems]   = useState([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')
  const [newName, setNewName] = useState('')
  const [newUrl,  setNewUrl]  = useState('')
  const [adding,  setAdding]  = useState(false)
  const [recs,    setRecs]    = useState([])
  const [recsLoading, setRecsLoading] = useState(false)

  useEffect(() => {
    getShoppingList()
      .then((d) => setItems(d.items))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  async function handleAdd(e) {
    e.preventDefault()
    if (!newName.trim()) return
    setAdding(true)
    try {
      const item = await addShoppingItem({ name: newName, url: newUrl || undefined })
      setItems((prev) => [item, ...prev])
      setNewName('')
      setNewUrl('')
      trackEvent('shopping_item_added')
    } catch (err) {
      setError(err.message)
    } finally {
      setAdding(false)
    }
  }

  async function handleTogglePurchased(item) {
    try {
      const updated = await updateShoppingItem(item.id, { purchased: !item.purchased })
      setItems((prev) => prev.map((i) => (i.id === item.id ? updated : i)))
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleDelete(itemId) {
    try {
      await deleteShoppingItem(itemId)
      setItems((prev) => prev.filter((i) => i.id !== itemId))
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleImageUpload(e) {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      const { item_id, url } = await uploadShoppingImage(file)
      setItems((prev) => [{ id: item_id, name: 'Inspo', image_url: url, purchased: false }, ...prev])
      trackEvent('shopping_image_uploaded')
    } catch (err) {
      setError(err.message)
    } finally {
      fileRef.current.value = ''
    }
  }

  async function handleGetRecommendations() {
    setRecsLoading(true)
    setError('')
    try {
      const data = await getShoppingRecommendations()
      setRecs(data.recommendations)
      trackEvent('shopping_recs_requested')
    } catch (err) {
      setError(err.message)
    } finally {
      setRecsLoading(false)
    }
  }

  const active    = items.filter((i) => !i.purchased)
  const purchased = items.filter((i) =>  i.purchased)

  return (
    <div className="page shopping-page">
      <header className="page-header">
        <h1>Shopping List</h1>
        <div className="page-header-actions">
          <button className="btn-secondary" onClick={() => fileRef.current?.click()}>
            + Inspo image
          </button>
          <button className="btn-primary" onClick={handleGetRecommendations} disabled={recsLoading}>
            {recsLoading ? 'Thinking…' : '✦ AI suggestions'}
          </button>
        </div>
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          className="visually-hidden"
          onChange={handleImageUpload}
        />
      </header>

      {error && <p className="page-error">{error}</p>}

      {/* Add form */}
      <form className="add-item-form" onSubmit={handleAdd}>
        <input
          type="text"
          className="auth-input"
          placeholder="Item name…"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
        />
        <input
          type="url"
          className="auth-input"
          placeholder="Link (optional)"
          value={newUrl}
          onChange={(e) => setNewUrl(e.target.value)}
        />
        <button type="submit" className="btn-primary" disabled={adding || !newName.trim()}>
          {adding ? '…' : 'Add'}
        </button>
      </form>

      {/* AI recommendations */}
      {recs.length > 0 && (
        <section className="recs-section">
          <h2>AI suggestions for your wardrobe</h2>
          <div className="recs-grid">
            {recs.map((rec, i) => (
              <div key={i} className="rec-card">
                <div className="rec-priority rec-priority--{rec.priority}">{rec.priority}</div>
                <strong>{rec.item}</strong>
                <p>{rec.reason}</p>
                <span className="rec-budget">{rec.approximate_budget}</span>
                <button
                  className="btn-secondary rec-add-btn"
                  onClick={async () => {
                    const item = await addShoppingItem({ name: rec.item, notes: rec.reason })
                    setItems((prev) => [item, ...prev])
                    setRecs((prev) => prev.filter((_, j) => j !== i))
                  }}
                >
                  Add to list
                </button>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Active list */}
      {loading ? (
        <p className="loading-text">Loading…</p>
      ) : active.length === 0 && purchased.length === 0 ? (
        <div className="empty-state">
          <p>Your shopping list is empty.</p>
        </div>
      ) : (
        <>
          <ul className="shopping-list">
            {active.map((item) => (
              <li key={item.id} className="shopping-item">
                {item.image_url && (
                  <img src={item.image_url} alt={item.name} className="shopping-thumb" />
                )}
                <div className="shopping-item-body">
                  <span className="shopping-item-name">{item.name}</span>
                  {item.url && (
                    <a href={item.url} target="_blank" rel="noopener noreferrer" className="shopping-item-link">
                      View →
                    </a>
                  )}
                </div>
                <button
                  className="btn-icon"
                  onClick={() => handleTogglePurchased(item)}
                  aria-label="Mark as purchased"
                >
                  ✓
                </button>
                <button
                  className="btn-icon btn-icon--danger"
                  onClick={() => handleDelete(item.id)}
                  aria-label="Delete"
                >
                  ×
                </button>
              </li>
            ))}
          </ul>

          {purchased.length > 0 && (
            <details className="purchased-section">
              <summary>Purchased ({purchased.length})</summary>
              <ul className="shopping-list shopping-list--purchased">
                {purchased.map((item) => (
                  <li key={item.id} className="shopping-item shopping-item--purchased">
                    <span className="shopping-item-name">{item.name}</span>
                    <button className="btn-icon" onClick={() => handleTogglePurchased(item)}>↩</button>
                    <button className="btn-icon btn-icon--danger" onClick={() => handleDelete(item.id)}>×</button>
                  </li>
                ))}
              </ul>
            </details>
          )}
        </>
      )}
    </div>
  )
}
