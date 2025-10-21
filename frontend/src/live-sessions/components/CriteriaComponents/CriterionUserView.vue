<template>
  <div class="max-w-7xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-2xl font-bold text-gray-800">
        {{ criterion?.name }} — Edit for All Users
      </h2>

      <BaseButton
        variant="switch"
        :disabled="!userCriteria.length"
        @click="$router.push({ path: `/users/${userCriteria[0]?.user?.id}`, query: { session: selectedSessionId } })"
        tooltip="Switch to User View"
      >
        <ArrowsRightLeftIcon class="h-5 w-5" />
      </BaseButton>
    </div>

    <!-- Criterion & Session Select -->
    <div class="mb-6 flex flex-col md:flex-row md:items-end md:space-x-6">
      <div class="w-full md:w-1/3">
        <label class="block mb-2 font-semibold">Select Criterion:</label>
        <BaseSelect
          v-model="selectedCriterionId"
          :options="criterionOptions"
          placeholder="-- Select Criterion --"
        />
      </div>

      <div class="w-full md:w-1/3 mt-4 md:mt-0">
        <label class="block mb-2 font-semibold">Select Session:</label>
        <BaseSelect
          v-model="selectedSessionId"
          :options="sessionOptions"
          placeholder="-- Select Session --"
        />
      </div>
    </div>

    <!-- No session selected -->
    <p v-if="!selectedSessionId" class="text-gray-500 text-center mt-4">
      Please select a session before criteria are displayed.
    </p>

    <!-- Criterion not in session -->
    <p v-else-if="filteredUserCriteria.length === 0" class="text-gray-500 text-center mt-4">
      This criterion is not part of the selected session.
    </p>

    <!-- UserCriteria Table -->
    <div v-else-if="userCriteria.length">
      <table class="w-full border-collapse border border-gray-200 rounded-lg">
        <thead class="bg-gray-100">
          <tr>
            <th class="p-3 text-left text-sm font-semibold text-gray-600">User</th>
            <th class="p-3 text-left text-sm font-semibold text-gray-600">Value</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="uc in filteredUserCriteria"
            :key="uc.user?.id"
            class="border-t border-gray-200 hover:bg-gray-50"
          >
            <td class="p-3 text-gray-800">
              {{ uc.user?.first_name }} {{ uc.user?.last_name }}
            </td>
            <td class="p-3">
              <!-- Countable -->
              <div v-if="criterion?.type === 'countable'" class="flex items-center space-x-2">
                <BaseButton @click="updateCount(uc, -1)">
                  <MinusIcon class="h-5 w-5" />
                </BaseButton>
                <span class="text-gray-700 font-bold text-lg">{{ uc.count_value ?? 0 }}</span>
                <BaseButton @click="updateCount(uc, 1)">
                  <PlusIcon class="h-5 w-5" />
                </BaseButton>
              </div>

              <!-- Boolean -->
              <div v-else-if="criterion?.type === 'boolean'">
                <input
                  type="checkbox"
                  v-model="uc.is_fulfilled"
                  @change="updateBoolean(uc)"
                  class="h-5 w-5 text-indigo-600"
                />
              </div>

              <!-- Text -->
              <div v-else-if="criterion?.type === 'text'" class="relative">
                <textarea
                  v-model="uc.text_value"
                  @focus="uc.isTextareaActive = true"
                  @blur="hideDropdown(uc)"
                  class="border rounded-md p-2 w-full text-gray-700 resize-y"
                  placeholder="Enter text..."
                  rows="3"
                />

                <!-- Commit Button -->
                <BaseButton
                  v-if="uc.isTextareaActive"
                  @click="updateText(uc)"
                  class="absolute top-2 right-2 px-2 py-1 text-sm"
                >
                  Save
                </BaseButton>

                <!-- History Dropdown -->
                <ul
                  v-if="uc.isTextareaActive && uc.historyOptions?.length"
                  class="absolute z-10 w-full bg-white border rounded-md mt-1 max-h-40 overflow-y-auto"
                >
                  <li
                    v-for="(item, index) in uc.historyOptions"
                    :key="index"
                    @mousedown.prevent="selectHistory(uc, item)"
                    class="p-2 hover:bg-gray-100 cursor-pointer"
                  >
                    {{ item }}
                  </li>
                </ul>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- No users for this session -->
    <p v-else class="text-gray-500 text-center mt-4">
      No users found for this criterion in the selected session.
    </p>
  </div>
