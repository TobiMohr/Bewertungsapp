<template>
  <div class="max-w-2xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">
      User: {{ user?.first_name }} {{ user?.last_name }}
    </h2>

    <p class="text-gray-600 mb-6">{{ user?.email }}</p>

    <h3 class="text-xl font-semibold text-gray-700 mb-2">Criteria</h3>

    <ul v-if="criteria.length" class="divide-y divide-gray-200">
      <li
        v-for="c in criteria"
        :key="c.id"
        class="py-4 flex justify-between items-center"
      >
        <div>
          <p class="text-gray-900 font-medium">
            {{ c.criterion.name }}
          </p>
          <p class="text-sm text-gray-500">Type: {{ c.criterion.type }}</p>
        </div>

        <!-- Countable -->
        <div v-if="c.criterion.type === 'countable'" class="flex items-center space-x-2">
          <span class="text-gray-700 font-semibold">{{ c.count_value ?? 0 }}</span>
          <button
            @click="increment(c.criterion_id)"
            class="bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded"
          >
            +
          </button>
        </div>

        <!-- Boolean -->
        <div v-else>
          <label class="flex items-center space-x-2">
            <input
              type="checkbox"
              v-model="c.is_fulfilled"
              @change="toggleBoolean(c.criterion_id, c.is_fulfilled)"
            />
            <span>Fulfilled</span>
          </label>
        </div>
      </li>
    </ul>

    <p v-else class="text-gray-500 mt-4">No criteria assigned to this user.</p>
  </div>
</template>

<script>
import { getUser } from "../../api/users";
import { getUserCriterias, incrementUserCriterion, setBooleanValue } from "@/api/criterias";

export default {
  data() {
    return {
      user: null,
      criteria: [],
    };
  },
  methods: {
    async fetchData() {
      const id = this.$route.params.id;
      const [userRes, critRes] = await Promise.all([
        getUser(id),
        getUserCriterias(id),
      ]);
      this.user = userRes.data;
      this.criteria = critRes.data;
    },
    async increment(criterionId) {
      const id = this.$route.params.id;
      await incrementUserCriterion(criterionId, id);
      this.fetchData();
    },
    async toggleBoolean(criterionId, value) {
      const id = this.$route.params.id;
      await setBooleanValue(criterionId, id, value);
    },
  },
  mounted() {
    this.fetchData();
  },
};
</script>
