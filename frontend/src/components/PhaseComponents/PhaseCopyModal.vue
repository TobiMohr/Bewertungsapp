<template>
  <!-- Background overlay -->
  <div
    v-if="show"
    class="fixed inset-0 flex items-center justify-center bg-gray-800 bg-opacity-50 z-50"
  >
    <!-- Modal box -->
    <div class="bg-white rounded-xl shadow-lg p-6 w-full max-w-md">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">
        Copy Phase
      </h3>

      <p class="text-sm text-gray-500 mb-4">
        Enter a name for the copied phase. You can adjust the title if needed.
      </p>

      <!-- Input field for title -->
      <BaseInput
        v-model="title"
        label="Title"
        placeholder="Enter new phase title"
        class="w-full mb-4"
      />

      <!-- Buttons -->
      <div class="flex justify-end space-x-3 pt-2">
        <BaseButton variant="cancel" @click="$emit('cancel')">
          Cancel
        </BaseButton>
        <BaseButton variant="primary" @click="confirmCopy">
          Confirm
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script>
import BaseInput from "../BaseComponents/BaseInput.vue";
import BaseButton from "../BaseComponents/BaseButton.vue";

export default {
  name: "CopyPhaseModal",
  components: { BaseInput, BaseButton },
  props: {
    show: {
      type: Boolean,
      required: true,
    },
    defaultTitle: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      title: this.defaultTitle,
    };
  },
  watch: {
    defaultTitle(newVal) {
      this.title = newVal;
    },
  },
  methods: {
    confirmCopy() {
      if (!this.title.trim()) return;
      this.$emit("confirm", this.title.trim());
    },
  },
};
</script>

<style scoped>
/* Optional fade-in transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
