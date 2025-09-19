<template>
  <div class="max-w-md mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">
      {{ isEdit ? "Edit User" : "Create User" }}
    </h2>

    <form @submit.prevent="submitForm" class="space-y-4">
      <BaseInput v-model="user.first_name" placeholder="First Name" required />
      <BaseInput v-model="user.last_name" placeholder="Last Name" required />
      <BaseInput v-model="user.email" type="email" placeholder="Email" required />

      <BaseInput
        v-if="!isEdit"
        v-model="user.password"
        type="password"
        placeholder="Password"
        required
      />

      <div class="flex space-x-2">
        <BaseButton type="submit">{{ isEdit ? "Update" : "Create" }}</BaseButton>
        <BaseButton
          v-if="isEdit"
          type="button"
          class="bg-gray-400 hover:bg-gray-500"
          @click="cancelEdit"
        >
          Cancel
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<script>
import BaseInput from "../BaseComponents/BaseInput.vue";
import BaseButton from "../BaseComponents/BaseButton.vue";
import { createUser, updateUser, getUser } from "../../api/users";

export default {
  components: { BaseInput, BaseButton },
  data() {
    return {
      user: { id: null, first_name: "", last_name: "", email: "", password: "" },
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
