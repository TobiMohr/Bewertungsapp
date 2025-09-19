<template>
  <input
    v-bind="$attrs"
    :value="modelValue"
    :placeholder="placeholder"
    class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
    @input="$emit('update:modelValue', $event.target.value)"
  />
</template>

<script>
export default {
  props: {
    modelValue: String,
    placeholder: String,
  },
};
</script>
