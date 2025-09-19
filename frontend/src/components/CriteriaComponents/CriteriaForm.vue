<template>
  <div class="max-w-md mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">
      Create Criterion
    </h2>

    <form @submit.prevent="submitForm" class="space-y-4">
      <!-- Criterion Name -->
      <BaseInput
        v-model="criterion.name"
        placeholder="Criterion Name"
        required
      />

      <!-- Criterion Type -->
      <BaseSelect
        v-model="criterion.type"
        :options="typeOptions"
        placeholder="Select Type"
        required
        />

      <div class="flex space-x-2">
        <BaseButton type="submit">Create</BaseButton>
        <BaseButton
          type="button"
          class="bg-gray-400 hover:bg-gray-500"
          @click="$router.push('/criterias')"
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
import BaseSelect from "@/components/BaseComponents/BaseSelect.vue";
import { createCriterion } from "../../api/criterias";

export default {
  components: { BaseInput, BaseButton, BaseSelect },
  data() {
    return {
        criterion: { name: "", type: "" },
        typeOptions: [
        { label: "Boolean", value: "boolean" },
        { label: "Countable", value: "countable" },
        ],
    };
  },
  methods: {
    async submitForm() {
      try {
        await createCriterion(this.criterion);
        this.$router.push("/criterias");
      } catch (err) {
        alert(err.response?.data?.detail || "Failed to create criterion");
      }
    },
  },
};
</script>
