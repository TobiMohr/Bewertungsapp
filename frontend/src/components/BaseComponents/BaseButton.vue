<template>
  <button
    v-bind="$attrs"
    :class="[
      'px-4 py-2 rounded-md text-white font-medium transition disabled:opacity-50',
      variantClasses
    ]"
  >
    <slot />
  </button>
</template>

<script>
export default {
  props: {
    variant: { type: String, default: 'primary' } // primary, gray, danger
  },
  computed: {
    variantClasses() {
      switch (this.variant) {
        case 'cancel':
          return 'bg-gray-400 hover:bg-gray-500 text-gray-800';
        case 'edit':
          return 'bg-yellow-400 hover:bg-yellow-500'
        case 'delete':
          return 'bg-red-600 hover:bg-red-700';
        default:
          return 'bg-green-600 hover:bg-green-700';
      }
    },
  },
};
</script>
