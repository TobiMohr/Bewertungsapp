<template>
  <div class="max-w-md mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold mb-4">Login</h2>
    <form @submit.prevent="submitForm" class="space-y-4">
      <input v-model="credentials.email" type="email" placeholder="Email" class="input" required />
      <input v-model="credentials.password" type="password" placeholder="Password" class="input" required />
      <button type="submit" class="btn">Login</button>
    </form>
    <p v-if="error" class="text-red-500 mt-2">{{ error }}</p>
  </div>
</template>

<script>
import { loginUser } from "@/live-sessions/api/auth";
import { useAuth } from "@/stores/auth";

export default {
  data() {
    return {
      credentials: {
        email: "",
        password: "",
      },
      error: null,
    };
  },
  setup() {
    const { login } = useAuth();
    return { login };
  },
  methods: {
    async submitForm() {
      try {
        const response = await loginUser(this.credentials);
        this.login(response.data.access_token); // ✅ reaktiver Store
        this.$router.push("/users");
      } catch (err) {
        this.error = "Login failed";
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
