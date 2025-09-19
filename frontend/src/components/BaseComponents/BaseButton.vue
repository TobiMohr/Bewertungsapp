<template>
  <button
    v-bind="$attrs"
    class="px-4 py-2 rounded-md text-white font-medium transition
           bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
  >
    <slot />
  </button>
</template>
