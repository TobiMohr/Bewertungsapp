<template>
  <div class="max-w-2xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold text-gray-800">Criterias</h2>
      <router-link to="/criterias/create">
        <button class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded">
          Create Criterion
        </button>
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
            {{ crit.name }} <span class="text-gray-500 text-sm">({{ crit.type }})</span>
          </p>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
import { getCriterias } from "../../api/criterias";

export default {
  data() {
    return { criterias: [] };
  },
  methods: {
    async fetchCriterias() {
      const response = await getCriterias();
      this.criterias = response.data;
    },
  },
  mounted() {
    this.fetchCriterias();
  },
};
</script>
