<template>
  <div class="max-w-7xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold text-gray-800">Roles</h2>
      <router-link to="/roles/create">
        <BaseButton class="bg-green-500 hover:bg-green-600">
          Create Role
        </BaseButton>
      </router-link>
    </div>

    <!-- Roles list -->
    <ul class="divide-y divide-gray-200">
      <li
        v-for="role in roles"
        :key="role.id"
        class="py-4 flex items-center justify-between"
      >
        <div>
          <p
            class="text-lg font-medium text-gray-900 cursor-pointer hover:underline"
            @click="$router.push(`/roles/edit/${role.id}`)"
          >
            {{ role.name }}
          </p>
          <p class="text-gray-600 text-sm">{{ role.description || "No description" }}</p>
        </div>

        <!-- Actions -->
        <div class="flex items-center space-x-2">
          <BaseButton
            @click="$router.push(`/roles/edit/${role.id}`)"
            class="p-2 rounded-full"
            variant="edit"
            tooltip="Edit role"
          >
            <PencilIcon class="h-5 w-5" />
          </BaseButton>

          <BaseButton
            @click="confirmDelete(role.id)"
            class="p-2 rounded-full"
            variant="delete"
            tooltip="Delete role"
          >
            <TrashIcon class="h-5 w-5" />
          </BaseButton>
        </div>
      </li>
    </ul>

    <!-- Empty state -->
    <p v-if="roles.length === 0" class="text-gray-500 mt-4 text-center">
      No roles found.
    </p>

    <!-- Confirm Modal -->
    <ConfirmModal
      :isOpen="showDeleteModal"
      title="Delete Role"
      message="Are you sure you want to delete this role?"
      @confirm="deleteConfirmed"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<script>
import { getRoles, deleteRole } from "@/live-sessions/api/roles";
import { PencilIcon, TrashIcon } from "@heroicons/vue/24/solid";
import BaseButton from "@/BaseComponents/BaseButton.vue";
import ConfirmModal from "@/BaseComponents/ConfirmModal.vue";

export default {
  components: { PencilIcon, TrashIcon, BaseButton, ConfirmModal },
  data() {
    return {
      roles: [],
      showDeleteModal: false,
      roleToDelete: null,
    };
  },
  methods: {
    async fetchRoles() {
      try {
        const res = await getRoles();
        this.roles = res.data.sort((a, b) =>
          a.name.localeCompare(b.name, "en", { sensitivity: "base" })
        );
      } catch (err) {
        console.error("Failed to load roles:", err);
      }
    },
    confirmDelete(roleId) {
      this.roleToDelete = roleId;
      this.showDeleteModal = true;
    },
    async deleteConfirmed() {
      if (this.roleToDelete) {
        await deleteRole(this.roleToDelete);
        this.showDeleteModal = false;
        this.roleToDelete = null;
        this.fetchRoles();
      }
    },
  },
  async mounted() {
    await this.fetchRoles();
  },
};
</script>
