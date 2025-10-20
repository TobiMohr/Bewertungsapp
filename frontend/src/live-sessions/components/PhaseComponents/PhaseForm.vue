<template>
  <div class="max-w-2xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-6">Create Phase</h2>

    <!-- Show info if child phase -->
    <div v-if="phase.parent_id" class="mb-4 text-sm text-gray-600 bg-gray-50 p-3 rounded">
      This phase will be created as a <strong>child</strong> of:
      <span class="font-semibold">{{ parentPhaseTitle }}</span>
    </div>

    <form @submit.prevent="submitForm" class="space-y-6">
      <!-- Title -->
      <div>
        <label class="block mb-2 font-semibold">Title</label>
        <input
          v-model="phase.title"
          type="text"
          class="w-full border border-gray-300 rounded-lg p-2"
          placeholder="Phase Title"
          required
        />
      </div>

      <!-- Description -->
      <div>
        <label class="block mb-2 font-semibold">Description</label>
        <textarea
          v-model="phase.description"
          class="w-full border border-gray-300 rounded-lg p-2"
          rows="4"
          placeholder="Description (optional)"
        ></textarea>
      </div>

      <!-- Criteria -->
      <div>
        <h3 class="text-lg font-semibold text-gray-700 mb-4">Select Criteria</h3>
        <div class="flex flex-col space-y-3">
          <div
            v-for="crit in criteria"
            :key="crit.id"
            class="flex items-center justify-between space-x-4"
          >
            <span class="text-gray-800 w-1/3">{{ crit.name }}</span>
            <BaseToggle v-model="checkedCriteria[crit.id]" />
            <input
              v-if="checkedCriteria[crit.id]"
              type="number"
              min="1"
              v-model.number="criteriaWeights[crit.id]"
              class="border rounded px-2 py-1 w-20 text-center"
            />
          </div>
        </div>
      </div>

      <!-- Buttons -->
      <div class="flex justify-between pt-4">
        <BaseButton type="button" variant="cancel" @click="$router.push('/sessions')">
          Cancel
        </BaseButton>
        <BaseButton type="submit">Create Phase</BaseButton>
      </div>
    </form>
  </div>
</template>

<script>
import BaseButton from "@/BaseComponents/BaseButton.vue";
import BaseToggle from "@/BaseComponents/BaseToggle.vue";
import { getCriterias } from "@/live-sessions/api/criterias";
import { createPhase } from "@/live-sessions/api/phases";

export default {
  components: { BaseButton, BaseToggle },
  data() {
    return {
      phase: {
        title: "",
        description: "",
        session_id: null,
        parent_id: null, // <-- added
      },
      parentPhaseTitle: null, // for display
      criteria: [],
      checkedCriteria: {},
      criteriaWeights: {},
    };
  },
  methods: {
    async fetchCriteria() {
      try {
        const res = await getCriterias();
        this.criteria = res.data;

        this.checkedCriteria = Object.fromEntries(this.criteria.map(c => [c.id, true]));
        this.criteriaWeights = Object.fromEntries(this.criteria.map(c => [c.id, 1]));
      } catch (err) {
        console.error("Failed to fetch criteria:", err);
      }
    },
    async submitForm() {
      try {
        const payload = {
          ...this.phase,
          criteria: Object.entries(this.checkedCriteria)
            .filter(([, checked]) => checked)
            .map(([id]) => ({
              id: Number(id),
              weight: this.criteriaWeights[id] || 1,
            })),
        };

        await createPhase(payload);
        this.$router.push(`/sessions/edit/${this.phase.session_id}`);
      } catch (err) {
        console.error("Failed to create phase:", err);
        alert(err.response?.data?.detail || "Failed to create phase");
      }
    },
  },
  async mounted() {
    const sessionId = Number(this.$route.query.sessionId);
    const parentId = this.$route.query.parentId ? Number(this.$route.query.parentId) : null;

    if (!sessionId) {
      alert("No session selected for this phase");
      this.$router.push("/sessions");
      return;
    }

    this.phase.session_id = sessionId;
    this.phase.parent_id = parentId;

    if (parentId) {
      try {
        const { getPhase } = await import("../../api/phases");
        const parentRes = await getPhase(parentId);
        this.parentPhaseTitle = parentRes.data.title;
      } catch {
        this.parentPhaseTitle = "(unknown)";
      }
    }

    this.fetchCriteria();
  },
};
</script>
