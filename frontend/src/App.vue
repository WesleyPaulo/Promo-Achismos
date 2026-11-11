<script setup>
import { computed, onMounted, ref, watch } from "vue"
import { getJson } from "./services/api"
import { pad } from "./utils/format"
import ItemsCard from "./components/ItemsCard.vue"
import ChannelsCard from "./components/ChannelsCard.vue"
import HistoryCard from "./components/HistoryCard.vue"

const items = ref([])
const channels = ref([])
const online = ref(null)

const loadItems = async () => (items.value = await getJson("/api/items"))
const loadChannels = async () => (channels.value = await getJson("/api/channels"))

const tabs = computed(() => [
  { id: "itens", label: "Itens", count: pad(items.value.length) },
  { id: "canais", label: "Canais", count: `${pad(channels.value.filter((c) => c.enabled).length)}/${pad(channels.value.length)}` },
  { id: "historico", label: "Histórico" },
])
const tab = ref(location.hash.slice(1) || "itens")
watch(tab, (t) => history.replaceState(null, "", `#${t}`))

onMounted(async () => {
  try {
    await Promise.all([loadItems(), loadChannels()])
    online.value = true
  } catch {
    online.value = false
  }
})
</script>

<template>
  <main class="mx-auto max-w-6xl px-4 py-8">
    <header class="mb-8 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <div class="grid size-11 place-items-center rounded-sm border border-neon/40 bg-neon/5 text-neon shadow-[0_0_20px_-4px_rgb(57_255_20/0.5)]">
          <svg class="size-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M19.07 4.93A10 10 0 0 0 6.99 3.34" /><path d="M4 6h.01" /><path d="M2.29 9.62A10 10 0 1 0 21.31 8.35" />
            <path d="M16.24 7.76A6 6 0 1 0 8.23 16.67" /><path d="M12 18h.01" /><path d="M17.99 11.66A6 6 0 0 1 15.77 16.67" />
            <circle cx="12" cy="12" r="2" /><path d="m13.41 10.59 5.66-5.66" />
          </svg>
        </div>
        <div>
          <h1 class="text-xl font-bold tracking-tight text-zinc-100">
            PROMO<span class="text-neon drop-shadow-[0_0_8px_rgb(57_255_20/0.6)]">_ACHISMOS</span><span class="cursor text-neon">▌</span>
          </h1>
          <p class="text-xs text-zinc-500">// monitor de promoções no telegram</p>
        </div>
      </div>
      <div class="flex items-center gap-2 rounded-sm border border-purple-800/60 bg-black/60 px-3 py-1.5 text-[11px] tracking-widest uppercase" role="status">
        <span class="relative flex size-2">
          <span v-if="online" class="absolute inline-flex size-full animate-ping rounded-full bg-neon opacity-75"></span>
          <span class="relative inline-flex size-2 rounded-full" :class="online ? 'bg-neon' : online === false ? 'bg-red-500' : 'bg-zinc-600'"></span>
        </span>
        <span :class="online ? 'text-neon' : online === false ? 'text-red-400' : 'text-zinc-500'">
          API {{ online ? "online" : online === false ? "offline" : "..." }}
        </span>
      </div>
    </header>

    <nav class="mb-6 flex gap-1 overflow-x-auto border-b border-purple-900/60" role="tablist" aria-label="Seções">
      <button
        v-for="(t, i) in tabs"
        :id="`tab-${t.id}`"
        :key="t.id"
        role="tab"
        :aria-selected="tab === t.id"
        :aria-controls="`panel-${t.id}`"
        class="-mb-px flex items-center gap-2 border-b-2 px-4 py-3 text-xs font-bold tracking-[0.18em] whitespace-nowrap uppercase transition"
        :class="tab === t.id ? 'border-neon bg-linear-to-t from-neon/10 to-transparent text-neon' : 'border-transparent text-zinc-500 hover:border-purple-500 hover:text-purple-200'"
        @click="tab = t.id"
      >
        <span class="font-normal text-purple-500">{{ pad(i + 1) }}</span>
        {{ t.label }}
        <span v-if="t.count" class="rounded-sm border border-purple-700/60 px-1.5 text-[10px] font-normal text-purple-200">{{ t.count }}</span>
      </button>
    </nav>

    <section v-show="tab === 'itens'" id="panel-itens" role="tabpanel" aria-labelledby="tab-itens">
      <ItemsCard :items="items" @changed="loadItems" />
    </section>
    <section v-show="tab === 'canais'" id="panel-canais" role="tabpanel" aria-labelledby="tab-canais">
      <ChannelsCard :channels="channels" @changed="loadChannels" />
    </section>
    <section v-show="tab === 'historico'" id="panel-historico" role="tabpanel" aria-labelledby="tab-historico">
      <HistoryCard :items="items" :channels="channels" />
    </section>
  </main>
</template>
