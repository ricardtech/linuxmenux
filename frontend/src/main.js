import { createApp } from 'vue'
import App from './App.vue'
import './style.css'
import { getAuthToken } from './lib/api-config'

// Global fetch interceptor: attach Bearer JWT to all /api/ calls automatically
const originalFetch = window.fetch.bind(window)
window.fetch = async (input, init = {}) => {
  const url = typeof input === 'string' ? input : (input?.url || '')
  if (url.startsWith('/api/')) {
    const token = getAuthToken()
    const headers = new Headers(init.headers || (typeof input !== 'string' ? input.headers : undefined) || {})
    if (token && !headers.has('Authorization')) {
      headers.set('Authorization', `Bearer ${token}`)
    }
    const res = await originalFetch(input, { ...init, headers })
    if (res.status === 401 && !url.startsWith('/api/auth/')) {
      window.dispatchEvent(new CustomEvent('linuxmenux:unauthorized'))
    }
    return res
  }
  return originalFetch(input, init)
}

createApp(App).mount('#app')
