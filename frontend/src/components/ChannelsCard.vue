<script setup>
import { api } from "../services/api"

defineProps({ channels: Array })
const emit = defineEmits(["changed"])

async function toggle(c) {
  await api(`/api/channels/${c.id}`, "POST")
  emit("changed")
}
</script>

<template>
  <div class="card">
    <h2 class="card-title"><span class="text-neon">&gt;</span> canais_monitorados</h2>
    <p class="hint">// clique para ligar/desligar · também pelo bot com <span class="text-purple-300">/canais</span></p>

    <div class="mt-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
      <button
        v-for="c in channels"
        :key="c.id"
        :aria-pressed="!!c.enabled"
        class="flex items-center gap-3 rounded-sm border px-3 py-2.5 text-left text-sm transition"
        :class="c.enabled ? 'border-neon/40 bg-neon/5 text-zinc-100 hover:shadow-[0_0_14px_-2px_rgb(57_255_20/0.4)]' : 'border-zinc-800 bg-black/40 text-zinc-500 hover:border-purple-700'"
        @click="toggle(c)"
      >
        <span class="size-2 shrink-0 rounded-full" :class="c.enabled ? 'bg-neon shadow-[0_0_8px_rgb(57_255_20)]' : 'bg-zinc-700'"></span>
        <span class="min-w-0 flex-1 truncate">{{ c.title }}</span>
        <span class="text-[10px] tracking-widest" :class="c.enabled ? 'text-neon' : 'text-zinc-600'">{{ c.enabled ? "ON" : "OFF" }}</span>
      </button>
    </div>
    <p v-if="!channels.length" class="mt-5 text-xs text-zinc-500">// os canais aparecem depois do primeiro login no telegram</p>
  </div>
</template>
