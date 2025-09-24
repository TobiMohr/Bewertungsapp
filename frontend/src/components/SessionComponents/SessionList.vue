<template>
  <div class="max-w-4xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold text-gray-800">Sessions</h2>
      <router-link to="/sessions/create">
        <BaseButton class="bg-green-500 hover:bg-green-600">
          Create Session
        </BaseButton>
      </router-link>
    </div>

    <!-- Session list -->
    <ul class="divide-y divide-gray-200">
      <li
        v-for="session in sessions"
        :key="session.id"
        class="py-4 flex items-center justify-between"
      >
        <div>
          <p
            class="text-lg font-medium text-gray-900 cursor-pointer hover:underline"
            @click="$router.push(`/sessions/edit/${session.id}`)"
          >
            {{ session.title }}
          </p>
          <p class="text-gray-500 text-sm">{{ session.description }}</p>
        </div>

        <!-- Actions -->
        <div class="flex items-center space-x-2">
          <BaseButton
            @click="$router.push(`/sessions/edit/${session.id}`)"
            class="p-2 rounded-full bg-yellow-500 hover:bg-yellow-600"
            title="Edit session"
          >
            <PencilIcon class="h-5 w-5" />
          </BaseButton>

          <BaseButton
            @click="removeSession(session.id)"
            class="p-2 rounded-full bg-red-600 hover:bg-red-700"
            title="Delete session"
          >
            <TrashIcon class="h-5 w-5" />
          </BaseButton>
        </div>
      </li>
    </ul>

    <!-- Empty state -->
    <p v-if="!sessions.length" class="text-gray-500 mt-4 text-center">
      No sessions found.
    </p>
  </div>
</template>

<script>
import { getSessions, deleteSession } from "../../api/sessions";
import { PencilIcon, TrashIcon } from "@heroicons/vue/24/solid";
import BaseButton from "../BaseComponents/BaseButton.vue";

export default {
  components: { PencilIcon, TrashIcon, BaseButton },
  data() {
    return {
      sessions: [],
    };
  },
  methods: {
    async fetchSessions() {
      const res = await getSessions();
      this.sessions = res.data;
    },
    async removeSession(id) {
      if (confirm("Are you sure you want to delete this session?")) {
        await deleteSession(id);
        this.fetchSessions();
      }
    },
  },
  mounted() {
    this.fetchSessions();
  },
};
</script>
