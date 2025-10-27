<template>
  <BaseCard>
    <template #header><h2>Feedback</h2></template>
    <p class="mb-4 whitespace-pre-wrap">{{ feedback?.summaryText }}</p>
    <ul class="divide-y">
      <li v-for="b in feedback?.criteriaBreakdown ?? []" :key="b.criterionId" class="py-2 flex items-center justify-between">
        <span>{{ b.criterionName }}</span>
        <span class="font-medium">{{ b.score }}</span>
      </li>
    </ul>
  </BaseCard>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { getFeedback } from "../api/asyncSessions";
const route = useRoute(); const feedback = ref(null);
onMounted(async () => {
  const { data } = await getFeedback(route.params.id);
  feedback.value = data;
});
</script>
