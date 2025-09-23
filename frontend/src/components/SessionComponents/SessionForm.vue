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
            class="flex items-center justify-between"
          >
            <span class="text-gray-800">{{ crit.name }}</span>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                v-model="selectedCriteria"
                :value="crit.id"
                class="sr-only peer"
              />
              <div
                class="w-11 h-6 bg-gray-300 rounded-full peer peer-checked:bg-green-500 transition-colors"
              ></div>
              <div
                class="absolute left-1 top-1 w-4 h-4 bg-white rounded-full shadow-md transform transition-transform peer-checked:translate-x-5"
              ></div>
            </label>
          </div>
        </div>
      </div>

      <!-- Buttons -->
      <div class="flex space-x-2 pt-4">
        <BaseButton type="submit">Create</BaseButton>
        <BaseButton
          type="button"
          class="bg-gray-400 hover:bg-gray-500"
          @click="$router.push('/')"
        >
          Cancel
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<script>
import BaseInput from "@/components/BaseComponents/BaseInput.vue";
import BaseButton from "@/components/BaseComponents/BaseButton.vue";
import { getCriterias } from "../../api/criterias";
import { createSession } from "../../api/sessions";

export default {
  components: { BaseInput, BaseButton },
  data() {
    return {
      session: {
        title: "",
        description: "",
      },
      criteria: [],
      selectedCriteria: [],
    };
  },
  methods: {
    async fetchCriteria() {
      try {
        const res = await getCriterias();
        this.criteria = res.data;
        // Alle Kriterien standardmäßig ausgewählt
        this.selectedCriteria = this.criteria.map(c => c.id);
      } catch (err) {
        console.error("Failed to load criteria", err);
      }
    },
    async submitForm() {
      try {
        await createSession({
          ...this.session,
          criteria_ids: this.selectedCriteria,
        });
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
