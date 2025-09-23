<template>
  <label class="relative inline-flex items-center cursor-pointer">
    <input
      type="checkbox"
      class="sr-only peer"
      :checked="modelValue"
      @change="$emit('update:modelValue', $event.target.checked)"
    />
    <div
      class="w-11 h-6 bg-gray-300 rounded-full peer peer-checked:bg-green-500 transition-colors"
    ></div>
    <div
      class="absolute left-1 top-1 w-4 h-4 bg-white rounded-full shadow-md transform transition-transform peer-checked:translate-x-5"
    ></div>
  </label>
</template>

<script>
export default {
  name: "BaseToggle",
  props: {
    modelValue: {
      type: Boolean,
      required: true,
    },
  },
  emits: ["update:modelValue"],
};
</script>
