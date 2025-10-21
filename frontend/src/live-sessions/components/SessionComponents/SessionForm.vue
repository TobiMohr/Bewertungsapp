<template>
  <div class="max-w-2xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-6">Create Session</h2>

    <!-- Show info if child session -->
    <div v-if="session.parent_id" class="mb-4 text-sm text-gray-600 bg-gray-50 p-3 rounded">
      This session will be created as a <strong>child</strong> of:
      <span class="font-semibold">{{ parentSessionTitle }}</span>
    </div>

    <form @submit.prevent="submitForm" class="space-y-6">
      <!-- Session Title -->
      <div>
        <label class="block mb-2 font-semibold">Title</label>
        <input
          v-model="session.title"
          type="text"
          class="w-full border border-gray-300 rounded-lg p-2"
          placeholder="Session Title"
          required
        />
      </div>

      <!-- Session Description -->
      <div>
        <label class="block mb-2 font-semibold">Description</label>
        <textarea
          v-model="session.description"
          class="w-full border border-gray-300 rounded-lg p-2"
          rows="4"
          placeholder="Description (optional)"
        ></textarea>
      </div>

      <!-- Criteria Selection -->
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
        <BaseButton type="submit">Create Session</BaseButton>
      </div>
    </form>
  </div>
</template>

<script>
import BaseButton from "@/BaseComponents/BaseButton.vue";
import BaseToggle from "@/BaseComponents/BaseToggle.vue";
import { getCriterias } from "@/live-sessions/api/criterias";
import { getSession, createSession } from "@/live-sessions/api/sessions";

export default {
  components: { BaseButton, BaseToggle },
  data() {
    return {
      session: {
        title: "",
        description: "",
        parent_id: null, // child session support
      },
      parentSessionTitle: null,
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
        console.error("Failed to load criteria", err);
      }
    },
    async fetchParentTitle(parentId) {
      try {
        const res = await getSession(parentId);
        this.parentSessionTitle = res.data.title;
      } catch {
        this.parentSessionTitle = "(unknown)";
      }
    },
    async submitForm() {
      try {
        const payload = {
          ...this.session,
          criteria: Object.entries(this.checkedCriteria)
            .filter(([, checked]) => checked)
            .map(([id]) => ({
              id: Number(id),
              weight: this.criteriaWeights[id] || 1,
            })),
        };
        await createSession(payload);
        this.$router.push("/sessions");
      } catch (err) {
        console.error("Failed to create session:", err);
        alert(err.response?.data?.detail || "Failed to create session");
      }
    },
  },
  async mounted() {
    const parentId = this.$route.query.parentId ? Number(this.$route.query.parentId) : null;
    if (parentId) {
      this.session.parent_id = parentId;
      await this.fetchParentTitle(parentId);
    }
    this.fetchCriteria();
  },
};
</script>
