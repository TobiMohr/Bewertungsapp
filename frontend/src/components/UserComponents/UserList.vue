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

    <!-- Session selector -->
    <div class="mb-6">
      <label class="block mb-2 font-semibold">Select Session</label>
      <BaseSelect
        :options="sessions.map(s => ({ label: s.title, value: s.id }))"
        :modelValue="selectedSession"
        @update:modelValue="updateSession"
        class="w-full md:w-1/3"
      />
    </div>

    <!-- User list -->
    <ul class="divide-y divide-gray-200">
      <li
        v-for="user in users"
        :key="user.id"
        class="py-4 flex items-center justify-between"
      >
        <div>
          <p
            class="text-lg font-medium text-gray-900 cursor-pointer hover:underline"
            @click="$router.push({ path: `/users/${user.id}`, query: { session: selectedSession } })"
          >
            {{ user.first_name }} {{ user.last_name }} - {{ user.email }}
          </p>
        </div>

        <!-- Actions -->
        <div class="flex items-center space-x-2">
          <BaseButton
            @click="$router.push(`/users/edit/${user.id}`)"
            class="p-2 rounded-full bg-yellow-500 hover:bg-yellow-600"
            title="Edit user"
          >
            <PencilIcon class="h-5 w-5" />
          </BaseButton>

          <BaseButton
            @click="removeUser(user.id)"
            class="p-2 rounded-full bg-red-600 hover:bg-red-700"
            title="Delete user"
          >
            <TrashIcon class="h-5 w-5" />
          </BaseButton>
        </div>
      </li>
    </ul>

    <!-- Empty state -->
    <p v-if="!users.length" class="text-gray-500 mt-4 text-center">
      No users found.
    </p>
  </div>
</template>

<script>
import { getUsers, deleteUser } from "../../api/users";
import { getSessions } from "../../api/sessions";
import { PencilIcon, TrashIcon } from "@heroicons/vue/24/solid";
import BaseButton from "../BaseComponents/BaseButton.vue";
import BaseSelect from "../BaseComponents/BaseSelect.vue";

export default {
  components: { PencilIcon, TrashIcon, BaseButton, BaseSelect },
  data() {
    return {
      users: [],
      sessions: [],
      selectedSession: null,
    };
  },
  methods: {
    async fetchSessions() {
      const res = await getSessions();
      this.sessions = res.data; // keep backend order

      // restore session from localStorage if possible
      const stored = localStorage.getItem("selectedSession");
      if (stored && this.sessions.some(s => s.id === parseInt(stored))) {
        this.selectedSession = parseInt(stored);
      } else if (this.sessions.length) {
        this.selectedSession = this.sessions[0].id;
        localStorage.setItem("selectedSession", this.selectedSession);
      }
    },
    async fetchUsers() {
      const res = await getUsers();
      this.users = res.data.sort((a, b) => {
        const last = a.last_name.localeCompare(b.last_name, "en", { sensitivity: "base" });
        if (last !== 0) return last;
        return a.first_name.localeCompare(b.first_name, "en", { sensitivity: "base" });
      });
    },
    async removeUser(id) {
      if (confirm("Are you sure you want to delete this user?")) {
        await deleteUser(id);
        this.fetchUsers();
      }
    },
    updateSession(value) {
      this.selectedSession = value;
      localStorage.setItem("selectedSession", value);
      this.fetchUsers();
    },
  },
  async mounted() {
    await this.fetchSessions();
    this.fetchUsers();
  },
};
</script>
