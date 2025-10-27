<template>
  <div class="bg-white rounded-xl shadow-md p-6">
    <div class="mb-4 border-b pb-2">
      <h2 class="text-2xl font-bold">Session #{{ id }}</h2>
    </div>

    <div class="text-gray-600">
      Status:
      <span :class="['px-2 py-0.5 rounded', badgeClass(status)]">{{ status }}</span>
      <span v-if="progress != null"> · {{ progress }}%</span>
    </div>

    <div class="mt-4 flex gap-2">
      <base-button v-if="status === 'PENDING'" @click="run">Start analysis</base-button>
      <router-link v-if="status === 'DONE'" :to="`/async/sessions/${id}/feedback`">
        <base-button>View Feedback</base-button>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute, RouterLink } from "vue-router"; // RouterLink in scope
import { getSession, getStatus, startSession } from "../api/asyncSessions";
import { usePolling } from "../usePolling";

// Pfad ggf. an euer Projekt anpassen:
import BaseButton from "@/BaseComponents/BaseButton.vue";

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
  await start();
}

onMounted(async () => {
  const { data } = await getSession(id);
  status.value = data?.status ?? "PENDING";
  if (status.value === "RUNNING") await start();
});
</script>
