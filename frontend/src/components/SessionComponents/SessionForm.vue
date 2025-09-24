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
            <BaseToggle v-model="checkedCriteria[crit.id]" />
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
      checkedCriteria: {}, // Mapping crit.id -> true/false
    };
  },
  computed: {
    selectedCriteria() {
        return Object.entries(this.checkedCriteria)
            .filter(entry => entry[1])          // entry[1] ist der Wert (true/false)
            .map(entry => Number(entry[0]));    // entry[0] ist der Key
    },
  },
  methods: {
    async fetchCriteria() {
      try {
        const res = await getCriterias();
        this.criteria = res.data;

        // Standardmäßig alle Kriterien ausgewählt
        this.checkedCriteria = Object.fromEntries(
          this.criteria.map((c) => [c.id, true])
        );
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
