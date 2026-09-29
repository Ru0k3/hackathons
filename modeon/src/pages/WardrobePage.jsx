import { useCallback, useEffect, useRef, useState } from 'react'
import {
  listWardrobeItems,
  addWardrobeItem,
  deleteWardrobeItem,
  classifyImage,
} from '@/api/wardrobe'
import { trackEvent } from '@/lib/posthog'

const CATEGORIES = ['All', 'tops', 'bottoms', 'outerwear', 'shoes', 'accessories', 'dresses', 'suits']

export default function WardrobePage() {
  const [items,      setItems]      = useState([])
  const [loading,    setLoading]    = useState(true)
  const [error,      setError]      = useState('')
  const [category,   setCategory]   = useState('All')
  const [uploading,  setUploading]  = useState(false)
  const [preview,    setPreview]    = useState(null)   // { file, url, aiMeta }
  const [deleting,   setDeleting]   = useState(null)
  const fileRef = useRef()

  const fetchItems = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const params = category !== 'All' ? { category } : {}
      const data   = await listWardrobeItems(params)
      setItems(data.items)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [category])

  useEffect(() => { fetchItems() }, [fetchItems])

  // ── File picked → AI classify → show preview ───────────────────────────────
  async function handleFilePick(e) {
    const file = e.target.files?.[0]
    if (!file) return
    const url = URL.createObjectURL(file)
    setPreview({ file, url, aiMeta: null, loading: true })

    try {
      const aiMeta = await classifyImage(file)
      setPreview((p) => ({ ...p, aiMeta, loading: false }))
    } catch {
      setPreview((p) => ({ ...p, loading: false }))
    }
  }

  // ── Confirm upload ─────────────────────────────────────────────────────────
  async function handleConfirmUpload() {
    if (!preview?.file) return
    setUploading(true)
    try {
      const newItem = await addWardrobeItem(preview.file, preview.aiMeta ?? {})
      setItems((prev) => [newItem, ...prev])
      trackEvent('wardrobe_item_added', { category: newItem.category })
      setPreview(null)
      URL.revokeObjectURL(preview.url)
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
      fileRef.current.value = ''
    }
  }

  // ── Delete ─────────────────────────────────────────────────────────────────
  async function handleDelete(itemId) {
    setDeleting(itemId)
    try {
      await deleteWardrobeItem(itemId)
      setItems((prev) => prev.filter((i) => i.id !== itemId))
      trackEvent('wardrobe_item_deleted')
    } catch (err) {
      setError(err.message)
    } finally {
      setDeleting(null)
    }
  }

  return (
    <div className="page wardrobe-page">
      <header className="page-header">
        <h1>My Wardrobe</h1>
        <button
          className="btn-primary"
          onClick={() => fileRef.current?.click()}
        >
          + Add item
        </button>
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          className="visually-hidden"
          onChange={handleFilePick}
        />
      </header>

      {/* Category filter */}
      <div className="filter-bar">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            className={`filter-chip ${category === cat ? 'active' : ''}`}
            onClick={() => setCategory(cat)}
          >
            {cat.charAt(0).toUpperCase() + cat.slice(1)}
          </button>
        ))}
      </div>

      {/* Upload preview modal */}
      {preview && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Add to wardrobe</h2>
            <img src={preview.url} alt="Preview" className="upload-preview-img" />
            {preview.loading ? (
              <p className="ai-loading">Analysing with AI…</p>
            ) : preview.aiMeta ? (
              <div className="ai-meta">
                <p><strong>Category:</strong> {preview.aiMeta.category}</p>
                <p><strong>Colour:</strong>   {preview.aiMeta.colour}</p>
                <p><strong>Tags:</strong>     {preview.aiMeta.tags?.join(', ')}</p>
                <p><strong>Description:</strong> {preview.aiMeta.description}</p>
              </div>
            ) : (
              <p className="ai-loading">Could not classify — will save as-is.</p>
            )}
            <div className="modal-actions">
              <button
                className="btn-secondary"
                onClick={() => {
                  URL.revokeObjectURL(preview.url)
                  setPreview(null)
                  fileRef.current.value = ''
                }}
              >
                Cancel
              </button>
              <button
                className="btn-primary"
                onClick={handleConfirmUpload}
                disabled={uploading || preview.loading}
              >
                {uploading ? 'Saving…' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Error */}
      {error && <p className="page-error">{error}</p>}

      {/* Grid */}
      {loading ? (
        <div className="grid-loading">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="wardrobe-card skeleton" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="empty-state">
          <p>No items yet.</p>
          <button className="btn-primary" onClick={() => fileRef.current?.click()}>
            Add your first item
          </button>
        </div>
      ) : (
        <div className="wardrobe-grid">
          {items.map((item) => (
            <div key={item.id} className="wardrobe-card">
              <img src={item.image_url} alt={item.description ?? item.category} loading="lazy" />
              <div className="wardrobe-card-body">
                <span className="wardrobe-card-category">{item.category}</span>
                {item.colour && <span className="wardrobe-card-colour">{item.colour}</span>}
                {item.brand  && <span className="wardrobe-card-brand">{item.brand}</span>}
              </div>
              <button
                className="wardrobe-card-delete"
                onClick={() => handleDelete(item.id)}
                disabled={deleting === item.id}
                aria-label="Delete item"
              >
                {deleting === item.id ? '…' : '×'}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
