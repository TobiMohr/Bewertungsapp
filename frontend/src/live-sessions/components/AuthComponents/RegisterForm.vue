<template>
  <div class="max-w-md mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold mb-4">Register</h2>
    <form @submit.prevent="submitForm" class="space-y-4">
      <input v-model="user.first_name" placeholder="First Name" class="input" />
      <input v-model="user.last_name" placeholder="Last Name" class="input" />
      <input v-model="user.email" type="email" placeholder="Email" class="input" required />
      <input v-model="user.password" type="password" placeholder="Password" class="input" required />
      <button type="submit" class="btn">Register</button>
    </form>
  </div>
</template>

<script>
import { registerUser } from '@/live-sessions/api/auth';

export default {
  data() {
    return {
      user: {
        first_name: "",
        last_name: "",
        email: "",
        password: "",
      },
    };
  },
  methods: {
    async submitForm() {
      try {
        const response = await registerUser(this.user);
        alert(`Registered ${response.data.email}`);
        this.user = { first_name: "", last_name: "", email: "", password: "" };
      } catch (err) {
        alert(err.response?.data?.detail || "Registration failed");
      }
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
</style>
