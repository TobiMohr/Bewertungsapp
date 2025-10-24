<template>
  <div class="max-w-7xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold text-gray-800">Criteria</h2>
      <router-link to="/criterias/create">
        <BaseButton class="bg-green-500 hover:bg-green-600 text-white">
          Create Criterion
        </BaseButton>
      </router-link>
    </div>

    <!-- Session selector -->
    <div class="mb-6 w-full md:w-1/3">
      <label class="block mb-2 font-semibold">Select Session</label>
      <BaseSelect
        v-model="selectedSessionId"
        :options="sessionOptions"
      />
    </div>

    <!-- Criteria list -->
    <ul class="divide-y divide-gray-200">
      <li
        v-for="crit in selectedSessionId ? criterias : allCriterias"
        :key="crit.id"
        class="py-4 flex items-center justify-between"
      >
        <div>
          <p class="text-lg font-medium text-gray-900">
            {{ crit.name }}
            <span class="text-gray-500 text-sm">({{ crit.type }})</span>
          </p>
        </div>

        <div>
          <BaseButton
            :disabled="!selectedSessionId"
            @click="$router.push({ path: `/criterias/${crit.id}/users`, query: { session: selectedSessionId } })"
            class="p-2 rounded-full"
            :tooltip="selectedSessionId ? 'Edit for Users' : 'Select a session to edit for users'"
          >
            <ChartBarIcon class="h-5 w-5" />
          </BaseButton>
        </div>
      </li>
    </ul>

    <!-- Empty state if no criteria for this session -->
    <p v-if="selectedSessionId && criterias.length === 0" class="text-gray-500 mt-4 text-center">
      This session has no criteria assigned.
    </p>
  </div>
</template>

<script>
import { getSessions } from "@/live-sessions/api/sessions";
import { getCriterias } from "@/live-sessions/api/criterias";
import { ChartBarIcon } from "@heroicons/vue/24/solid";
import BaseButton from "@/BaseComponents/BaseButton.vue";
import BaseSelect from "@/BaseComponents/BaseSelect.vue";

export default {
  components: { BaseButton, BaseSelect, ChartBarIcon },
  data() {
    return {
      sessions: [],
      criterias: [],       // criteria for selected session
      allCriterias: [],    // all criteria
      selectedSessionId: null,
    };
  },
  computed: {
    sessionOptions() {
      const flattenSessions = (sessions, depth = 0) => {
        return sessions.flatMap(s => [
          { value: s.id.toString(), label: `${"— ".repeat(depth)}${s.title}` },
          ...(s.children ? flattenSessions(s.children, depth + 1) : [])
        ]);
      };
      return [
        { value: "", label: "All Sessions" },
        ...flattenSessions(this.sessions)
      ];
    }
  },
  watch: {
    selectedSessionId() {
      this.fetchCriteriasBySession();
    }
  },
  methods: {
    async fetchSessions() {
      try {
        const res = await getSessions();
        this.sessions = res.data;
      } catch (err) {
        console.error("Failed to load sessions:", err);
      }
    },

    async fetchAllCriterias() {
      try {
        const res = await getCriterias();
        this.allCriterias = res.data.sort((a, b) =>
          a.name.localeCompare(b.name, "en", { sensitivity: "base" })
        );
      } catch (err) {
        console.error("Failed to load all criterias:", err);
      }
    },

    async fetchCriteriasBySession() {
      if (!this.selectedSessionId) {
        // No session selected → show all criteria
        this.criterias = this.allCriterias;
        return;
      }

      const sessionIdNum = Number(this.selectedSessionId);
      const flattenAllSessions = (sessions) =>
        sessions.flatMap(s => [s, ...(s.children ? flattenAllSessions(s.children) : [])]);

      const allSessions = flattenAllSessions(this.sessions);
      const session = allSessions.find(s => s.id === sessionIdNum);

      console.log("Selected sessions criteria:", session.criteria);

      const uniqueCriteria = Array.from(
        new Map(session.criteria.map(c => [c.criterion.id, c.criterion])).values()
      );

      this.criterias = uniqueCriteria.sort((a, b) =>
        a.name.localeCompare(b.name, "en", { sensitivity: "base" })
      );
    }
  },
  async mounted() {
    await this.fetchSessions();
    await this.fetchAllCriterias();
    // initially show all criteria
    this.criterias = this.allCriterias;
  }
};
</script>
