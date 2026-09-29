import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockSession, mockSupabase, mockApiClient } = vi.hoisted(() => {
  const session = {
    access_token: 'test-token',
    user: { id: 'user-123', email: 'test@example.com' },
  }

  return {
    mockSession: session,
    mockSupabase: {
      auth: {
        getSession: vi.fn().mockResolvedValue({ data: { session } }),
        onAuthStateChange: vi.fn().mockReturnValue({
          data: { subscription: { unsubscribe: vi.fn() } },
        }),
        signUp: vi.fn().mockResolvedValue({ data: session, error: null }),
        signInWithPassword: vi.fn().mockResolvedValue({ data: session, error: null }),
        signInWithOAuth: vi.fn().mockResolvedValue({ error: null }),
        signOut: vi.fn().mockResolvedValue({ error: null }),
        resetPasswordForEmail: vi.fn().mockResolvedValue({ error: null }),
        updateUser: vi.fn().mockResolvedValue({ error: null }),
      },
    },
    mockApiClient: {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      patch: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    },
  }
})

vi.mock('@/lib/supabase', () => ({ supabase: mockSupabase }))
vi.mock('@/lib/posthog', () => ({ identifyUser: vi.fn(), resetUser: vi.fn() }))
vi.mock('@/lib/apiClient', () => ({ apiClient: mockApiClient }))

import useAuthStore from '@/stores/useAuthStore'
import { apiClient } from '@/lib/apiClient'
import { listWardrobeItems, deleteWardrobeItem } from '@/api/wardrobe'
import { listOutfits, createOutfit, generateOutfits } from '@/api/outfits'
import { getLaundryStatus, markAllClean } from '@/api/laundry'

describe('useAuthStore', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    useAuthStore.setState({ user: null, session: null, loading: true })
  })

  it('starts with loading=true and no user', () => {
    const state = useAuthStore.getState()
    expect(state.loading).toBe(true)
    expect(state.user).toBeNull()
  })

  it('init resolves session from Supabase', async () => {
    const cleanup = useAuthStore.getState().init()
    await Promise.resolve()
    await Promise.resolve()

    const state = useAuthStore.getState()
    expect(state.user).toEqual(mockSession.user)
    expect(state.loading).toBe(false)
    cleanup()
  })

  it('signIn calls supabase.signInWithPassword', async () => {
    await useAuthStore
      .getState()
      .signIn({ email: 'test@example.com', password: 'pass' })

    expect(mockSupabase.auth.signInWithPassword).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'pass',
    })
  })

  it('signUp calls supabase.signUp with fullName metadata', async () => {
    await useAuthStore
      .getState()
      .signUp({ email: 'a@b.com', password: 'pass', fullName: 'Jane' })

    expect(mockSupabase.auth.signUp).toHaveBeenCalledWith(
      expect.objectContaining({ options: { data: { full_name: 'Jane' } } }),
    )
  })

  it('signOut clears user and session', async () => {
    useAuthStore.setState({ user: mockSession.user, session: mockSession })
    await useAuthStore.getState().signOut()

    const state = useAuthStore.getState()
    expect(state.user).toBeNull()
    expect(state.session).toBeNull()
  })

  it('signIn throws on Supabase error', async () => {
    mockSupabase.auth.signInWithPassword.mockResolvedValueOnce({
      data: null,
      error: new Error('Invalid credentials'),
    })

    await expect(
      useAuthStore.getState().signIn({ email: 'x@y.com', password: 'wrong' }),
    ).rejects.toThrow('Invalid credentials')
  })
})

describe('wardrobe API', () => {
  beforeEach(() => vi.clearAllMocks())

  it('listWardrobeItems calls GET /api/wardrobe', async () => {
    apiClient.get.mockResolvedValue({ data: { items: [], total: 0 } })

    const result = await listWardrobeItems()

    expect(apiClient.get).toHaveBeenCalledWith('/api/wardrobe', { params: {} })
    expect(result.items).toEqual([])
  })

  it('listWardrobeItems passes category filter', async () => {
    apiClient.get.mockResolvedValue({ data: { items: [], total: 0 } })

    await listWardrobeItems({ category: 'tops' })

    expect(apiClient.get).toHaveBeenCalledWith('/api/wardrobe', {
      params: { category: 'tops' },
    })
  })

  it('deleteWardrobeItem calls DELETE /api/wardrobe/:id', async () => {
    apiClient.delete.mockResolvedValue({})

    await deleteWardrobeItem('item-abc')

    expect(apiClient.delete).toHaveBeenCalledWith('/api/wardrobe/item-abc')
  })
})

describe('outfits API', () => {
  beforeEach(() => vi.clearAllMocks())

  it('listOutfits calls GET /api/outfits', async () => {
    apiClient.get.mockResolvedValue({ data: { outfits: [], total: 0 } })

    await listOutfits()

    expect(apiClient.get).toHaveBeenCalledWith('/api/outfits', { params: {} })
  })

  it('createOutfit calls POST /api/outfits', async () => {
    const payload = { name: 'Summer look', item_ids: ['i1', 'i2'] }
    apiClient.post.mockResolvedValue({ data: { id: 'o1', ...payload } })

    const result = await createOutfit(payload)

    expect(apiClient.post).toHaveBeenCalledWith('/api/outfits', payload)
    expect(result.id).toBe('o1')
  })

  it('generateOutfits calls POST /api/outfits/generate', async () => {
    apiClient.post.mockResolvedValue({ data: { outfits: [] } })

    await generateOutfits({ occasion: 'casual' })

    expect(apiClient.post).toHaveBeenCalledWith('/api/outfits/generate', {
      occasion: 'casual',
    })
  })
})

describe('laundry API', () => {
  beforeEach(() => vi.clearAllMocks())

  it('getLaundryStatus calls GET /api/laundry', async () => {
    apiClient.get.mockResolvedValue({ data: { items: [] } })

    await getLaundryStatus()

    expect(apiClient.get).toHaveBeenCalledWith('/api/laundry')
  })

  it('markAllClean calls POST /api/laundry/reset', async () => {
    apiClient.post.mockResolvedValue({ data: { reset_count: 5 } })

    await markAllClean()

    expect(apiClient.post).toHaveBeenCalledWith('/api/laundry/reset')
  })
})
