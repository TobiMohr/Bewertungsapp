<template>
  <div class="max-w-2xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <!-- Header -->
    <h2 class="text-2xl font-bold text-gray-800 mb-2">
      {{ user?.first_name }} {{ user?.last_name }}
    </h2>
    <p class="text-gray-600 mb-6">{{ user?.email }}</p>

    <h3 class="text-xl font-semibold text-gray-700 mb-4">Criteria</h3>

    <!-- Criteria list -->
    <ul v-if="criteria.length" class="divide-y divide-gray-200">
      <li
        v-for="c in criteria"
        :key="c.id"
        class="py-4 flex justify-between items-center"
      >
        <!-- Criterion name -->
        <p class="text-gray-900 font-medium">{{ c.criterion.name }}</p>

        <!-- Countable criterion -->
        <div v-if="c.criterion.type === 'countable'" class="flex items-center space-x-2">
          <span class="text-gray-700 font-bold text-lg">{{ c.count_value ?? 0 }}</span>
          <BaseButton
            class="w-8 h-8 flex items-center justify-center p-0 rounded-full bg-blue-500 hover:bg-blue-600 text-white text-xl shadow"
            @click="increment(c.criterion_id)"
          >
            +
          </BaseButton>
        </div>

        <!-- Boolean criterion -->
        <div v-else>
          <label class="flex items-center cursor-pointer">
            <input
              type="checkbox"
              v-model="c.is_fulfilled"
              class="form-checkbox h-5 w-5 text-indigo-600"
              @change="toggleBoolean(c.criterion_id, c.is_fulfilled)"
            />
          </label>
        </div>
      </li>
    </ul>

    <!-- Empty state -->
    <p v-else class="text-gray-500 mt-4 text-center">
      No criteria assigned to this user.
    </p>
  </div>
</template>

<script>
import BaseButton from "../BaseComponents/BaseButton.vue";
import { getUser } from "../../api/users";
import { getUserCriterias, incrementUserCriterion, setBooleanValue } from "../../api/criterias";

export default {
  components: { BaseButton },
  data() {
    return {
      user: null,
      criteria: [],
    };
  },
  methods: {
    async fetchData() {
      const id = this.$route.params.id;
      const sessionId = this.$route.query.session; // <-- get session ID from query param

      const [userRes, critRes] = await Promise.all([
        getUser(id),
        getUserCriterias(id, sessionId), // <-- pass session ID here
      ]);

      this.user = userRes.data;
      this.criteria = critRes.data;
    },
    async increment(criterionId) {
      const id = this.$route.params.id;
      const sessionId = this.$route.query.session;
      await incrementUserCriterion(criterionId, id, sessionId); // <-- pass session ID
      this.fetchData();
    },
    async toggleBoolean(criterionId, value) {
      const id = this.$route.params.id;
      const sessionId = this.$route.query.session;
      await setBooleanValue(criterionId, id, sessionId, value); // <-- pass session ID
    },
  },
  mounted() {
    this.fetchData();
  },
};
</script>

