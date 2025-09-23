<template>
  <div class="max-w-md mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">
      Create Session
    </h2>

    <form @submit.prevent="submitForm" class="space-y-4">
      <!-- Title -->
      <BaseInput
        v-model="session.title"
        placeholder="Session Title"
        required
      />

      <!-- Description -->
      <BaseInput
        v-model="session.description"
        placeholder="Description (optional)"
      />

      <div class="flex space-x-2">
        <BaseButton type="submit">Create</BaseButton>
        <BaseButton
          type="button"
          class="bg-gray-400 hover:bg-gray-500"
          @click="$router.push('/')" 
        >
          Cancel
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<script>
import BaseInput from "@/components/BaseComponents/BaseInput.vue";
import BaseButton from "@/components/BaseComponents/BaseButton.vue";
import { createSession } from "../../api/sessions";

export default {
  components: { BaseInput, BaseButton },
  data() {
    return {
      session: {
        title: "",
        description: "",
      },
    };
  },
  methods: {
    async submitForm() {
      try {
        await createSession(this.session);
        this.$router.push("/"); // redirect after creation
      } catch (err) {
        alert(err.response?.data?.detail || "Failed to create session");
      }
    },
  },
};
</script>

<style scoped>
/* Optional styling for BaseInput/BaseButton already applied */
</style>
