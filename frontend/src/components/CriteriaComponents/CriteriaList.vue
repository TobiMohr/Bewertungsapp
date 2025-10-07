<template>
  <div class="max-w-7xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold text-gray-800">Criteria</h2>
      <router-link to="/criterias/create">
        <BaseButton class="bg-green-500 hover:bg-green-600">
          Create Criterion
        </BaseButton>
      </router-link>
    </div>

    <ul class="divide-y divide-gray-200">
      <li
        v-for="crit in criterias"
        :key="crit.id"
        class="py-4 flex items-center justify-between"
      >
        <div>
          <p class="text-lg font-medium text-gray-900">
            {{ crit.name }}
            <span class="text-gray-500 text-sm">({{ crit.type }})</span>
          </p>
        </div>
      </li>
    </ul>

    <p v-if="criterias.length === 0" class="text-gray-500 mt-4">
      No criterias created yet.
    </p>
  </div>
</template>

<script>
import { getCriterias } from "../../api/criterias";
import BaseButton from "@/components/BaseComponents/BaseButton.vue";

export default {
  components: { BaseButton },
  data() {
    return { criterias: [] };
  },
  methods: {
    async fetchCriterias() {
      const response = await getCriterias();
      this.criterias = response.data.sort((a, b) =>
        a.name.localeCompare(b.name, "en", { sensitivity: "base" })
      );
    },
  },
  mounted() {
    this.fetchCriterias();
  },
};
</script>
