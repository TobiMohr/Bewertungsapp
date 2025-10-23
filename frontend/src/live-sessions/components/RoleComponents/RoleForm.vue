<template>
  <div class="max-w-md mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">
      {{ isEdit ? "Edit Role" : "Create Role" }}
    </h2>

    <form @submit.prevent="submitForm" class="space-y-4">
      <BaseInput v-model="role.name" placeholder="Role Name" required />
      <BaseInput v-model="role.description" placeholder="Description (optional)" />

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
import { createRole, updateRole, getRole } from "@/live-sessions/api/roles";

export default {
  components: { BaseInput, BaseButton },
  data() {
    return {
      role: { id: null, name: "", description: "" },
      isEdit: false,
    };
  },
  async created() {
    const roleId = this.$route.params.id;
    if (roleId) {
      this.isEdit = true;
      try {
        const response = await getRole(roleId);
        this.role = { ...response.data };
      } catch (err) {
        alert("Failed to load role data");
        this.$router.push("/roles");
      }
    }
  },
  methods: {
    async submitForm() {
      if (!this.role.name.trim()) {
        alert("Role name cannot be empty");
        return;
      }

      try {
        if (this.isEdit) {
          await updateRole(this.role.id, { name: this.role.name, description: this.role.description });
        } else {
          await createRole({ name: this.role.name, description: this.role.description });
        }
        this.$router.push("/roles");
      } catch (err) {
        alert(err.response?.data?.detail || "Operation failed");
      }
    },
    cancel() {
      this.$router.push("/roles");
    },
  },
};
</script>
