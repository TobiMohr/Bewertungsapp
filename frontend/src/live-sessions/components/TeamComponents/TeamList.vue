<template>
  <div class="max-w-7xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold text-gray-800">Teams</h2>
      <router-link to="/teams/create">
        <BaseButton class="bg-green-500 hover:bg-green-600">
          Create Team
        </BaseButton>
      </router-link>
    </div>

    <!-- Teams list -->
    <ul class="divide-y divide-gray-200">
      <li
        v-for="team in teams"
        :key="team.id"
        class="py-4 flex items-center justify-between"
      >
        <div>
          <p
            class="text-lg font-medium text-gray-900 cursor-pointer hover:underline"
            @click="$router.push(`/teams/edit/${team.id}`)"
          >
            {{ team.name }}
          </p>
        </div>

        <!-- Actions -->
        <div class="flex items-center space-x-2">
          <BaseButton
            @click="$router.push(`/teams/edit/${team.id}`)"
            class="p-2 rounded-full"
            variant="edit"
            tooltip="Edit team"
          >
            <PencilIcon class="h-5 w-5" />
          </BaseButton>

          <BaseButton
            @click="confirmDelete(team.id)"
            class="p-2 rounded-full"
            variant="delete"
            tooltip="Delete team"
          >
            <TrashIcon class="h-5 w-5" />
          </BaseButton>
        </div>
      </li>
    </ul>

    <!-- Empty state -->
    <p v-if="teams.length === 0" class="text-gray-500 mt-4 text-center">
      No teams found.
    </p>

    <!-- Confirm Modal -->
    <ConfirmModal
      :isOpen="showDeleteModal"
      title="Delete Team"
      message="Are you sure you want to delete this team?"
      @confirm="deleteConfirmed"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<script>
import { getTeams, deleteTeam } from "@/live-sessions/api/teams";
import { PencilIcon, TrashIcon } from "@heroicons/vue/24/solid";
import BaseButton from "@/BaseComponents/BaseButton.vue";
import ConfirmModal from "@/BaseComponents/ConfirmModal.vue";

export default {
  components: { PencilIcon, TrashIcon, BaseButton, ConfirmModal },
  data() {
    return {
      teams: [],
      showDeleteModal: false,
      teamToDelete: null,
    };
  },
  methods: {
    async fetchTeams() {
      try {
        const res = await getTeams();
        this.teams = res.data.sort((a, b) =>
          a.name.localeCompare(b.name, "en", { sensitivity: "base" })
        );
      } catch (err) {
        console.error("Failed to load teams:", err);
      }
    },
    formatDate(date) {
      return new Date(date).toLocaleString();
    },
    confirmDelete(teamId) {
      this.teamToDelete = teamId;
      this.showDeleteModal = true;
    },
    async deleteConfirmed() {
      if (this.teamToDelete) {
        await deleteTeam(this.teamToDelete);
        this.showDeleteModal = false;
        this.teamToDelete = null;
        this.fetchTeams();
      }
    },
  },
  async mounted() {
    await this.fetchTeams();
  },
};
</script>
