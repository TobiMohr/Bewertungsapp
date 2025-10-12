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

    <!-- Phase selector -->
    <div class="mb-6 w-full md:w-1/3">
      <label class="block mb-2 font-semibold">Select Phase</label>
      <BaseSelect
        v-model="selectedPhaseId"
        :groups="phaseGroups"
        placeholder="-- All Phases --"
      />
    </div>

    <!-- Criteria list -->
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

        <div>
          <BaseButton
            @click="$router.push({ path: `/criterias/${crit.id}/users`, query: { phase: selectedPhaseId } })"
            class="p-2 rounded-full"
            tooltip="Edit for Users"
          >
            <ChartBarIcon class="h-5 w-5" />
          </BaseButton>
        </div>
      </li>
    </ul>

    <!-- Empty state -->
    <p v-if="criterias.length === 0" class="text-gray-500 mt-4 text-center">
      No criteria found for this phase.
    </p>
  </div>
</template>

<script>
import { getCriterias } from "@/api/criterias";
import { getSessions } from "@/api/sessions";
import { getPhase } from "@/api/phases";
import { ChartBarIcon  } from "@heroicons/vue/24/solid";
import BaseButton from "@/components/BaseComponents/BaseButton.vue";
import BaseSelect from "@/components/BaseComponents/BaseSelect.vue";

export default {
  components: { BaseButton, BaseSelect, ChartBarIcon},
  data() {
    return {
      criterias: [],
      sessions: [],
      selectedPhaseId: null,
    };
  },
  computed: {
    phaseGroups() {
      return this.sessions.map(session => ({
        label: session.title,
        options: session.phases.map(phase => ({
          value: phase.id.toString(),
          label: phase.title,
        })),
      }));
    },
  },
  watch: {
    selectedPhaseId() {
      this.fetchCriteriasByPhase();
    },
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

    async fetchCriterias() {
      try {
        const res = await getCriterias();
        this.criterias = res.data.sort((a, b) =>
          a.name.localeCompare(b.name, "en", { sensitivity: "base" })
        );
      } catch (err) {
        console.error("Failed to load criterias:", err);
      }
    },

    async fetchCriteriasByPhase() {
      try {
        if (!this.selectedPhaseId) {
          // no phase selected → show all criteria
          await this.fetchCriterias();
        } else {
          const res = await getPhase(Number(this.selectedPhaseId));
          const phaseCriteriaIds = res.data.criteria.map(c => c.criterion.id);

          const allRes = await getCriterias();
          this.criterias = allRes.data
            .filter(c => phaseCriteriaIds.includes(c.id))
            .sort((a, b) =>
              a.name.localeCompare(b.name, "en", { sensitivity: "base" })
            );
        }
      } catch (err) {
        console.error("Failed to load criteria for phase:", err);
      }
    },
  },
  async mounted() {
    await Promise.all([this.fetchSessions(), this.fetchCriteriasByPhase()]);
  },
};
</script>
