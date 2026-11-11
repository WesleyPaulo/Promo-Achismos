<script setup>
import { ref } from "vue"
import { api } from "../services/api"
import { brl, pad } from "../utils/format"

defineProps({ items: Array })
const emit = defineEmits(["changed"])

const terms = ref("")
const maxPrice = ref("")
const erro = ref("")

async function add() {
  const r = await api("/api/items", "POST", { terms: terms.value, max_price: maxPrice.value === "" ? null : Number(maxPrice.value) })
  erro.value = r.ok ? "" : r.status === 409 ? "erro: item já cadastrado" : "erro: dados inválidos"
  if (!r.ok) return
  terms.value = maxPrice.value = ""
  emit("changed")
}

async function remove(id) {
  await api(`/api/items/${id}`, "DELETE")
  emit("changed")
}
</script>

<template>
  <div class="card">
    <h2 class="card-title"><span class="text-neon">&gt;</span> itens_de_interesse</h2>
    <p class="hint">// todas as palavras precisam aparecer na mensagem · preço máximo é opcional</p>

    <form class="mt-5 flex flex-wrap gap-2" @submit.prevent="add">
      <input v-model="terms" class="input min-w-0 flex-1" placeholder="ex: rtx 4070" aria-label="Termos" required>
      <div class="relative w-40">
        <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-xs text-purple-400">R$</span>
        <input v-model="maxPrice" class="input w-full pl-9" type="number" min="0" step="0.01" placeholder="máx." aria-label="Preço máximo (opcional)">
      </div>
      <button class="btn">
        <svg class="size-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><path d="M12 5v14M5 12h14" /></svg>
        Adicionar
      </button>
    </form>
    <p v-if="erro" class="mt-2 text-xs text-red-400" role="alert">{{ erro }}</p>

    <ul class="mt-5 grid gap-2 sm:grid-cols-2">
      <li v-for="(i, n) in items" :key="i.id" class="flex items-center gap-3 rounded-sm border border-purple-900/60 bg-black/50 px-3 py-2.5 transition hover:border-purple-500/80">
        <span class="text-xs text-purple-500">{{ pad(items.length - n) }}</span>
        <span class="min-w-0 flex-1 truncate text-sm text-zinc-100">{{ i.terms }}</span>
        <span v-if="i.max_price != null" class="rounded-sm border border-neon/40 bg-neon/5 px-2 py-0.5 text-[11px] text-neon">≤ {{ brl(i.max_price) }}</span>
        <button class="rounded-sm p-1 text-zinc-600 transition hover:bg-red-500/10 hover:text-red-400" :aria-label="`Remover ${i.terms}`" @click="remove(i.id)">
          <svg class="size-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12" /></svg>
        </button>
      </li>
    </ul>
    <p v-if="!items.length" class="mt-5 text-xs text-zinc-500">// nenhum item cadastrado</p>
  </div>
</template>
