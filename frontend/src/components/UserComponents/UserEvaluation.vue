<template>
  <div class="max-w-7xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-2">
      Evaluation für {{ user?.first_name }} {{ user?.last_name }}
    </h2>

    <!-- Tabs: Sessions -->
    <div v-if="sessions.length">
      <!-- Tab-Leiste -->
      <div class="flex flex-wrap border-b mb-6">
        <button
          v-for="(session, index) in sessions"
          :key="session.id"
          @click="activeSession = index"
          class="py-2 px-4 font-medium text-sm rounded-t-lg transition-colors duration-150"
          :class="[
            activeSession === index
              ? 'bg-emerald-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
        >
          {{ session.title }}
        </button>
      </div>

      <!-- Aktiver Session-Inhalt -->
      <div v-if="sessions[activeSession]" class="space-y-8">
        <div class="border-t pt-6 first:border-t-0 first:pt-0">
          <h3 class="text-xl font-semibold text-gray-800 mb-3">
            {{ sessions[activeSession].title }}
          </h3>
          <p v-if="sessions[activeSession].description" class="text-gray-600 mb-4">
            {{ sessions[activeSession].description }}
          </p>

          <!-- Phases der aktiven Session -->
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
              v-if="phase.userCriteria?.length"
              class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
            >
              <div
                v-for="uc in phase.userCriteria"
                :key="uc.id"
                class="flex justify-between items-center p-3 border rounded-lg shadow-sm bg-white"
              >
                <p class="text-gray-900 font-medium">{{ uc.criterion.name }}</p>

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
                    {{ uc.is_fulfilled ? 'Erfüllt' : 'Nicht erfüllt' }}
                  </span>
                </div>

                <div
                  v-else-if="uc.criterion.type === 'text'"
                  class="text-gray-600 text-sm italic truncate max-w-[180px]"
                >
                  {{ uc.text_value || '—' }}
                </div>
              </div>
            </div>

            <p v-else class="text-gray-500 text-center">
              Keine Kriterien für diese Phase.
            </p>
          </div>
        </div>
      </div>
    </div>

    <p v-else class="text-gray-500 text-center mt-8">
      Keine Sessions für diesen Benutzer gefunden.
    </p>
  </div>
</template>

<script>
import { getUser, getUserEvaluation } from "../../api/users";

export default {
  data() {
    return {
      user: null,
      sessions: [],
      activeSession: 0, // Index des aktiven Tabs
    };
  },
  async mounted() {
    try {
      const userId = this.$route.params.id;
      const [userRes, evaluationRes] = await Promise.all([
        getUser(userId),
        getUserEvaluation(userId),
      ]);
      this.user = userRes.data;
      this.sessions = evaluationRes.data;
    } catch (error) {
      console.error("Error fetching user evaluation:", error);
    }
  },
};
</script>
