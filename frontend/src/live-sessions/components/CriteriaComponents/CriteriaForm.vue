<template> 
  <div class="max-w-md mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">
      {{ isEdit ? "Edit Criterion" : "Create Criterion" }}
    </h2>

    <form @submit.prevent="submitForm" class="space-y-4">
      <!-- Criterion Name -->
      <BaseInput
        v-model="criterion.name"
        placeholder="Criterion Name"
        required
      />

      <!-- Criterion Type (disabled if editing) -->
      <BaseSelect
        v-model="criterion.type"
        :options="typeOptions"
        placeholder="Select Type"
        :showPlaceholder="true"
        :disabled="isEdit"
        required
      />

      <!-- Buttons -->
      <div class="flex justify-between pt-4">
        <!-- Cancel button on the left -->
        <BaseButton
          type="button"
          variant="cancel"
          @click="$router.push('/criterias')"
        >
          Cancel
        </BaseButton>

        <!-- Submit button on the right -->
        <BaseButton type="submit">
          {{ isEdit ? "Save" : "Create" }}
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<script>
import BaseInput from "@/BaseComponents/BaseInput.vue";
import BaseButton from "@/BaseComponents/BaseButton.vue";
import BaseSelect from "@/BaseComponents/BaseSelect.vue";
import { createCriterion, updateCriterion, getCriterion } from "@/live-sessions/api/criterias";

export default {
  components: { BaseInput, BaseButton, BaseSelect },
  data() {
    return {
      criterion: { name: "", type: "" },
      typeOptions: [
        { label: "Boolean", value: "boolean" },
        { label: "Countable", value: "countable" },
        { label: "Text", value: "text" },
      ],
      isEdit: false,
    };
  },
  async mounted() {
    const criterionId = this.$route.params.id;
    if (criterionId) {
      this.isEdit = true;
      try {
        const res = await getCriterion(criterionId);
        this.criterion = { ...res.data };
      } catch (err) {
        alert(err.response?.data?.detail || "Failed to load criterion");
        this.$router.push("/criterias");
      }
    }
  },
  methods: {
    async submitForm() {
      try {
        if (this.isEdit) {
          await updateCriterion(this.$route.params.id, { name: this.criterion.name });
        } else {
          await createCriterion(this.criterion);
        }
        this.$router.push("/criterias");
      } catch (err) {
        alert(err.response?.data?.detail || "Failed to save criterion");
      }
    },
  },
};
</script>
