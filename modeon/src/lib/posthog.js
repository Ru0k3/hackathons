import posthog from 'posthog-js'

const POSTHOG_KEY = import.meta.env.VITE_POSTHOG_KEY
const POSTHOG_HOST = import.meta.env.VITE_POSTHOG_HOST ?? 'https://app.posthog.com'

export function initPostHog() {
  if (!POSTHOG_KEY || posthog.__loaded) return

  posthog.init(POSTHOG_KEY, {
    api_host: POSTHOG_HOST,
    capture_pageview: false,       // handled manually via router
    capture_pageleave: true,
    autocapture: false,
    persistence: 'localStorage+cookie',
  })
}

/**
 * Identify the signed-in user.
 * Call this once after auth resolves.
 */
export function identifyUser(userId, traits = {}) {
  try {
    if (!posthog.__loaded) return
    posthog.identify(userId, traits)
  } catch (_) {
    // safe no-op
  }
}

/**
 * Reset identity on sign-out.
 */
export function resetUser() {
  try {
    if (!posthog.__loaded) return
    posthog.reset()
  } catch (_) {
    // safe no-op
  }
}

/**
 * Generic event helper used by scaffolded pages and hooks.
 * Typed event wrappers live in analytics.js, but this keeps
 * direct call-sites safe.
 */
export function trackEvent(event, properties = {}) {
  try {
    if (!posthog.__loaded) return
    posthog.capture(event, properties)
  } catch (_) {
    // safe no-op
  }
}

// Export the raw posthog instance so analytics.js can call
// posthog.capture() directly.
export { posthog }
