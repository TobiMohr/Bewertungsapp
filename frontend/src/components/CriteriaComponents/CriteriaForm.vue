<template>
  <div class="max-w-md mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">
      Create Criterion
    </h2>

    <form @submit.prevent="submitForm" class="space-y-4">
      <input
        v-model="criterion.name"
        placeholder="Criterion Name"
        class="input"
        required
      />

      <select v-model="criterion.type" class="input" required>
        <option disabled value="">Select Type</option>
        <option value="boolean">Boolean</option>
        <option value="countable">Countable</option>
      </select>

      <button type="submit" class="btn">Create</button>
      <button type="button" class="btn cancel" @click="$router.push('/criterias')">
        Cancel
      </button>
    </form>
  </div>
</template>

<script>
import { createCriterion } from "../../api/criterias";

export default {
  data() {
    return {
      criterion: { name: "", type: "" },
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

<style scoped>
.input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 0.375rem;
}
.btn {
  padding: 0.5rem 1rem;
  background-color: #4f46e5;
  color: white;
  border-radius: 0.375rem;
}
.btn.cancel {
  background-color: #9ca3af;
}
</style>
