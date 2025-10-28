<template>
  <div class="p-3 border rounded-lg shadow-sm flex justify-between items-start">
    <div>
      <p class="text-gray-900 font-medium">{{ comment.text }}</p>
      <p class="text-gray-400 text-sm mt-1">Created: {{ formatDate(comment.created_at) }}</p>
    </div>

    <BaseButton
      @click="$emit('delete-comment', comment.id)"
      class="p-2 rounded-full ml-2"
      variant="delete"
      tooltip="Delete comment"
    >
      <TrashIcon class="h-5 w-5" />
    </BaseButton>
  </div>
</template>

<script>
import BaseButton from "@/BaseComponents/BaseButton.vue";
import { TrashIcon } from "@heroicons/vue/24/solid";

export default {
  name: "BaseCommentComponent",
  components: { BaseButton, TrashIcon },
  props: {
    comment: { type: Object, required: true },
  },
  methods: {
    formatDate(dt) {
      return new Date(dt).toLocaleString();
    },
  },
};
</script>

<style scoped>
</style>
