<template>
  <div class="p-3 border rounded-lg shadow-sm">
    <p class="text-gray-900 font-medium">{{ comment.text }}</p>
    <p class="text-gray-400 text-sm mt-1">Created: {{ formatDate(comment.created_at) }}</p>
  </div>
</template>

<script>
export default {
  name: "BaseCommentComponent",
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
