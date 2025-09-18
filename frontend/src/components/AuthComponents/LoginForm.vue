<template>
  <div class="max-w-md mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold mb-4">Login</h2>
    <form @submit.prevent="submitForm" class="space-y-4">
      <input v-model="credentials.email" type="email" placeholder="Email" class="input" required />
      <input v-model="credentials.password" type="password" placeholder="Password" class="input" required />
      <button type="submit" class="btn">Login</button>
    </form>
  </div>
</template>

<script>
import { loginUser } from "../../api/auth";

export default {
  data() {
    return {
      credentials: {
        email: "",
        password: "",
      },
    };
  },
  methods: {
    async submitForm() {
      try {
        const response = await loginUser(this.credentials);
        localStorage.setItem("token", response.data.access_token); // save token
        this.$emit("login-success"); // tell parent
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
