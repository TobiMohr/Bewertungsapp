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

    <!-- Session selector -->
    <div class="mb-6 w-1/4">
      <label class="block mb-2 font-semibold">Select Session</label>
      <BaseSelect v-model="selectedSessionId" :options="sessionOptions" />
    </div>

    <!-- Teams list -->
    <ul class="divide-y divide-gray-200">
      <li v-for="team in teams" :key="team.id" class="py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2 cursor-pointer" @click="toggleTeam(team.id)">
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

            <!-- Role badge based on selected session -->
            <span
              class="inline-flex items-center px-2 py-0.5 rounded-full text-sm font-medium"
              :class="userRoles[user.id]?.name
                ? 'bg-indigo-100 text-indigo-800'
                : 'bg-gray-100 text-gray-500'"
            >
              {{ userRoles[user.id]?.name || 'No Role yet' }}
            </span>
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
import { getSessions } from "@/live-sessions/api/sessions";
import { getUserRoleForSession } from "@/live-sessions/api/roles";
import BaseButton from "@/BaseComponents/BaseButton.vue";
import ConfirmModal from "@/BaseComponents/ConfirmModal.vue";
import BaseSelect from "@/BaseComponents/BaseSelect.vue";
import { PencilIcon, TrashIcon, ChevronRightIcon, ChevronDownIcon } from "@heroicons/vue/24/solid";

export default {
  components: { PencilIcon, TrashIcon, ChevronRightIcon, ChevronDownIcon, BaseButton, ConfirmModal, BaseSelect },
  data() {
    return {
      teams: [],
      users: [],
      usersByTeam: {},
      sessions: [],
      selectedSessionId: null,
      selectedTeamId: null,
      userRoles: {},
      showDeleteModal: false,
      teamToDelete: null,
    };
  },
  computed: {
    sessionOptions() {
      const flattenSessions = (sessions, depth = 0) =>
        sessions.flatMap(s => [
          { value: s.id.toString(), label: `${"— ".repeat(depth)}${s.title}` },
          ...(s.children ? flattenSessions(s.children, depth + 1) : [])
        ]);
      return flattenSessions(this.sessions);
    },
  },
  watch: {
    async selectedSessionId(sessionId) {
      if (!sessionId) return;
      await this.fetchRolesForAllUsers(sessionId);
    },
  },
  methods: {
    async fetchTeams() {
      try {
        const res = await getTeams();
        this.teams = res.data.sort((a, b) => a.name.localeCompare(b.name, "en", { sensitivity: "base" }));
      } catch (err) {
        console.error("Failed to load teams:", err);
      }
    },
    async fetchUsers() {
      try {
        const res = await getUsers();
        this.users = res.data.sort((a, b) => {
          const last = a.last_name.localeCompare(b.last_name, "en", { sensitivity: "base" });
          return last !== 0 ? last : a.first_name.localeCompare(b.first_name, "en", { sensitivity: "base" });
        });

        // build usersByTeam map
        this.usersByTeam = this.teams.reduce((acc, team) => {
          acc[team.id] = this.users.filter(u => u.team?.id === team.id);
          return acc;
        }, {});

        if (this.selectedSessionId) await this.fetchRolesForAllUsers(this.selectedSessionId);
      } catch (err) {
        console.error("Failed to load users:", err);
      }
    },
    async fetchSessions() {
      try {
        const res = await getSessions();
        this.sessions = res.data;
        if (this.sessions.length > 0) this.selectedSessionId = this.sessions[0].id.toString();
      } catch (err) {
        console.error("Failed to load sessions:", err);
      }
    },
    async fetchRolesForAllUsers(sessionId) {
      if (!sessionId || !this.users.length) return;

      const roles = {};
      await Promise.all(this.users.map(async (u) => {
        try {
          const res = await getUserRoleForSession(u.id, sessionId);
          roles[u.id] = { id: res.data.role_id, name: res.data.role_name };
        } catch {
          roles[u.id] = { id: null, name: null };
        }
      }));
      this.userRoles = roles;
    },
    toggleTeam(teamId) {
      this.selectedTeamId = this.selectedTeamId === teamId ? null : teamId;
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
        await this.fetchTeams();
        await this.fetchUsers();
      }
    },
  },
  async mounted() {
    await Promise.all([this.fetchTeams(), this.fetchSessions()]);
    await this.fetchUsers();
  },
};
</script>

