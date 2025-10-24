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

    <!-- Info text -->
    <div class="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg text-blue-800 text-sm">
      Criteria can only be deleted if they are not used in any session. <br />
      To assign criteria to users, select a session from the dropdown above and click the "Edit for Users" button next to a criterion.
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

        <div class="flex items-center space-x-2">
          <BaseButton
            :disabled="!selectedSessionId"
            @click="$router.push({ path: `/criterias/${crit.id}/users`, query: { session: selectedSessionId } })"
            class="p-2 rounded-full"
            :tooltip="selectedSessionId ? 'Edit for Users' : 'Select a session to edit for users'"
          >
            <ChartBarIcon class="h-5 w-5" />
          </BaseButton>

          <BaseButton
            @click="confirmDelete(crit.id)"
            class="p-2 rounded-full"
            variant="delete"
            :tooltip="crit.has_dependencies || selectedSessionId
              ? 'Cannot delete: criterion is in use or part of a session'
              : 'Delete criterion'"
            :disabled="crit.has_dependencies || !!selectedSessionId"
          >
            <TrashIcon class="h-5 w-5" />
          </BaseButton>
        </div>
      </li>
    </ul>

    <!-- Empty state -->
    <p v-if="selectedSessionId && criterias.length === 0" class="text-gray-500 mt-4 text-center">
      This session has no criteria assigned.
    </p>

    <!-- Confirm Modal -->
    <ConfirmModal
      :isOpen="showDeleteModal"
      title="Delete Criterion"
      message="Are you sure you want to delete this criterion?"
      @confirm="deleteConfirmed"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<script>
import { getSessions } from "@/live-sessions/api/sessions";
import { getCriterias, deleteCriterion } from "@/live-sessions/api/criterias";
import { ChartBarIcon, TrashIcon } from "@heroicons/vue/24/solid";
import BaseButton from "@/BaseComponents/BaseButton.vue";
import BaseSelect from "@/BaseComponents/BaseSelect.vue";
import ConfirmModal from "@/BaseComponents/ConfirmModal.vue";

export default {
  components: { BaseButton, BaseSelect, ChartBarIcon, TrashIcon, ConfirmModal },
  data() {
    return {
      sessions: [],
      criterias: [],
      allCriterias: [],
      selectedSessionId: null,
      showDeleteModal: false,
      criterionToDelete: null,
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
        this.criterias = this.allCriterias;
        return;
      }
      const sessionIdNum = Number(this.selectedSessionId);
      const flattenAllSessions = (sessions) =>
        sessions.flatMap(s => [s, ...(s.children ? flattenAllSessions(s.children) : [])]);
      const allSessions = flattenAllSessions(this.sessions);
      const session = allSessions.find(s => s.id === sessionIdNum);
      const uniqueCriteria = Array.from(
        new Map(session.criteria.map(c => [c.criterion.id, c.criterion])).values()
      );
      this.criterias = uniqueCriteria.sort((a, b) =>
        a.name.localeCompare(b.name, "en", { sensitivity: "base" })
      );
    },
    confirmDelete(id) {
      this.criterionToDelete = id;
      this.showDeleteModal = true;
    },
    async deleteConfirmed() {
      if (!this.criterionToDelete) return;
      try {
        await deleteCriterion(this.criterionToDelete);
        this.showDeleteModal = false;
        this.criterionToDelete = null;
        // refresh lists like roles page
        await this.fetchAllCriterias();
        if (this.selectedSessionId) await this.fetchCriteriasBySession();
      } catch (err) {
        console.error("Failed to delete criterion:", err);
      }
    }
  },
  async mounted() {
    await this.fetchSessions();
    await this.fetchAllCriterias();
    this.criterias = this.allCriterias;
  }
};
</script>
