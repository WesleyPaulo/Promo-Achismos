import { brl } from "../utils/format"

// Notificações nativas do navegador. Funcionam com o site aberto em alguma aba (mesmo em segundo plano).
// Exigem contexto seguro: http://localhost ou HTTPS.
const KEY = "promo.notify"
const MAX_INDIVIDUAL = 3

export const supported = "Notification" in window

export const permission = () => (supported ? Notification.permission : "unsupported")

export function isOn() {
  try {
    return permission() === "granted" && localStorage.getItem(KEY) !== "off"
  } catch {
    return permission() === "granted"
  }
}

export async function setOn(on) {
  if (on && permission() !== "granted") on = (await Notification.requestPermission()) === "granted"
  try {
    localStorage.setItem(KEY, on ? "on" : "off")
  } catch {
    /* sem storage: vale só nesta sessão */
  }
  return on
}

function show(title, body, tag, link) {
  const n = new Notification(title, { body, tag })
  n.onclick = () => {
    window.focus()
    if (link) window.open(link, "_blank", "noopener")
    n.close()
  }
}

export function notifyHits(hits) {
  for (const h of hits.slice(0, MAX_INDIVIDUAL)) {
    show(`${h.terms} · ${brl(h.price)}`, `${h.channel}\n${h.text.slice(0, 140)}`, `hit-${h.id}`, h.link)
  }
  if (hits.length > MAX_INDIVIDUAL) {
    show(`+${hits.length - MAX_INDIVIDUAL} ocorrências`, "Veja a aba Histórico", "hit-more")
  }
}
