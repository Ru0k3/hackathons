import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useUIStore from '@/stores/useUIStore'
import { trackEvent } from '@/lib/posthog'

// ── Constants ──────────────────────────────────────────────────────────────────
const GENDER_OPTIONS = [
  "Women's",
  "Men's",
  'Non-binary / Gender-fluid',
  'Prefer not to say',
]

const COLOUR_PALETTES = [
  { label: 'Neutral & Earthy',  swatches: ['#EDE8DF', '#8C7B6B', '#1C1916', '#C8A97E'] },
  { label: 'Cool Monochromes', swatches: ['#F0F0F2', '#B0B8C4', '#4A5568', '#1A202C'] },
  { label: 'Warm Brights',     swatches: ['#FFF1E6', '#F4845F', '#C1292E', '#241023'] },
  { label: 'Jewel Tones',      swatches: ['#F2E9E4', '#9A8C98', '#4A4E69', '#22223B'] },
]

const STYLE_TAGS = [
  'Minimalist', 'Classic', 'Streetwear', 'Boho', 'Preppy',
  'Athleisure', 'Romantic', 'Edgy', 'Business Casual', 'Y2K',
]

const STEPS = ['Gender', 'Palette', 'Style', 'Done']

export default function OnboardingPage() {
  const navigate = useNavigate()
  const setOnboarded = useUIStore((s) => s.setOnboarded)

  const [step, setStep]           = useState(0)
  const [gender, setGender]       = useState(null)
  const [palette, setPalette]     = useState(null)
  const [styles, setStyles]       = useState([])

  function toggleStyle(tag) {
    setStyles((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    )
  }

  function handleNext() {
    if (step < STEPS.length - 2) {
      setStep((s) => s + 1)
    } else {
      trackEvent('onboarding_completed', { gender, palette, styles })
      setOnboarded(true)
      navigate('/wardrobe')
    }
  }

  const canAdvance =
    (step === 0 && gender !== null) ||
    (step === 1 && palette !== null) ||
    (step === 2 && styles.length > 0)

  return (
    <div className="onboarding-page">
      {/* Progress */}
      <div className="onboarding-steps">
        {STEPS.slice(0, -1).map((label, i) => (
          <span
            key={label}
            className={`onboarding-step ${i === step ? 'active' : ''} ${i < step ? 'done' : ''}`}
          >
            {label}
          </span>
        ))}
      </div>

      {/* Step 0 — Gender */}
      {step === 0 && (
        <section>
          <h2>How do you like to shop?</h2>
          <div className="option-grid">
            {GENDER_OPTIONS.map((opt) => (
              <button
                key={opt}
                className={`option-btn ${gender === opt ? 'selected' : ''}`}
                onClick={() => setGender(opt)}
              >
                {opt}
              </button>
            ))}
          </div>
        </section>
      )}

      {/* Step 1 — Colour palette */}
      {step === 1 && (
        <section>
          <h2>Pick your colour vibe</h2>
          <div className="palette-grid">
            {COLOUR_PALETTES.map((p) => (
              <button
                key={p.label}
                className={`palette-btn ${palette === p.label ? 'selected' : ''}`}
                onClick={() => setPalette(p.label)}
              >
                <div className="swatches">
                  {p.swatches.map((hex) => (
                    <span key={hex} style={{ background: hex }} />
                  ))}
                </div>
                <span>{p.label}</span>
              </button>
            ))}
          </div>
        </section>
      )}

      {/* Step 2 — Style tags */}
      {step === 2 && (
        <section>
          <h2>Your style (pick at least one)</h2>
          <div className="tag-cloud">
            {STYLE_TAGS.map((tag) => (
              <button
                key={tag}
                className={`tag-btn ${styles.includes(tag) ? 'selected' : ''}`}
                onClick={() => toggleStyle(tag)}
              >
                {tag}
              </button>
            ))}
          </div>
        </section>
      )}

      <button
        className="btn-primary"
        disabled={!canAdvance}
        onClick={handleNext}
      >
        {step === STEPS.length - 2 ? "Let's go →" : 'Next →'}
      </button>
    </div>
  )
}