</template>

<script>
import BaseButton from "@/BaseComponents/BaseButton.vue";
import BaseSelect from "@/BaseComponents/BaseSelect.vue";
import { PlusIcon, MinusIcon, ArrowsRightLeftIcon } from "@heroicons/vue/24/solid";
import {
  getCriterias,
  getUserCriteriasForCriterion,
  incrementUserCriterion,
  decrementUserCriterion,
  setBooleanValue,
  setTextValue,
} from "@/live-sessions/api/criterias";
import { getSessions } from "@/live-sessions/api/sessions";

export default {
  components: { BaseSelect, BaseButton, PlusIcon, MinusIcon, ArrowsRightLeftIcon },
  data() {
    return {
      criterias: [],
      sessions: [],
      selectedCriterionId: this.$route.params.id || "",
      selectedSessionId: this.$route.query.session || "",
      criterion: null,
      userCriteria: [],
    };
  },
  computed: {
    criterionOptions() {
      return this.criterias.map(c => ({ value: c.id.toString(), label: c.name }));
    },
    sessionOptions() {
      const flattenChildren = (children, depth = 0) =>
        children.flatMap(c => [
          { value: c.id.toString(), label: `${"— ".repeat(depth)}${c.title}` },
          ...(c.children?.length ? flattenChildren(c.children, depth + 1) : []),
        ]);

      return this.sessions.flatMap(s => [
        { value: s.id.toString(), label: s.title },
        ...(s.children ? flattenChildren(s.children, 1) : []),
      ]);
    },
    filteredUserCriteria() {
      return this.userCriteria.filter(uc => uc.session_id.toString() === this.selectedSessionId);
    },
  },
  watch: {
    async selectedCriterionId() {
      await this.fetchData();
    },
    async selectedSessionId() {
      await this.fetchData();
    },
  },
  methods: {
    async fetchCriterias() {
      const res = await getCriterias();
      this.criterias = res.data.sort((a, b) => a.name.localeCompare(b.name));
    },
    async fetchSessions() {
      const res = await getSessions();
      this.sessions = res.data;
    },
    async fetchData() {
      if (!this.selectedCriterionId || !this.selectedSessionId) {
        this.userCriteria = [];
        this.criterion = null;
        return;
      }

      if (!this.criterias.length) await this.fetchCriterias();
      this.criterion = this.criterias.find(c => c.id.toString() === this.selectedCriterionId);

      const res = await getUserCriteriasForCriterion(this.selectedCriterionId, this.selectedSessionId);

      this.userCriteria = res.data.map(uc => ({
        ...uc,
        text_value: uc.active_text || "",
        historyOptions: uc.last_texts?.slice(0, 5) || [],
        isTextareaActive: false,
      }));
    },
    async updateCount(uc, delta) {
      const newValue = (uc.count_value || 0) + delta;
      uc.count_value = Math.max(0, newValue);
      if (delta > 0)
        await incrementUserCriterion(this.selectedCriterionId, uc.user.id, this.selectedSessionId);
      else
        await decrementUserCriterion(this.selectedCriterionId, uc.user.id, this.selectedSessionId);
    },
    async updateBoolean(uc) {
      await setBooleanValue(this.selectedCriterionId, uc.user.id, this.selectedSessionId, uc.is_fulfilled);
    },
    hideDropdown(uc) {
      setTimeout(() => (uc.isTextareaActive = false), 100);
    },
    selectHistory(uc, text) {
      uc.text_value = text;
    },
    async updateText(uc) {
      if (!uc.text_value) return;
      await setTextValue(this.selectedCriterionId, uc.user.id, this.selectedSessionId, uc.text_value);

      if (!uc.historyOptions) uc.historyOptions = [];
      const existingIndex = uc.historyOptions.indexOf(uc.text_value);
      if (existingIndex !== -1) uc.historyOptions.splice(existingIndex, 1);
      uc.historyOptions.unshift(uc.text_value);
      uc.historyOptions = uc.historyOptions.slice(0, 5);

      uc.isTextareaActive = false;
      this.fetchData();
    },
  },
  async mounted() {
    await Promise.all([this.fetchCriterias(), this.fetchSessions()]);
    await this.fetchData();
  },
};
</script>
