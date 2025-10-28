<template>
  <div class="max-w-md mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">
      {{ isEdit ? "Edit User" : "Create User" }}
    </h2>

    <form @submit.prevent="submitForm" class="space-y-4">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">First Name</label>
          <BaseInput v-model="user.first_name" placeholder="First Name" required />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
          <BaseInput v-model="user.last_name" placeholder="Last Name" required />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">E-Mail</label>
          <BaseInput v-model="user.email" type="email" placeholder="Email" required />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
          <BaseInput v-model="user.username" placeholder="Username" required />
        </div>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Team</label>
        <BaseSelect
          v-model="user.team_id"
          :options="teamOptions"
          placeholder="Select a team"
          :showPlaceholder="true"
        />
      </div>
      <div v-if="!isEdit">
        <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
        <BaseInput
          v-model="user.password"
          type="password"
          placeholder="Password"
          required
        />
      </div>

      <!-- Buttons -->
      <div class="flex justify-between pt-4">
        <BaseButton
          type="button"
          variant="cancel"
          @click="cancel"
        >
          Cancel
        </BaseButton>

        <BaseButton type="submit">
          {{ isEdit ? "Update" : "Create" }}
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<script>
import BaseInput from "@/BaseComponents/BaseInput.vue";
import BaseButton from "@/BaseComponents/BaseButton.vue";
import BaseSelect from "@/BaseComponents/BaseSelect.vue";
import { createUser, updateUser, getUser } from "@/live-sessions/api/users";
import { getTeams } from "@/live-sessions/api/teams";

export default {
  components: { BaseInput, BaseButton, BaseSelect },
  data() {
    return {
      user: {
        id: null,
        first_name: "",
        last_name: "",
        team_id: null,
        email: "",
        username: "", // added username
        password: "",
      },
      teams: [],
      isEdit: false,
      loading: true,
    };
  },
  computed: {
    teamOptions() {
      return this.teams.map(team => ({
        value: team.id,
        label: team.name,
      }));
    },
  },
  async created() {
    try {
      // Load teams first
      const teamsRes = await getTeams();
      this.teams = teamsRes.data;

      const userId = this.$route.params.id;
      if (userId) {
        this.isEdit = true;
        const userRes = await getUser(userId);
        this.user = {
          ...userRes.data,
          password: "", // never load password
          team_id: userRes.data.team ? userRes.data.team.id : null,
          username: userRes.data.username || "", // ensure username is loaded
        };
      }
    } catch (err) {
      console.error("Failed to load data", err);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    async submitForm() {
      try {
        if (this.isEdit) {
          const payload = { ...this.user };
          delete payload.password; // password cannot be updated
          await updateUser(this.user.id, payload);
        } else {
          await createUser(this.user);
        }
        this.$router.push("/users");
      } catch (err) {
        alert(err.response?.data?.detail || "Operation failed");
      }
    },
    cancel() {
      this.$router.push("/users");
    },
  },
};
</script>
