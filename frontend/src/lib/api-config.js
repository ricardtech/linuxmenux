const TOKEN_KEY = 'linuxmenux-token'

export function getAuthToken() {
  try {
    return localStorage.getItem(TOKEN_KEY) || ''
  } catch {
    return ''
  }
}

export function setAuthToken(token) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token)
    else localStorage.removeItem(TOKEN_KEY)
  } catch {
    // ignore storage quota errors
  }
}

export async function fetchApi(path, options = {}) {
  const token = getAuthToken()
  const headers = { ...(options.headers || {}) }
  if (token && !headers.Authorization) {
    headers.Authorization = `Bearer ${token}`
  }
  const res = await fetch(path, { ...options, headers })
  if (res.status === 401) {
    window.dispatchEvent(new CustomEvent('linuxmenux:unauthorized'))
  }
  return res
}
