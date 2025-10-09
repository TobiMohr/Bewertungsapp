<template>
  <div class="max-w-7xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold text-gray-800">Users</h2>
      <router-link to="/users/create">
        <BaseButton class="bg-green-500 hover:bg-green-600">
          Create User
        </BaseButton>
      </router-link>
    </div>

    <!-- Phase selector -->
    <div class="mb-6 w-full md:w-1/3">
      <label class="block mb-2 font-semibold">Select Phase</label>
      <BaseSelect
        v-model="selectedPhaseId"
        :groups="phaseGroups"
        placeholder="-- Select Phase --"
      />
    </div>

    <!-- User list -->
    <ul class="divide-y divide-gray-200">
      <li
        v-for="user in users"
        :key="user.id"
        class="py-4 flex items-center justify-between"
      >
        <div>
          <p
            class="text-lg font-medium text-gray-900 cursor-pointer hover:underline"
            @click="$router.push({ path: `/users/${user.id}`, query: { phase: selectedPhaseId } })"
          >
            {{ user.first_name }} {{ user.last_name }} - {{ user.email }}
          </p>
        </div>

        <!-- Actions -->
        <div class="flex items-center space-x-2">
          <BaseButton
            @click="$router.push(`/users/edit/${user.id}`)"
            class="p-2 rounded-full"
            variant="edit"
            tooltip="Edit user"
          >
            <PencilIcon class="h-5 w-5" />
          </BaseButton>

          <BaseButton
            @click="$router.push(`/users/${user.id}/evaluation`)"
            class="p-2 rounded-full"
            variant="view"
            tooltip="View Evaluation for User"
          >
            <ChartBarIcon class="h-5 w-5" />
          </BaseButton>

          <BaseButton
            @click="confirmDelete(user.id)"
            class="p-2 rounded-full"
            variant="delete"
            tooltip="Delete user"
          >
            <TrashIcon class="h-5 w-5" />
          </BaseButton>
        </div>
      </li>
    </ul>

    <!-- Empty state -->
    <p v-if="!users.length" class="text-gray-500 mt-4 text-center">
      No users found.
    </p>

    <!-- Confirm Modal -->
    <ConfirmModal
      :isOpen="showDeleteModal"
      title="Delete User"
      message="Are you sure you want to delete this user?"
      @confirm="deleteConfirmed"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<script>
import { getUsers, deleteUser } from "../../api/users";
import { getSessions } from "../../api/sessions";
import { PencilIcon, TrashIcon, ChartBarIcon  } from "@heroicons/vue/24/solid";
import BaseButton from "../BaseComponents/BaseButton.vue";
import ConfirmModal from "../BaseComponents/ConfirmModal.vue";
import BaseSelect from "../BaseComponents/BaseSelect.vue";

export default {
  components: { PencilIcon, ChartBarIcon , TrashIcon, BaseButton, BaseSelect, ConfirmModal },
  data() {
    return {
      users: [],
      sessions: [],
      selectedPhaseId: null,
      showDeleteModal: false,
      userToDelete: null,
    };
  },
  computed: {
    phaseGroups() {
      return this.sessions.map(session => ({
        label: session.title,
        options: session.phases.map(phase => ({
          value: phase.id.toString(),
          label: phase.title,
        })),
      }));
    },
  },
  methods: {
    async fetchSessions() {
      try {
        const res = await getSessions();
        this.sessions = res.data;
      } catch (err) {
        console.error("Failed to load sessions:", err);
      }
    },

    async fetchUsers() {
      try {
        const res = await getUsers();
        this.users = res.data.sort((a, b) => {
          const last = a.last_name.localeCompare(b.last_name, "en", { sensitivity: "base" });
          if (last !== 0) return last;
          return a.first_name.localeCompare(b.first_name, "en", { sensitivity: "base" });
        });
      } catch (err) {
        console.error("Failed to load users:", err);
      }
    },

    confirmDelete(userId) {
      this.userToDelete = userId;
      this.showDeleteModal = true;
    },

    async deleteConfirmed() {
      if (this.userToDelete) {
        await deleteUser(this.userToDelete);
        this.showDeleteModal = false;
        this.userToDelete = null;
        this.fetchUsers();
      }
    },
  },

  async mounted() {
    await this.fetchSessions();
    await this.fetchUsers();
  },
};
</script>
