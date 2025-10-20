<template>
  <button
    v-bind="$attrs"
    :class="[
      'px-4 py-2 rounded-md text-white font-medium transition disabled:opacity-50',
      variantClasses
    ]"
    :title="tooltip"
  >
    <slot />
  </button>
</template>

<script>
export default {
  props: {
    variant: { type: String, default: 'primary' },
    tooltip: { type: String, default: ''}
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
        case 'copy':
          return 'bg-cyan-500 hover:bg-cyan-600'
        case 'switch':
          return 'bg-indigo-500 hover:bg-indigo-600'
        default:
          return 'bg-emerald-500 hover:bg-emerald-600';
      }
    },
  },
};
</script>
