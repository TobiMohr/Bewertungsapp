<template>
  <div class="max-w-7xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">

    <div class="flex items-center justify-between mb-4">
      <!-- Header -->
      <h2 class="text-2xl font-bold text-gray-800 mb-2">
        {{ phase?.title }} from {{ user?.first_name }} {{ user?.last_name }}
      </h2>

      <BaseButton
        variant="switch"
        @click="$router.push({ path: `/criterias/1/users`, query: { phase: selectedPhaseId } })"
        tooltip="Switch to Criterion View"
      >
        <ArrowsRightLeftIcon class="h-5 w-5" />
      </BaseButton>
    </div>
    
    <!-- Phase & User Selection -->
    <div class="mb-6 flex flex-col md:flex-row md:items-end md:space-x-6">
      <!-- Phase Select -->
      <div class="w-full md:w-1/4">
        <label class="block mb-2 font-semibold">Select Phase:</label>
        <BaseSelect
          v-model="selectedPhaseId"
          :groups="phaseGroups"
          placeholder="-- Select Phase --"
        />
      </div>

      <!-- User Select -->
      <div class="w-full md:w-1/4 mt-4 md:mt-0">
        <label class="block mb-2 font-semibold">Select User:</label>
        <BaseSelect
          v-model="selectedUserId"
          :options="userOptions"
          placeholder="-- Select User --"
        />
      </div>
    </div>

    <h3 class="text-xl font-semibold text-gray-700 mb-4">Criteria</h3>

    <!-- Criteria grid -->
    <div v-if="criteria.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="c in criteria"
        :key="c.id"
        class="flex justify-between items-center p-3 border rounded-lg shadow-sm"
      >
        <p class="text-gray-900 font-medium">{{ c.criterion.name }}</p>

        <!-- Countable criterion -->
        <div v-if="c.criterion.type === 'countable'" class="flex items-center space-x-2">
          <BaseButton @click="decrement(c.criterion_id)">
            <MinusIcon class="h-5 w-5" />
          </BaseButton>
          <span class="text-gray-700 font-bold text-lg">{{ c.count_value ?? 0 }}</span>
          <BaseButton @click="increment(c.criterion_id)">
            <PlusIcon class="h-5 w-5" />
          </BaseButton>
        </div>

        <!-- Text criterion -->
        <div v-else-if="c.criterion.type === 'text'" class="flex items-center">
          <DocumentTextIcon
            class="h-6 w-6 text-indigo-500 hover:text-indigo-600 cursor-pointer"
            :title="c.text_value ? 'Edit Text' : 'Add Text'"
            @click="openTextModal(c)"
          />
        </div>

        <!-- Boolean criterion -->
        <div v-else>
          <label class="flex items-center cursor-pointer">
            <input
              type="checkbox"
              v-model="c.is_fulfilled"
              class="form-checkbox h-5 w-5 text-indigo-600"
              @change="toggleBoolean(c.criterion_id, c.is_fulfilled)"
            />
          </label>
        </div>
      </div>
    </div>

    <p v-else class="text-gray-500 mt-4 text-center">
      No criteria assigned to this user.
    </p>

    <!-- Modal -->
    <transition name="fade">
      <div
        v-if="showTextModal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      >
        <div class="bg-white rounded-xl shadow-lg max-w-md w-full p-6">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">
            Text für {{ activeCriterion?.criterion.name }}
          </h3>

          <!-- Textarea with search-history dropdown -->
          <div class="relative">
            <textarea
              v-model="textDraft"
              class="w-full border rounded-md p-2 text-gray-700 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              @input="filterHistory"
              @focus="isTextareaActive = true"
              @blur="hideDropdown"
              rows="4"
              placeholder="Enter text..."
            ></textarea>

            <ul
              v-if="isTextareaActive && filteredHistory.length"
              class="absolute z-10 w-full bg-white border rounded-md mt-1 max-h-40 overflow-y-auto"
            >
              <li
                v-for="(item, index) in filteredHistory"
                :key="index"
                @mousedown.prevent="selectHistory(item)"
                class="p-2 hover:bg-gray-100 cursor-pointer"
              >
                {{ item }}
              </li>
            </ul>
          </div>

          <div class="flex justify-between mt-6">
            <BaseButton variant="cancel" @click="cancelText">Cancel</BaseButton>
            <BaseButton @click="saveText">Save</BaseButton>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script>
import BaseButton from "../BaseComponents/BaseButton.vue";
import BaseSelect from "../BaseComponents/BaseSelect.vue";
import { getUsers, getUser } from "../../api/users";
import { getPhase } from "../../api/phases";
import { getSessions } from "../../api/sessions";
import {
  getUserCriterias,
  incrementUserCriterion,
  decrementUserCriterion,
  setBooleanValue,
  setTextValue,
} from "../../api/criterias";
import { DocumentTextIcon, PlusIcon, MinusIcon, ArrowsRightLeftIcon } from "@heroicons/vue/24/solid";

