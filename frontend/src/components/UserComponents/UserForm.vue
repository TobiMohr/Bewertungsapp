<template>
  <div class="max-w-md mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">
      {{ isEdit ? "Edit User" : "Create User" }}
    </h2>

    <form @submit.prevent="submitForm" class="space-y-4">
      <input
        v-model="user.first_name"
        placeholder="First Name"
        class="input"
        required
      />
      <input
        v-model="user.last_name"
        placeholder="Last Name"
        class="input"
        required
      />
      <input
        v-model="user.email"
        type="email"
        placeholder="Email"
        class="input"
        required
      />

      <!-- Only show password field when creating a user -->
      <input
        v-if="!isEdit"
        v-model="user.password"
        type="password"
        placeholder="Password"
        class="input"
        required
      />

      <button type="submit" class="btn">
        {{ isEdit ? "Update" : "Create" }}
      </button>
      <button
        v-if="isEdit"
        type="button"
        class="btn cancel"
        @click="cancelEdit"
      >
        Cancel
      </button>
    </form>
  </div>
</template>

<script>
import { createUser, updateUser, getUser } from "../../api/users";

export default {
  data() {
    return {
      user: {
        id: null,
        first_name: "",
        last_name: "",
        email: "",
        password: "",
      },
      isEdit: false,
    };
  },
  async created() {
    const userId = this.$route.params.id;
    if (userId) {
      this.isEdit = true;
      const response = await getUser(userId);
      this.user = { ...response.data, password: "" }; // don't load password
    }
  },
  methods: {
    async submitForm() {
      try {
        if (this.isEdit) {
          const payload = { ...this.user };
          delete payload.password; // password cannot be edited
          await updateUser(this.user.id, payload);
        } else {
          await createUser(this.user);
        }
        this.$router.push("/users"); // redirect to user list
      } catch (err) {
        alert(err.response?.data?.detail || "Operation failed");
      }
    },
    cancelEdit() {
      this.$router.push("/users");
    },
  },
};
</script>

<style scoped>
.input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 0.375rem;
}
.btn {
  padding: 0.5rem 1rem;
  background-color: #4f46e5;
  color: white;
  border-radius: 0.375rem;
}
.btn.cancel {
  background-color: #9ca3af;
}
</style>
