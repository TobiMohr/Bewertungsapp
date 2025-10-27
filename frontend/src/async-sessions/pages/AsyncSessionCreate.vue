<template>
  <div class="max-w-4xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Create Async Session</h2>
    </div>

    <form @submit.prevent="submit" class="space-y-6">
      <!-- Channel ID -->
      <div>
        <label class="block mb-2 font-semibold">Discord Channel ID</label>
        <BaseInput
            v-model="channelId"
            placeholder="z. B. 123456789012345678"
            class="w-full"
            required
        />
      </div>

      <!-- Criteria (multi) -->
      <div>
        <label class="block mb-2 font-semibold">Criteria (multi)</label>
        <select
            v-model="criteriaIds"
            multiple
            class="w-full border border-gray-300 rounded-lg p-2 h-28"
        >
          <option v-for="c in allCriteria" :key="c.id" :value="c.id">
            {{ c.name }}
          </option>
        </select>
        <p class="text-sm text-gray-500 mt-1">
          Halte Strg/Cmd für Mehrfachauswahl.
        </p>
      </div>

      <div class="flex items-center gap-3 pt-2">
        <BaseButton type="submit" :disabled="saving">
          {{ saving ? "Creating…" : "Create" }}
        </BaseButton>

        <RouterLink to="/async/sessions">
          <BaseButton variant="cancel" type="button">Cancel</BaseButton>
        </RouterLink>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import BaseButton from "@/BaseComponents/BaseButton.vue";
import BaseInput from "@/BaseComponents/BaseInput.vue";
import { createSession } from "../api/asyncSessions";

// MVP-Kriterien (statisch). Später ggf. via getCriterias() laden.
const allCriteria = ref([
  { id: "clarity",   name: "Clarity" },
  { id: "tone",      name: "Tone" },
  { id: "relevance", name: "Relevance" },
]);

const router = useRouter();
const channelId = ref("");
const criteriaIds = ref(["clarity", "tone", "relevance"]);
const saving = ref(false);

async function submit() {
  if (!channelId.value?.trim()) return;
  saving.value = true;
  try {
    const { data } = await createSession({
      channel_id: channelId.value.trim(),
      criteria_ids: criteriaIds.value,
    });
    router.push(`/async/sessions/${data.id}`);
  } finally {
    saving.value = false;
  }
}
</script>
