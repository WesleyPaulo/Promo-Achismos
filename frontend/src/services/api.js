export const api = (url, method = "GET", body) =>
  fetch(url, { method, body: body && JSON.stringify(body) })

export async function getJson(url) {
  const r = await api(url)
  if (!r.ok) throw new Error(`HTTP ${r.status}`) // ex.: 502 do nginx com o backend fora
  return r.json()
}
