<template>
  <div class="max-w-2xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    
    <!-- Header with Edit Session button next to the headline -->
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Edit Session</h2>
      <BaseButton
        class="p-2 rounded-full"
        variant="edit"
        tooltip="Edit this Session"
        @click="openEditModal"
      >
        <PencilIcon class="h-5 w-5" />
      </BaseButton>
    </div>

    <!-- Display session info -->
    <div class="space-y-4">
      <div>
        <label class="block font-bold text-gray-600">Title:</label>
        <p class="text-gray-800">{{ form.title }}</p>
      </div>

      <div>
        <label class="block font-bold text-gray-600">Description:</label>
        <p class="text-gray-800">{{ form.description || "—" }}</p>
      </div>
    </div>

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

    <!-- Edit Session Modal -->
    <BaseDialog v-if="showEditModal" @close="showEditModal = false">
      <template #title>Edit Session</template>

      <template #content>
        <div class="space-y-4">
          <div>
            <label class="block mb-1 font-semibold">Title</label>
            <input
              v-model="editForm.title"
              type="text"
              class="w-full border border-gray-300 rounded-lg p-2"
              required
            />
          </div>

          <div>
            <label class="block mb-1 font-semibold">Description</label>
            <textarea
              v-model="editForm.description"
              class="w-full border border-gray-300 rounded-lg p-2"
              rows="4"
            ></textarea>
          </div>
        </div>
      </template>

      <template #actions>
        <BaseButton variant="cancel" @click="showEditModal = false">Cancel</BaseButton>
        <BaseButton @click="updateSessionHandler">Update</BaseButton>
      </template>
    </BaseDialog>
  </div>
</template>

<script>
import { getSession, updateSession } from "@/live-sessions/api/sessions";
import BaseButton from "@/BaseComponents/BaseButton.vue";
import BaseDialog from "@/BaseComponents/BaseDialog.vue";
import { PencilIcon } from "@heroicons/vue/24/solid";

export default {
  components: { BaseButton, BaseDialog, PencilIcon },
  data() {
    return {
      form: { title: "", description: "" }, // displayed values
      editForm: { title: "", description: "" }, // editable values
      phases: [],
      showEditModal: false,
    };
  },
  methods: {
    openEditModal() {
      this.editForm.title = this.form.title;
      this.editForm.description = this.form.description;
      this.showEditModal = true;
    },
    async updateSessionHandler() {
      const id = this.$route.params.id;
      try {
        await updateSession(id, {
          title: this.editForm.title,
          description: this.editForm.description,
        });
        // Update the displayed values
        this.form.title = this.editForm.title;
        this.form.description = this.editForm.description;
        this.showEditModal = false;
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
