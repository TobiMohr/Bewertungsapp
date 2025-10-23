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

    <div class="mb-6 flex flex-col md:flex-row md:items-end md:space-x-6">
      <!-- Session selector -->
      <div class="w-full md:w-1/4">
        <label class="block mb-2 font-semibold">Select Session</label>
        <BaseSelect
          v-model="selectedSessionId"
          :options="sessionOptions"
          placeholder="-- Select Session --"
        />
      </div>

      <!-- Team selector -->
      <div class="w-full md:w-1/4 mt-4 md:mt-0">
        <label class="block mb-2 font-semibold">Select Team</label>
        <BaseSelect
          v-model="selectedTeamId"
          :options="teamOptions"
          placeholder="-- All Teams --"
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
      selectedTeamId: null, // team filter
      showDeleteModal: false,
      userToDelete: null,
    };
  },
  computed: {
    sessionOptions() {
      // Flatten sessions and subsessions for the select with depth prefix
      const flattenSessions = (sessions, depth = 0) => {
        return sessions.flatMap(s => [
          { value: s.id.toString(), label: `${"— ".repeat(depth)}${s.title}` },
          ...(s.children ? flattenSessions(s.children, depth + 1) : []),
        ]);
      };
      return flattenSessions(this.sessions);
    },
    teamOptions() {
      return this.teams.map(team => ({ value: team.id, label: team.name }));
    },
    filteredUsers() {
      // Keep session filter logic intact
      console.log("Filtering users by team:", this.selectedTeamId);
      console.log(this.users);
      let filtered = this.users;
      if (this.selectedTeamId) {
        filtered = filtered.filter(user => user.team && user.team.id === Number(this.selectedTeamId));
      }
      console.log("Filtered users:", filtered);
      return filtered;
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
      } catch (err) {
        console.error("Failed to load users:", err);
      }
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
        this.fetchUsers();
      }
    },
  },
  async mounted() {
    await Promise.all([this.fetchSessions(), this.fetchTeams(), this.fetchUsers()]);
  },
};
</script>
