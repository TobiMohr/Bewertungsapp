<template>
  <div class="max-w-7xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold text-gray-800">
        Evaluation for {{ user?.first_name }} {{ user?.last_name }}
      </h2>
    </div>

    <!-- User selector -->
    <div class="mb-6 w-full md:w-1/3">
      <label class="block mb-2 font-semibold">Select User</label>
      <BaseSelect
        v-model="selectedUserId"
        :options="userOptions"
        placeholder="-- Select User --"
      />
    </div>

    <!-- Tabs: Sessions -->
    <div v-if="sessions.length">
      <!-- Tab bar -->
      <div class="flex flex-wrap border-b mb-6">
        <button
          v-for="(session, index) in sessions"
          :key="session.id"
          @click="activeSession = index"
          class="py-2 px-4 font-medium text-sm rounded-t-lg transition-colors duration-150"
          :class="[activeSession === index
            ? 'bg-emerald-500 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200']"
        >
          {{ session.title }}
        </button>
      </div>

      <!-- Active session content -->
      <div v-if="sessions[activeSession]" class="space-y-8">
        <div class="border-t pt-6 first:border-t-0 first:pt-0">
          <h3 class="text-xl font-semibold text-gray-800 mb-3">
            {{ sessions[activeSession].title }}
          </h3>
          <p
            v-if="sessions[activeSession].description"
            class="text-gray-600 mb-4"
          >
            {{ sessions[activeSession].description }}
          </p>

          <!-- Phases of the active session -->
          <div
            v-for="phase in sessions[activeSession].phases"
            :key="phase.id"
            class="mb-8 bg-gray-50 p-4 rounded-lg shadow-sm"
          >
            <h4 class="text-lg font-semibold text-gray-700 mb-3">
              {{ phase.title }}
            </h4>
            <p v-if="phase.description" class="text-gray-500 mb-3">
              {{ phase.description }}
            </p>

            <!-- Criteria grid -->
            <div
              v-if="sortedCriteria(phase).length"
              class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
            >
              <div
                v-for="uc in sortedCriteria(phase)"
                :key="uc.id"
                class="flex justify-between items-center p-3 border rounded-lg shadow-sm bg-white"
              >
                <div class="flex flex-col">
                  <p class="text-gray-900 font-medium">
                    {{ uc.criterion.name }}
                    <span
                      class="ml-2 text-xs font-semibold px-2 py-0.5 rounded-full"
                      :class="uc.criterion.weight === 0
                        ? 'bg-red-100 text-red-700'
                        : 'bg-emerald-100 text-emerald-700'"
                    >
                      Weight: {{ uc.criterion.weight }}
                    </span>
                  </p>
                </div>

                <div
                  v-if="uc.criterion.type === 'countable'"
                  class="text-gray-700 font-bold text-lg"
                >
                  {{ uc.count_value }}
                </div>

                <div v-else-if="uc.criterion.type === 'boolean'">
                  <span
                    class="inline-flex items-center px-2 py-1 rounded-full text-sm font-medium"
                    :class="uc.is_fulfilled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-gray-500'"
                  >
                    {{ uc.is_fulfilled ? 'Fulfilled' : 'Not fulfilled' }}
                  </span>
                </div>

                <div v-else-if="uc.criterion.type === 'text'" class="w-full">
                  <div class="text-gray-800 whitespace-pre-wrap break-words">
                    <p :class="{ 'line-clamp-3': !uc.showFull }">
                      {{ uc.text_value || '—' }}
                    </p>

                    <button
                      v-if="uc.text_value && uc.text_value.length > 100"  
                      @click="uc.showFull = !uc.showFull"
                      class="text-indigo-600 hover:underline text-sm mt-1"
                    >
                      {{ uc.showFull ? 'Show less' : 'Show more' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <p v-else class="text-gray-500 text-center">
              No criteria for this phase.
            </p>
          </div>
        </div>
      </div>
    </div>

    <p v-else class="text-gray-500 text-center mt-8">
      No sessions found for this user.
    </p>
  </div>
</template>

<script>
import BaseSelect from "../BaseComponents/BaseSelect.vue";
import { getUser, getUserEvaluation, getUsers } from "../../api/users";

export default {
  components: { BaseSelect },
  data() {
    return {
      user: null,
      sessions: [],
      activeSession: 0,
      selectedUserId: null,
      userOptions: [],
    };
  },
  watch: {
    async selectedUserId(newUserId) {
      if (newUserId) {
        await this.fetchUserData(newUserId);
      }
    },
  },
  methods: {
    sortedCriteria(phase) {
      if (!phase.userCriteria) return [];
      return [...phase.userCriteria].sort((a, b) =>
        a.criterion.name.localeCompare(b.criterion.name, "en", { sensitivity: "base" })
      );
    },

    async fetchUserData(userId) {
      try {
        const [userRes, evalRes] = await Promise.all([
          getUser(userId),
          getUserEvaluation(userId),
        ]);
        this.user = userRes.data;
        this.sessions = evalRes.data;
        this.activeSession = 0;
      } catch (err) {
        console.error("Failed to fetch user data:", err);
      }
    },

    async fetchUsers() {
      try {
        const res = await getUsers();
        this.userOptions = res.data.map((u) => ({
          value: u.id.toString(),
          label: `${u.first_name} ${u.last_name}`,
        }));
      } catch (err) {
        console.error("Failed to fetch users:", err);
      }
    },
  },
  async mounted() {
    await this.fetchUsers();

    const userId = this.$route.params.id;
    if (userId) {
      this.selectedUserId = userId.toString();
      await this.fetchUserData(userId);
    }
  },
};
</script>

<style scoped>
button {
  transition: all 0.2s ease;
}
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  line-clamp: 3;
  overflow: hidden;
}
</style>
