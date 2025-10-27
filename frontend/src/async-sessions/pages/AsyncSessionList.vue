<template>
  <BaseCard>
    <template #header>
      <div class="flex items-center justify-between">
        <h2>Async Sessions</h2>
        <RouterLink to="/async/create"><BaseButton>New</BaseButton></RouterLink>
      </div>
    </template>

    <div v-if="loading" class="py-6 text-center">Loading…</div>
    <div v-else-if="!items.length" class="py-6 text-center text-gray-500">No sessions found.</div>

    <ul v-else class="divide-y">
      <li v-for="s in items" :key="s.id" class="py-3 flex items-center justify-between">
        <div>
          <div class="font-medium">#{{ s.id }} – {{ s.channelName }}</div>
          <div class="text-sm text-gray-500">
            Status:
            <span :class="['px-2 py-0.5 rounded', badgeClass(s.status)]">{{ s.status }}</span>
            · {{ new Date(s.createdAt).toLocaleString() }}
          </div>
        </div>
        <div class="flex gap-2">
          <RouterLink :to="`/async/sessions/${s.id}`"><BaseButton variant="ghost">Detail</BaseButton></RouterLink>
          <RouterLink :to="`/async/sessions/${s.id}/feedback`" v-if="s.status==='DONE'">
            <BaseButton>Feedback</BaseButton>
          </RouterLink>
        </div>
      </li>
    </ul>
  </BaseCard>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { getSessions } from "../api/asyncSessions";

const items = ref([]); const loading = ref(true);
const badgeClass = (s) => ({
  PENDING: "bg-gray-100 text-gray-700",
  RUNNING: "bg-yellow-100 text-yellow-700",
  DONE:    "bg-green-100 text-green-700",
  FAILED:  "bg-red-100 text-red-700",
}[s] || "bg-gray-100 text-gray-700");

onMounted(async () => {
  const { data } = await getSessions();
  items.value = data;
  loading.value = false;
});
</script>
