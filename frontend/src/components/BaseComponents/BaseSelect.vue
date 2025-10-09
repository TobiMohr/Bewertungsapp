<template>
  <select
    v-bind="$attrs"
    :value="modelValue"
    class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
    @change="onChange($event)"
  >
    <option disabled value="">{{ placeholder }}</option>

    <template v-if="groups.length">
      <optgroup
        v-for="group in groups"
        :key="group.label"
        :label="group.label"
      >
        <option
          v-for="option in group.options"
          :key="option.value"
          :value="option.value"
        >
          {{ option.label }}
        </option>
      </optgroup>
    </template>

    <template v-else>
      <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
      >
        {{ option.label }}
      </option>
    </template>
  </select>
</template>

<script>
export default {
  props: {
    modelValue: [String, Number],
    options: {
      type: Array,
      default: () => [],
    },
    groups: {
      type: Array,
      default: () => [],
    },
    placeholder: {
      type: String,
      default: "Select",
    },
  },
  methods: {
    onChange(event) {
      this.$emit('update:modelValue', event.target.value);
    },
  },
};
</script>
