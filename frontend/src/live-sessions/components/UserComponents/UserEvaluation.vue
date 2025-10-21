<template>
  <div class="max-w-7xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md flex gap-6">

    <!-- Collapsible sidebar -->
    <aside
      :class="[
        'transition-all duration-300 bg-gray-50 p-4 rounded-lg border overflow-y-auto',
        isTreeCollapsed ? 'w-16' : 'w-1/4'
      ]"
    >
      <!-- Toggle Button -->
      <button
        @click="isTreeCollapsed = !isTreeCollapsed"
        class="mb-4 p-2 bg-gray-200 hover:bg-gray-300 rounded text-sm font-medium w-full flex items-center justify-center gap-1"
      >
        <ChevronLeftIcon v-if="!isTreeCollapsed" class="w-5 h-5" />
        <span v-if="!isTreeCollapsed">Collapse</span>
        <ChevronRightIcon v-else class="w-5 h-5" />
      </button>

      <!-- Tree only when expanded -->
      <div v-if="!isTreeCollapsed">
        <h3 class="text-lg font-semibold text-gray-800 mb-3">Sessions</h3>
        <PhaseTree
          :items="sessions"
          :activeId="selectedItem?.id"
          @select="handleSelect"
        />
      </div>
    </aside>

    <!-- Main content -->
    <main class="flex-1 overflow-hidden">

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

      <!-- Main session/subsession display -->
      <div v-if="selectedItem" class="mb-8 bg-gray-100 p-4 rounded-lg shadow-sm">

        <!-- Session info -->
        <h3 class="text-xl font-semibold text-gray-800 mb-2">
          {{ selectedItem.title }}
        </h3>
        <p v-if="selectedItem.description" class="text-gray-600 mb-4">
          {{ selectedItem.description }}
        </p>

        <!-- Criteria -->
        <div v-if="sortedCriteria(selectedItem).length">

          <!-- Non-text criteria grid -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            <div
              v-for="uc in sortedCriteria(selectedItem).filter(c => c.criterion.type !== 'text')"
              :key="uc.id"
              class="flex justify-between items-center p-3 border rounded-lg shadow-sm bg-white"
            >
              <div class="flex flex-col">
                <p class="text-gray-900 font-medium">{{ uc.criterion.name }}</p>
                <span
                  class="text-xs font-semibold px-2 py-0.5 rounded-full mt-1 self-start"
                  :class="uc.criterion.weight === 0
                    ? 'bg-red-100 text-red-700'
                    : 'bg-emerald-100 text-emerald-700'"
                >
                  Weight: {{ uc.criterion.weight }}
                </span>
              </div>

              <div v-if="uc.criterion.type === 'countable'" class="text-gray-700 font-bold text-lg">
                {{ uc.count_value }}
              </div>

              <div v-else-if="uc.criterion.type === 'boolean'">
                <span
                  class="inline-flex items-center px-2 py-1 rounded-full text-sm font-medium"
                  :class="uc.is_fulfilled
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-gray-500'"
                >
                  {{ uc.is_fulfilled ? 'Fulfilled' : 'Not fulfilled' }}
                </span>
              </div>
            </div>
          </div>

          <!-- Text criteria full width -->
          <div class="flex flex-col gap-4">
            <div
              v-for="uc in sortedCriteria(selectedItem).filter(c => c.criterion.type === 'text')"
              :key="uc.id"
              class="p-3 border rounded-lg shadow-sm bg-white"
            >
              <div class="flex flex-col">
                <p class="text-gray-900 font-medium mb-1">{{ uc.criterion.name }}</p>
                <span
                  class="text-xs font-semibold px-2 py-0.5 rounded-full self-start"
                  :class="uc.criterion.weight === 0
                    ? 'bg-red-100 text-red-700'
                    : 'bg-emerald-100 text-emerald-700'"
                >
                  Weight: {{ uc.criterion.weight }}
                </span>
              </div>

              <div class="text-gray-800 whitespace-pre-wrap break-words mt-2">
                {{ uc.text_value || '—' }}
              </div>
            </div>
          </div>

        </div>

        <p v-else class="text-gray-500 text-center">No criteria for this session/subsession.</p>
      </div>

      <p v-else class="text-gray-500 text-center mt-8">
        Select a session or subsession from the tree.
      </p>
    </main>
  </div>
</template>

<script>
import BaseSelect from "@/BaseComponents/BaseSelect.vue";
import PhaseTree from "@/BaseComponents/PhaseTree.vue";
import { getUser, getUserEvaluation, getUsers } from "@/live-sessions/api/users";
import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/vue/24/solid";

export default {
  components: { BaseSelect, PhaseTree, ChevronLeftIcon, ChevronRightIcon },
  data() {
    return {
      user: null,
      sessions: [],
      selectedItem: null,
      selectedUserId: null,
      userOptions: [],
      isTreeCollapsed: false,
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
    sortedCriteria(item) {
      if (!item.userCriteria) return [];
      return [...item.userCriteria].sort((a, b) => {
        const order = { countable: 1, boolean: 2, text: 3 };
        if (order[a.criterion.type] !== order[b.criterion.type]) {
          return order[a.criterion.type] - order[b.criterion.type];
        }
        return a.criterion.name.localeCompare(b.criterion.name, "en", { sensitivity: "base" });
      });
    },

    async fetchUserData(userId) {
      try {
        const [userRes, evalRes] = await Promise.all([
          getUser(userId),
          getUserEvaluation(userId),
        ]);
        this.user = userRes.data;
        this.sessions = evalRes.data;

        // default selection
        this.selectedItem = this.sessions[0] || null;
      } catch (err) {
        console.error("Failed to fetch user data:", err);
      }
    },

    async fetchUsers() {
      try {
        const res = await getUsers();
        this.userOptions = res.data.map(u => ({ value: u.id.toString(), label: `${u.first_name} ${u.last_name}` }));
      } catch (err) {
        console.error("Failed to fetch users:", err);
      }
    },

    handleSelect(item) {
      this.selectedItem = item;
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