export default {
  components: { BaseButton, BaseSelect, DocumentTextIcon, PlusIcon, MinusIcon, ArrowsRightLeftIcon },
  data() {
    return {
      sessions: [],
      selectedPhaseId: "",
      users: [],
      user: null,
      selectedUserId: "",
      criteria: [],
      showTextModal: false,
      activeCriterion: null,
      textDraft: "",
      filteredHistory: [],
      isTextareaActive: false,
      phase: null,
    };
  },
  computed: {
    phaseGroups() {
      const flattenPhases = (phases, depth = 0) => {
        return phases.flatMap(phase => [
          {
            value: phase.id.toString(),
            label: `${"— ".repeat(depth)}${phase.title}`,
          },
          ...(phase.children?.length ? flattenPhases(phase.children, depth + 1) : []),
        ]);
      };

      return this.sessions.map(session => ({
        label: session.title,
        options: flattenPhases(session.phases || []),
      }));
    },

    userOptions() {
      return this.users.map(u => ({
        value: u.id.toString(),
        label: `${u.first_name} ${u.last_name}`,
      }));
    },
  },
  watch: {
    selectedPhaseId(newPhaseId) {
      this.fetchData(this.selectedUserId, newPhaseId);
    },
    selectedUserId(newUserId) {
      this.fetchData(newUserId, this.selectedPhaseId);
    },
  },
  methods: {
    getStorageKey(criterionId) {
      return `criterion_text_history_${criterionId}`;
    },
    filterHistory() {
      const history = JSON.parse(localStorage.getItem(this.getStorageKey(this.activeCriterion.criterion_id))) || [];
      const search = this.textDraft.toLowerCase();
      this.filteredHistory = history.filter(entry => entry.toLowerCase().includes(search));
    },
    hideDropdown() {
      setTimeout(() => (this.isTextareaActive = false), 100);
    },
    selectHistory(item) {
      this.textDraft = item;
      this.filteredHistory = [];
    },
    async fetchSessions() {
      const res = await getSessions();
      this.sessions = res.data;
      const routePhaseId = this.$route.query.phase;
      if (routePhaseId) this.selectedPhaseId = routePhaseId.toString();
    },
    async fetchUsers() {
      const res = await getUsers();
      this.users = res.data;
      const routeUserId = this.$route.params.id;
      if (!this.selectedUserId && routeUserId)
        this.selectedUserId = routeUserId.toString();
    },
    async fetchData(userIdOverride, phaseIdOverride) {
      const userId = userIdOverride || this.selectedUserId;
      const phaseId = phaseIdOverride || this.selectedPhaseId;
      if (!phaseId || !userId) return;

      const [userRes, critRes, phaseRes] = await Promise.all([
        getUser(userId),
        getUserCriterias(userId, phaseId),
        getPhase(phaseId),
      ]);

      this.user = userRes.data;
      this.phase = phaseRes.data;
      this.criteria = critRes.data.sort((a, b) =>
        a.criterion.name.localeCompare(b.criterion.name, "en", { sensitivity: "base" })
      );
    },
    async increment(id) {
      const crit = this.criteria.find(c => c.criterion_id === id);
      if (crit) crit.count_value = (crit.count_value || 0) + 1;
      await incrementUserCriterion(id, this.selectedUserId, this.selectedPhaseId);
    },
    async decrement(id) {
      const crit = this.criteria.find(c => c.criterion_id === id);
      if (crit) crit.count_value = Math.max((crit.count_value || 0) - 1, 0);
      await decrementUserCriterion(id, this.selectedUserId, this.selectedPhaseId);
    },
    async toggleBoolean(id, value) {
      await setBooleanValue(id, this.selectedUserId, this.selectedPhaseId, !!value);
    },
    openTextModal(c) {
      this.activeCriterion = c;
      this.textDraft = c.text_value || "";
      this.showTextModal = true;
      this.filterHistory();
    },
    cancelText() {
      this.showTextModal = false;
      this.activeCriterion = null;
      this.textDraft = "";
      this.filteredHistory = [];
    },
    saveTextToLocalStorage(text) {
      const key = this.getStorageKey(this.activeCriterion.criterion_id);
      let history = JSON.parse(localStorage.getItem(key)) || [];
      history = history.filter(entry => entry !== text);
      history.unshift(text);
      localStorage.setItem(key, JSON.stringify(history.slice(0, 5)));
    },
    async saveText() {
      if (!this.activeCriterion) return;
      await setTextValue(
        this.activeCriterion.criterion_id,
        this.selectedUserId,
        this.selectedPhaseId,
        this.textDraft
      );
      this.activeCriterion.text_value = this.textDraft;
      this.saveTextToLocalStorage(this.textDraft);
      this.cancelText();
    },
  },
  async mounted() {
    await Promise.all([this.fetchSessions(), this.fetchUsers()]);
    await this.fetchData();
  },
};
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
