<template>
  <div class="max-w-7xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Feedback</h2>

      <div class="flex items-center gap-2">
        <span
            :class="[
            'px-2 py-0.5 rounded text-sm',
            approved ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
          ]"
        >
          {{ approved ? 'Approved' : 'Not approved' }}
        </span>

        <router-link :to="`/async/sessions/${id}`">
          <BaseButton variant="cancel" type="button">Back</BaseButton>
        </router-link>
      </div>
    </div>

    <!-- Summary -->
    <p class="mb-6 text-gray-600">
      {{ feedback?.summaryText || '—' }}
    </p>

    <!-- Kriterien mit +/- -->
    <ul class="divide-y">
      <li
          v-for="(b, idx) in editedBreakdown"
          :key="b.criterionId || idx"
          class="py-3 flex items-center justify-between"
      >
        <div class="font-medium text-gray-800">
          {{ b.criterionName }}
        </div>

        <div class="flex items-center gap-2">
          <BaseButton
              variant="cancel"
              class="px-2"
              :disabled="approved"
              @click="decrement(idx)"
              title="Decrease"
          >−</BaseButton>

          <span
              :class="[
              'min-w-[3rem] text-center px-2 py-1 rounded',
              scoreClass(b.score)
            ]"
          >
            {{ b.score }}
          </span>

          <BaseButton
              class="px-2"
              :disabled="approved"
              @click="increment(idx)"
              title="Increase"
          >+</BaseButton>
        </div>
      </li>
    </ul>

    <!-- Aktionen -->
    <div class="mt-6 flex gap-2">
      <BaseButton
          :disabled="saving || approved"
          @click="saveEdits"
          variant="copy"
          title="Speichert nur die Änderungen (ohne Approve)"
      >
        {{ saving ? 'Saving…' : 'Save' }}
      </BaseButton>

      <BaseButton
          :disabled="approving || approved"
          @click="approve"
          title="Speichern & Approven"
      >
        {{ approving ? 'Approving…' : 'Approve' }}
      </BaseButton>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRoute, RouterLink } from 'vue-router';
import BaseButton from '@/BaseComponents/BaseButton.vue';

// Mock-API
import { getFeedback, getSession, updateFeedback, approveSession } from '../api/asyncSessions';

const route = useRoute();
const id = route.params.id;

const feedback = ref(null);
const editedBreakdown = ref([]);
const approved = ref(false);
const saving = ref(false);
const approving = ref(false);

function scoreClass(s) {
  if (s >= 80) return 'bg-green-100 text-green-700';
  if (s >= 60) return 'bg-yellow-100 text-yellow-700';
  return 'bg-red-100 text-red-700';
}

function clamp(n) { return Math.max(0, Math.min(100, n)); }
function increment(idx) { editedBreakdown.value[idx].score = clamp(editedBreakdown.value[idx].score + 1); }
function decrement(idx) { editedBreakdown.value[idx].score = clamp(editedBreakdown.value[idx].score - 1); }

async function load() {
  const [fbRes, sessRes] = await Promise.all([getFeedback(id), getSession(id)]);
  feedback.value = fbRes.data;
  approved.value = !!(sessRes.data?.approved);
  editedBreakdown.value = JSON.parse(JSON.stringify(fbRes.data?.criteriaBreakdown ?? []));
}

async function saveEdits() {
  saving.value = true;
  try {
    await updateFeedback(id, { criteriaBreakdown: editedBreakdown.value });
  } finally {
    saving.value = false;
  }
}

async function approve() {
  approving.value = true;
  try {
    // Speichert die aktuellen Werte und markiert Session als approved
    await approveSession(id, { criteriaBreakdown: editedBreakdown.value });
    approved.value = true;
  } finally {
    approving.value = false;
  }
}

onMounted(load);
</script>
