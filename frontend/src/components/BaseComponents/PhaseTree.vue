<template>
  <ul class="space-y-1">
    <li v-for="item in items" :key="item.id">
      <div
        class="flex items-center justify-between cursor-pointer px-2 py-1 rounded-md hover:bg-emerald-100"
        :class="item.id === activeId ? 'bg-emerald-200 font-semibold' : 'text-gray-700'"
        @click.stop="$emit('select', item, item.phases?.length ? 'session' : 'phase')"
      >
        <div class="flex items-center gap-2">
          <!-- Expand/Collapse icon -->
          <span v-if="item.phases && item.phases.length" @click.stop="toggle(item.id)">
            <ChevronRightIcon
              v-if="!isExpanded(item.id)"
              class="w-4 h-4 text-gray-500"
            />
            <ChevronDownIcon
              v-else
              class="w-4 h-4 text-gray-500"
            />
          </span>

          <span>{{ item.title }}</span>
        </div>
      </div>

      <!-- Recursive child phases -->
      <PhaseTree
        v-if="item.phases && item.phases.length && isExpanded(item.id)"
        :items="item.phases"
        :activeId="activeId"
        @select="$emit('select', $event, $eventType)"
        class="ml-4 border-l border-gray-200 pl-2"
      />
    </li>
  </ul>
</template>

<script>
import { ref } from 'vue';
import { ChevronRightIcon, ChevronDownIcon } from '@heroicons/vue/24/solid';

export default {
  name: 'PhaseTree',
  components: { ChevronRightIcon, ChevronDownIcon },
  props: {
    items: {
      type: Array,
      required: true,
    },
    activeId: {
      type: Number,
      default: null,
    },
  },
  setup() {
    const expandedIds = ref(new Set());

    const toggle = (id) => {
      if (expandedIds.value.has(id)) {
        expandedIds.value.delete(id);
      } else {
        expandedIds.value.add(id);
      }
    };

    const isExpanded = (id) => expandedIds.value.has(id);

    return { expandedIds, toggle, isExpanded };
  },
};
</script>

<style scoped>
ul {
  list-style-type: none;
  padding-left: 0;
}
</style>
