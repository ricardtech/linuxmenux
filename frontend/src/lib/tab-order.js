const STORAGE_KEY = 'linuxmenux-tab-order'
export const DEFAULT_TAB_ORDER = ['overview', 'apps', 'containers', 'node', 'backup', 'terminal', 'admin']

export function loadTabOrder() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return [...DEFAULT_TAB_ORDER]
    const parsed = JSON.parse(raw)
    if (Array.isArray(parsed) && parsed.length === DEFAULT_TAB_ORDER.length) {
      return parsed
    }
  } catch {
    // ignore
  }
  return [...DEFAULT_TAB_ORDER]
}

export function saveTabOrder(order) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(order))
    window.dispatchEvent(new CustomEvent('linuxmenux:tab-order-changed', { detail: order }))
  } catch {
    // ignore
  }
}
