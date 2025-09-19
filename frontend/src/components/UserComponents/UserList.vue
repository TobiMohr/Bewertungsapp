<template>
  <div class="max-w-2xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold text-gray-800">Users</h2>
      <router-link to="/users/create">
        <button class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded">
          Create User
        </button>
      </router-link>
    </div>

    <ul class="divide-y divide-gray-200">
      <li
        v-for="user in users"
        :key="user.id"
        class="py-4 flex items-center justify-between"
      >
        <div>
          <p class="text-lg font-medium text-gray-900 cursor-pointer hover:underline"
            @click="$router.push(`/users/${user.id}`)"
          >
            {{ user.first_name }} {{ user.last_name }} - {{ user.email }}
          </p>
        </div>

        <div class="flex items-center space-x-2">
          <!-- Edit button -->
          <button
            @click="$router.push(`/users/edit/${user.id}`)"
            class="p-2 rounded-full bg-yellow-500 text-white hover:bg-yellow-600 transition"
            title="Edit user"
          >
            <PencilIcon class="h-5 w-5" />
          </button>

          <!-- Delete button -->
          <button
            @click="removeUser(user.id)"
            class="p-2 rounded-full bg-red-600 text-white hover:bg-red-700 transition"
            title="Delete user"
          >
            <TrashIcon class="h-5 w-5" />
          </button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
import { getUsers, deleteUser } from "../../api/users";
import { PencilIcon, TrashIcon } from "@heroicons/vue/24/solid";

export default {
  components: { PencilIcon, TrashIcon },
  data() {
    return { users: [] };
  },
  methods: {
    async fetchUsers() {
      const response = await getUsers();
      this.users = response.data;
    },
    async removeUser(id) {
      if (confirm("Are you sure you want to delete this user?")) {
        await deleteUser(id);
        this.fetchUsers();
      }
    },
  },
  mounted() {
    this.fetchUsers();
  },
};
</script>
