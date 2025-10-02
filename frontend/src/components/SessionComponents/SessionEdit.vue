<template>
  <div class="max-w-2xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-6">Edit Session</h2>

    <form @submit.prevent="updateSessionHandler" class="space-y-6">
      <!-- Title -->
      <div>
        <label class="block mb-2 font-semibold">Title</label>
        <input
          v-model="form.title"
          type="text"
          class="w-full border border-gray-300 rounded-lg p-2"
          required
        />
      </div>

      <!-- Description -->
      <div>
        <label class="block mb-2 font-semibold">Description</label>
        <textarea
          v-model="form.description"
          class="w-full border border-gray-300 rounded-lg p-2"
          rows="4"
        ></textarea>
      </div>

      <!-- Buttons -->
      <div class="flex justify-between pt-4">
        <BaseButton
          type="button"
          variant="cancel"
          @click="$router.push('/sessions')"
        >
          Cancel
        </BaseButton>
        <BaseButton type="submit">
          Update Session
        </BaseButton>
      </div>
    </form>

    <!-- Phases list with "Add Phase" button -->
    <div class="mt-8">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-800">Phases</h3>
        <BaseButton
          @click="$router.push({ path: '/phases/create', query: { sessionId: $route.params.id } })"
        >
          Add Phase
        </BaseButton>
      </div>

      <ul class="divide-y divide-gray-200">
        <li
          v-for="phase in phases"
          :key="phase.id"
          class="py-3 cursor-pointer hover:bg-gray-50 px-2 rounded"
          @click="$router.push(`/phases/${phase.id}`)"
        >
          <div class="flex items-center justify-between">
            <span class="font-medium text-gray-700 hover:underline">{{ phase.title }}</span>
            <p class="text-gray-500 text-sm">{{ phase.description }}</p>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { getSession, updateSession } from "../../api/sessions";
import BaseButton from "../BaseComponents/BaseButton.vue";

export default {
  components: { BaseButton },
  data() {
    return {
      form: {
        title: "",
        description: "",
      },
      phases: [], // store session phases
    };
  },
  methods: {
    async updateSessionHandler() {
      const id = this.$route.params.id;

      try {
        await updateSession(id, {
          title: this.form.title,
          description: this.form.description,
        });
        this.$router.push("/sessions");
      } catch (err) {
        console.error("Failed to update session:", err);
        alert(err.response?.data?.detail || "Failed to update session");
      }
    },
  },
  async mounted() {
    try {
      const sessionRes = await getSession(this.$route.params.id);
      const s = sessionRes.data;

      this.form.title = s.title;
      this.form.description = s.description;
      this.phases = s.phases || [];
    } catch (err) {
      console.error("Failed to fetch session:", err);
      alert("Failed to load session data");
    }
  },
};
</script>
