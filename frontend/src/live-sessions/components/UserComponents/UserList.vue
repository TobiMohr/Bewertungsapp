<template>
  <div class="max-w-7xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold text-gray-800">Users</h2>
      <router-link to="/users/create">
        <BaseButton class="bg-green-500 hover:bg-green-600">
          Create User
        </BaseButton>
      </router-link>
    </div>

    <!-- Filters -->
    <div class="mb-6 flex flex-col md:flex-row md:items-end md:space-x-6">
      <!-- Session selector -->
      <div class="w-full md:w-1/4">
        <label class="block mb-2 font-semibold">Select Session</label>
        <BaseSelect
          v-model="selectedSessionId"
          :options="sessionOptions"
        />
      </div>

      <!-- Team selector -->
      <div class="w-full md:w-1/4 mt-4 md:mt-0">
        <label class="block mb-2 font-semibold">Select Team</label>
        <BaseSelect
          v-model="selectedTeamId"
          :options="teamOptions"
        />
      </div>
    </div>

    <!-- Users list -->
    <ul class="divide-y divide-gray-200">
      <li
        v-for="user in filteredUsers"
        :key="user.id"
        class="py-4 flex items-center justify-between"
      >
        <div>
          <p
            class="text-lg font-medium text-gray-900 cursor-pointer hover:underline"
            @click="$router.push({ path: `/users/${user.id}`, query: { session: selectedSessionId } })"
          >
            {{ user.first_name }} {{ user.last_name }} - {{ user.email }}

            <!-- Role badge -->
            <span
              class="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-sm font-medium"
              :class="userRoles[user.id]?.name
                ? 'bg-indigo-100 text-indigo-800'
                : 'bg-gray-100 text-gray-500'"
            >
              {{ userRoles[user.id]?.name || 'No Role yet' }}
            </span>

            <!-- Team badge -->
            <span
              class="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-sm font-medium"
              :class="user.team?.name
                ? 'bg-green-100 text-green-800'
                : 'bg-gray-100 text-gray-500'"
            >
              {{ user.team?.name || 'No Team yet'}}
            </span>
          </p>
        </div>

        <!-- Actions -->
        <div class="flex items-center space-x-2">
          <BaseButton
            @click="$router.push(`/users/edit/${user.id}`)"
            class="p-2 rounded-full"
            variant="edit"
            tooltip="Edit user"
          >
            <PencilIcon class="h-5 w-5" />
          </BaseButton>

          <BaseButton
            @click="$router.push({ path: `/users/${user.id}/evaluation`, query: { session: selectedSessionId } })"
            class="p-2 rounded-full"
            variant="view"
            tooltip="View Evaluation for User"
          >
            <ChartBarIcon class="h-5 w-5" />
          </BaseButton>

          <BaseButton
            @click="confirmDelete(user.id)"
            class="p-2 rounded-full"
            variant="delete"
            tooltip="Delete user"
          >
            <TrashIcon class="h-5 w-5" />
          </BaseButton>
        </div>
      </li>
    </ul>

    <!-- Empty state -->
    <p v-if="filteredUsers.length === 0" class="text-gray-500 mt-4 text-center">
      No users found.
    </p>

    <!-- Confirm Modal -->
    <ConfirmModal
      :isOpen="showDeleteModal"
      title="Delete User"
      message="Are you sure you want to delete this user?"
      @confirm="deleteConfirmed"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<script>
import { getUsers, deleteUser } from "@/live-sessions/api/users";
import { getUserRoleForSession } from "@/live-sessions/api/roles";
import { getSessions } from "@/live-sessions/api/sessions";
import { getTeams } from "@/live-sessions/api/teams";
import { PencilIcon, TrashIcon, ChartBarIcon } from "@heroicons/vue/24/solid";
import BaseButton from "@/BaseComponents/BaseButton.vue";
import ConfirmModal from "@/BaseComponents/ConfirmModal.vue";
import BaseSelect from "@/BaseComponents/BaseSelect.vue";

export default {
  components: { PencilIcon, TrashIcon, ChartBarIcon, BaseButton, BaseSelect, ConfirmModal },
  data() {
    return {
      users: [],
      sessions: [],
      teams: [],
      selectedSessionId: null,
      selectedTeamId: "", // team filter
      showDeleteModal: false,
      userToDelete: null,
      userRoles: {},
    };
  },
  computed: {
    sessionOptions() {
      const flattenSessions = (sessions, depth = 0) => {
        return sessions.flatMap(s => [
          { value: s.id.toString(), label: `${"— ".repeat(depth)}${s.title}` },
          ...(s.children ? flattenSessions(s.children, depth + 1) : []),
        ]);
      };
      return flattenSessions(this.sessions);
    },
    teamOptions() {
      return [
        { value: "", label: "All Teams" },
        { value: "no-team", label: "No Team" },
        ...this.teams.map(team => ({ value: team.id.toString(), label: team.name })),
        
      ];
    },
    filteredUsers() {
      let filtered = this.users;

      if (this.selectedTeamId) {
        if (this.selectedTeamId === "no-team") {
          filtered = filtered.filter(user => !user.team);
        } else {
          filtered = filtered.filter(user => user.team && user.team.id === Number(this.selectedTeamId));
        }
      }

      // Sort by team name, then last name
      return filtered.sort((a, b) => {
        const teamA = a.team?.name || "";
        const teamB = b.team?.name || "";
        const cmp = teamA.localeCompare(teamB, "en", { sensitivity: "base" });
        if (cmp !== 0) return cmp;
        return a.last_name.localeCompare(b.last_name, "en", { sensitivity: "base" });
      });
    },
  },
  watch: {
    async selectedSessionId(newSessionId) {
      if (newSessionId) {
        await this.fetchRolesForUsers(newSessionId);
      }
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
    async fetchTeams() {
      try {
        const res = await getTeams();
        this.teams = res.data;
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
        if (this.selectedSessionId) {
          await this.fetchRolesForUsers(this.selectedSessionId);
        }
      } catch (err) {
        console.error("Failed to load users:", err);
      }
    },
    async fetchRolesForUsers(sessionId) {
      if (!sessionId || !this.users.length) return;
      const roles = {};
      await Promise.all(
        this.users.map(async (u) => {
          try {
            const res = await getUserRoleForSession(u.id, sessionId);
            roles[u.id] = {
              id: res.data.role_id || null,
              name: res.data.role_name || null,
            };
          } catch (err) {
            roles[u.id] = { id: null, name: null };
          }
        })
      );
      this.userRoles = roles;
    },
    confirmDelete(userId) {
      this.userToDelete = userId;
      this.showDeleteModal = true;
    },
    async deleteConfirmed() {
      if (this.userToDelete) {
        await deleteUser(this.userToDelete);
        this.showDeleteModal = false;
        this.userToDelete = null;
        await this.fetchUsers();
      }
    },
  },
  async mounted() {
    await Promise.all([this.fetchSessions(), this.fetchTeams(), this.fetchUsers()]);

    if (this.sessions.length > 0) {
      this.selectedSessionId = this.sessions[0].id.toString();
    }
    await this.fetchUsers();
    this.selectedTeamId = "";
  },
};
</script>
