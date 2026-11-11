export const brl = (v) => (v == null ? "—" : v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" }))

// "2026-11-10 22:49" no fuso local (sv-SE já formata no padrão ISO)
export const dt = (ts) => new Date(ts * 1000).toLocaleString("sv-SE").slice(0, 16)

export const pad = (n) => String(n).padStart(2, "0")
