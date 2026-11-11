<script setup>
import { onMounted, onUnmounted, ref, watch } from "vue"
import { getJson } from "../services/api"
import { brl, dt, pad } from "../utils/format"

defineProps({ items: Array, channels: Array })

const blank = () => ({ q: "", item: "", channel: "", min: "", max: "", from: "", to: "" })
const f = ref(blank())
const hits = ref([])

async function load() {
  const p = { ...f.value }
  if (p.from) p.from = Date.parse(`${p.from}T00:00`) / 1000 // datas locais -> epoch
  if (p.to) p.to = Date.parse(`${p.to}T23:59:59`) / 1000
  const qs = new URLSearchParams(Object.entries(p).filter(([, v]) => v !== ""))
  hits.value = await getJson(`/api/hits?${qs}`)
}

watch(f, load, { deep: true })
let timer
onMounted(() => {
  load()
  timer = setInterval(load, 30000)
})
onUnmounted(() => clearInterval(timer))
</script>

<template>
  <div class="card">
    <div class="flex flex-wrap items-baseline justify-between gap-2">
      <h2 class="card-title"><span class="text-neon">&gt;</span> historico_de_avisos</h2>
      <span class="text-xs text-zinc-500">[{{ pad(hits.length) }}{{ hits.length === 500 ? "+" : "" }}] registros</span>
    </div>
    <p class="hint">// atualiza a cada 30s · mostra os 500 mais recentes</p>

    <div class="mt-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
      <input v-model="f.q" class="input" placeholder="buscar no texto..." aria-label="Buscar no texto">
      <select v-model="f.item" class="input" aria-label="Item">
        <option value="">item: todos</option>
        <option v-for="i in items" :key="i.id">{{ i.terms }}</option>
      </select>
      <select v-model="f.channel" class="input" aria-label="Canal">
        <option value="">canal: todos</option>
        <option v-for="c in channels" :key="c.id" :value="c.id">{{ c.title }}</option>
      </select>
      <div class="flex gap-2">
        <input v-model="f.min" class="input w-full" type="number" min="0" placeholder="R$ mín" aria-label="Preço mínimo">
        <input v-model="f.max" class="input w-full" type="number" min="0" placeholder="R$ máx" aria-label="Preço máximo">
      </div>
      <label class="flex items-center gap-2 text-xs tracking-widest text-purple-400 uppercase">de <input v-model="f.from" class="input flex-1" type="date"></label>
      <label class="flex items-center gap-2 text-xs tracking-widest text-purple-400 uppercase">até <input v-model="f.to" class="input flex-1" type="date"></label>
      <div class="flex gap-2 lg:col-span-2">
        <button class="btn-ghost" @click="f = blank()">Limpar</button>
        <button class="btn-ghost" @click="load">
          <svg class="size-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a9 9 0 1 1-3-6.7L21 8" /><path d="M21 3v5h-5" /></svg>
          Atualizar
        </button>
      </div>
    </div>

    <div class="mt-5 overflow-x-auto">
      <table class="w-full min-w-[48rem] text-left text-sm [&_td]:py-2.5 [&_th]:py-2">
        <thead class="border-b border-purple-900/70 text-[11px] tracking-widest text-purple-400 uppercase">
          <tr><th class="pr-4 font-medium">Timestamp</th><th class="pr-4 font-medium">Item</th><th class="pr-4 font-medium">Canal</th><th class="pr-4 font-medium">Preço</th><th class="font-medium">Mensagem</th></tr>
        </thead>
        <tbody class="divide-y divide-zinc-800/80">
          <tr v-for="h in hits" :key="h.id" class="align-top transition hover:bg-purple-950/40">
            <td class="pr-4 whitespace-nowrap text-zinc-500">{{ dt(h.ts) }}</td>
            <td class="pr-4 whitespace-nowrap text-zinc-100">{{ h.terms }}</td>
            <td class="pr-4 text-purple-200">{{ h.channel }}</td>
            <td class="pr-4 whitespace-nowrap text-neon">{{ brl(h.price) }}</td>
            <td><a :href="h.link" target="_blank" rel="noopener" class="text-zinc-400 transition hover:text-neon">{{ h.text.slice(0, 140) || "abrir" }}</a></td>
          </tr>
          <tr v-if="!hits.length"><td colspan="5" class="py-8 text-center text-xs text-zinc-500">// nenhum aviso encontrado</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
