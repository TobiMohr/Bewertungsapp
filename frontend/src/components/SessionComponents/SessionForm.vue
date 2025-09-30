<template>
  <div class="max-w-2xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-6">Create Session</h2>

    <form @submit.prevent="submitForm" class="space-y-6">
      <!-- Title -->
      <BaseInput
        v-model="session.title"
        placeholder="Session Title"
        required
      />

      <!-- Description -->
      <BaseInput
        v-model="session.description"
        placeholder="Description (optional)"
      />

        <!-- Criteria selection -->
      <div>
        <h3 class="text-lg font-semibold text-gray-700 mb-4">
          Select Criteria
        </h3>
        <div class="flex flex-col space-y-3">
          <div
            v-for="crit in criteria"
            :key="crit.id"
            class="flex items-center justify-between space-x-4"
          >
            <span class="text-gray-800 w-1/3">{{ crit.name }}</span>

            <!-- Toggle -->
            <BaseToggle v-model="checkedCriteria[crit.id]" />

            <!-- Weight input (nur sichtbar, wenn aktiviert) -->
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
        <!-- Cancel button on the left -->
        <BaseButton
          type="button"
          variant="cancel"
          @click="$router.push('/')"
        >
          Cancel
        </BaseButton>

        <!-- Create button on the right -->
        <BaseButton type="submit">
          Create
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<script>
import BaseInput from "@/components/BaseComponents/BaseInput.vue";
import BaseButton from "@/components/BaseComponents/BaseButton.vue";
import BaseToggle from "@/components/BaseComponents/BaseToggle.vue";
import { getCriterias } from "../../api/criterias";
import { createSession } from "../../api/sessions";

export default {
  components: { BaseInput, BaseButton, BaseToggle },
  data() {
    return {
      session: {
        title: "",
        description: "",
      },
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

        // Initialize checked criteria and weights
        this.checkedCriteria = Object.fromEntries(this.criteria.map(c => [c.id, true]));
        this.criteriaWeights = Object.fromEntries(this.criteria.map(c => [c.id, 1]));
      } catch (err) {
        console.error("Failed to load criteria", err);
      }
    },
    async submitForm() {
      try {
        // Build payload with a single default phase
        const payload = {
          ...this.session,
          phases: [
            {
              title: "Default Phase",
              order: 1,
              criteria: Object.entries(this.checkedCriteria)
                .filter(([, checked]) => checked)
                .map(([id]) => ({
                  id: Number(id),
                  weight: this.criteriaWeights[id] || 1,
                })),
            },
          ],
        };

        await createSession(payload);
        this.$router.push("/");
      } catch (err) {
        alert(err.response?.data?.detail || "Failed to create session");
      }
    },
  },
  mounted() {
    this.fetchCriteria();
  },
};
</script>
