export const api = (url, method = "GET", body) =>
  fetch(url, { method, body: body && JSON.stringify(body) })

export const getJson = async (url) => (await api(url)).json()
