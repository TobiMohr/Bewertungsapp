<template>
  <transition name="fade">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
    >
      <div class="bg-white rounded-xl shadow-lg max-w-md w-full p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">{{ title }}</h3>
        <p class="text-gray-600 mb-6">{{ message }}</p>

        <div class="flex justify-end space-x-3">
            <!-- Cancel button first (left) -->
            <BaseButton @click="cancel" variant="cancel">
                Cancel
            </BaseButton>

            <!-- Delete button (right) -->
            <BaseButton @click="confirm" variant="delete">
                Delete
            </BaseButton>
        </div>

      </div>
    </div>
  </transition>
</template>

<script>
import BaseButton from "./BaseButton.vue";

export default {
  components: { BaseButton },
  props: {
    isOpen: { type: Boolean, required: true },
    title: { type: String, default: "Confirm Action" },
    message: { type: String, default: "Are you sure?" },
  },
  emits: ["confirm", "cancel"],
  methods: {
    confirm() {
      this.$emit("confirm");
    },
    cancel() {
      this.$emit("cancel");
    },
  },
};
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
