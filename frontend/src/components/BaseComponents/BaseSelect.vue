<template>
  <select
    v-bind="$attrs"
    :value="modelValue"
    class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
    @change="$emit('update:modelValue', $event.target.value)"
  >
    <option disabled value="">{{ placeholder }}</option>
    <option
      v-for="option in options"
      :key="option.value"
      :value="option.value"
    >
      {{ option.label }}
    </option>
  </select>
</template>

<script>
export default {
  props: {
    modelValue: String,
    options: {
      type: Array,
      default: () => [],
    },
    placeholder: {
      type: String,
      default: "Select",
    },
  },
};
</script>
