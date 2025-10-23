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
      <li v-for="team in teams" :key="team.id" class="py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2 cursor-pointer" @click="toggleTeam(team.id)">
            <!-- Show ChevronDown if expanded, ChevronRight if collapsed -->
            <ChevronDownIcon v-if="selectedTeamId === team.id" class="h-5 w-5 text-gray-500" />
            <ChevronRightIcon v-else class="h-5 w-5 text-gray-500" />

            <span class="text-lg font-medium text-gray-900 hover:underline">
                {{ team.name }}
            </span>
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
        </div>

        <!-- Users submenu -->
        <ul
          v-if="selectedTeamId === team.id"
          class="mt-2 ml-6 border-l border-gray-300 pl-4 space-y-1"
        >
          <li
            v-for="user in usersByTeam[team.id] || []"
            :key="user.id"
            class="text-gray-700 hover:text-gray-900 cursor-pointer"
          >
            {{ user.first_name }} {{ user.last_name }}
          </li>
          <li
            v-if="!(usersByTeam[team.id] && usersByTeam[team.id].length)"
            class="text-gray-500 italic"
          >
            No users in this team.
          </li>
        </ul>
      </li>
    </ul>

    <!-- Empty state -->
    <p
      v-if="teams.length === 0"
      class="text-gray-500 mt-4 text-center"
    >
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
import { getUsers } from "@/live-sessions/api/users";
import BaseButton from "@/BaseComponents/BaseButton.vue";
import ConfirmModal from "@/BaseComponents/ConfirmModal.vue";

// Heroicons
import {
  PencilIcon,
  TrashIcon,
  ChevronRightIcon,
  ChevronDownIcon,
} from "@heroicons/vue/24/solid";

export default {
  components: {
    PencilIcon,
    TrashIcon,
    ChevronRightIcon,
    ChevronDownIcon,
    BaseButton,
    ConfirmModal,
  },
  data() {
    return {
      teams: [],
      usersByTeam: {},
      selectedTeamId: null,
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
    async fetchUsersForTeam(teamId) {
      try {
        const res = await getUsers(teamId);
        this.usersByTeam[teamId] = res.data;
      } catch (err) {
        console.error("Failed to load users for team:", err);
      }
    },
    toggleTeam(teamId) {
      if (this.selectedTeamId === teamId) {
        this.selectedTeamId = null;
      } else {
        this.selectedTeamId = teamId;
        if (!this.usersByTeam[teamId]) {
          this.fetchUsersForTeam(teamId);
        }
      }
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
