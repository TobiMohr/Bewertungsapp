<template>
  <div class="max-w-md mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">
      {{ isEdit ? "Edit Team" : "Create Team" }}
    </h2>

    <form @submit.prevent="submitForm" class="space-y-4">
      <BaseInput v-model="team.name" placeholder="Team Name" required />

      <!-- Buttons -->
      <div class="flex justify-between pt-4">
        <BaseButton type="button" variant="cancel" @click="cancel">
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
import { createTeam, updateTeam, getTeam, getTeams } from "@/live-sessions/api/teams";

export default {
  components: { BaseInput, BaseButton },
  data() {
    return {
      team: { id: null, name: "" },
      isEdit: false,
    };
  },
  async created() {
    const teamId = this.$route.params.id;

    if (teamId) {
      this.isEdit = true;
      try {
        const response = await getTeam(teamId);
        this.team = { ...response.data };
      } catch (err) {
        alert("Failed to load team data");
        this.$router.push("/teams");
      }
    } else {
      try {
        const response = await getTeams();
        const existingTeams = response.data || [];
        const nextNumber = existingTeams.length + 1;
        this.team.name = `Team ${nextNumber}`;
      } catch (err) {
        console.error("Failed to fetch teams", err);
        this.team.name = "Team 1";
      }
    }
  },
  methods: {
    async submitForm() {
      if (!this.team.name.trim()) {
        alert("Team name cannot be empty");
        return;
      }

      try {
        if (this.isEdit) {
          await updateTeam(this.team.id, { name: this.team.name });
        } else {
          await createTeam({ name: this.team.name });
        }
        this.$router.push("/teams");
      } catch (err) {
        alert(err.response?.data?.detail || "Operation failed");
      }
    },
    cancel() {
      this.$router.push("/teams");
    },
  },
};
</script>
