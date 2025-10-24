<!-- src/components/BaseComponents/Dialog.vue -->
<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-white rounded-xl shadow-lg w-full max-w-md mx-4">
      <!-- Header -->
      <div class="px-6 py-4 border-b">
        <h3 class="text-lg font-semibold text-gray-800">
          <slot name="title"></slot>
        </h3>
      </div>

      <!-- Content -->
      <div class="px-6 py-4">
        <slot name="content"></slot>
      </div>

      <!-- Actions -->
      <div class="px-6 py-4 border-t flex justify-between space-x-2">
        <slot name="actions"></slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  emits: ["close"],
  mounted() {
    // close modal on ESC
    window.addEventListener("keydown", this.handleEsc);
  },
  unmounted() {
    window.removeEventListener("keydown", this.handleEsc);
  },
  methods: {
    handleEsc(e) {
      if (e.key === "Escape") this.$emit("close");
    },
  },
};
</script>

<style scoped>
/* optional: smooth fade-in/out */
</style>
