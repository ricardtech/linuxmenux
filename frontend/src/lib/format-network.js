export function formatNetworkBytes(bytes, unit = 'bytes') {
  const b = Number(bytes || 0)
  if (unit === 'bits') {
    const bits = b * 8
    if (bits >= 1e9) return `${(bits / 1e9).toFixed(2)} Gb`
    if (bits >= 1e6) return `${(bits / 1e6).toFixed(2)} Mb`
    if (bits >= 1e3) return `${(bits / 1e3).toFixed(1)} Kb`
    return `${bits} b`
  }
  if (b >= 1024 ** 3) return `${(b / 1024 ** 3).toFixed(2)} GB`
  if (b >= 1024 ** 2) return `${(b / 1024 ** 2).toFixed(2)} MB`
  if (b >= 1024) return `${(b / 1024).toFixed(1)} KB`
  return `${Math.round(b)} B`
}
