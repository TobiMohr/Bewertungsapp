<template>
  <div class="max-w-2xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">Users</h2>

    <!-- Edit User Form -->
    <div v-if="editingUser" class="mb-6 p-4 bg-gray-50 rounded">
      <h3 class="text-xl font-semibold mb-2">Edit User</h3>
      <form @submit.prevent="submitEdit" class="space-y-3">
        <input
          v-model="editingUser.first_name"
          placeholder="First Name"
          class="w-full px-3 py-2 border rounded"
        />
        <input
          v-model="editingUser.last_name"
          placeholder="Last Name"
          class="w-full px-3 py-2 border rounded"
        />
        <div class="flex space-x-2">
          <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Save
          </button>
          <button
            type="button"
            @click="cancelEdit"
            class="px-4 py-2 bg-gray-400 text-white rounded hover:bg-gray-500"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>

    <!-- Users List -->
    <ul class="divide-y divide-gray-200">
      <li
        v-for="user in users"
        :key="user.id"
        class="py-4 flex items-center justify-between"
      >
        <div>
          <p class="text-lg font-medium text-gray-900">
            {{ user.first_name }} {{ user.last_name }}
          </p>
        </div>

        <div class="flex items-center space-x-2">
          <!-- Edit Icon Button -->
          <button
            @click="startEdit(user)"
            class="p-2 rounded-full bg-yellow-500 text-white hover:bg-yellow-600 transition"
            title="Edit user"
          >
            <PencilIcon class="h-5 w-5" />
          </button>

          <!-- Delete Icon Button -->
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
import { getUsers, deleteUser, updateUser } from "../api/users";
import { PencilIcon, TrashIcon } from "@heroicons/vue/24/solid";

export default {
  components: { PencilIcon, TrashIcon },
  data() {
    return {
      users: [],
      editingUser: null, // Holds the user being edited
    };
  },
  methods: {
    async fetchUsers() {
      const response = await getUsers();
      this.users = response.data;
    },
    async removeUser(id) {
      await deleteUser(id);
      this.fetchUsers();
    },
    startEdit(user) {
      // Make a copy to avoid mutating the list directly
      this.editingUser = { ...user };
    },
    cancelEdit() {
      this.editingUser = null;
    },
    async submitEdit() {
      await updateUser(this.editingUser.id, {
        first_name: this.editingUser.first_name,
        last_name: this.editingUser.last_name,
      });
      this.editingUser = null;
      this.fetchUsers();
    },
  },
  mounted() {
    this.fetchUsers();
  },
};
</script>
