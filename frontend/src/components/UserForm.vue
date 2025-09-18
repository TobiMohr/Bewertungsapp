<template>
  <div class="max-w-md mx-auto p-6 bg-white rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">Create User</h2>

    <form @submit.prevent="submitForm" class="space-y-4">
      <input
        v-model="user.first_name"
        placeholder="First Name"
        required
        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
      />

      <input
        v-model="user.last_name"
        placeholder="Last Name"
        required
        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring focus:ring-blue-300"
      />

      <button
        type="submit"
        class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors"
      >
        Create
      </button>
    </form>
  </div>
</template>

<script>
import { createUser } from "../api/users";

export default {
  data() {
    return {
      user: {
        first_name: "",
        last_name: "",
      },
    };
  },
  methods: {
    async submitForm() {
      await createUser(this.user);
      this.$emit("user-created");
      this.user = { first_name: "", last_name: "" };
    },
  },
};
</script>
