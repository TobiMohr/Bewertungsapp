<template>
  <BaseCard>
    <template #header><h2>Session #{{ id }}</h2></template>
    <div class="text-gray-600">
      Status:
      <span :class="['px-2 py-0.5 rounded', badgeClass(status)]">{{ status }}</span>
      <span v-if="progress != null"> · {{ progress }}%</span>
    </div>

    <div class="mt-4 flex gap-2">
      <BaseButton v-if="status === 'PENDING'" @click="run">Start analysis</BaseButton>
      <RouterLink v-if="status === 'DONE'" :to="`/async/sessions/${id}/feedback`">
        <BaseButton>View Feedback</BaseButton>
      </RouterLink>
    </div>
  </BaseCard>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { getSession, getStatus, startSession } from "../api/asyncSessions";
import { usePolling } from "../usePolling";

// ✅ Lokale Importe für Basis-Komponenten
import BaseCard from "@/components/BaseCard.vue";
import BaseButton from "@/components/BaseButton.vue";

const route = useRoute();
const id = route.params.id;
const status = ref("PENDING");
const progress = ref(null);

const badgeClass = (s) =>
    ({
      PENDING: "bg-gray-100 text-gray-700",
      RUNNING: "bg-yellow-100 text-yellow-700",
      DONE: "bg-green-100 text-green-700",
      FAILED: "bg-red-100 text-red-700",
    }[s] || "bg-gray-100 text-gray-700");

const { start, stop } = usePolling(async () => {
  const { data } = await getStatus(id);
  status.value = data.status;
  progress.value = data.progress ?? null;
  if (data.status !== "RUNNING") stop();
}, 1500);

async function run() {
  await startSession(id);
  status.value = "RUNNING";
  start();
}

onMounted(async () => {
  const { data } = await getSession(id);
  status.value = data?.status ?? "PENDING";
  if (status.value === "RUNNING") start();
});
</script>
