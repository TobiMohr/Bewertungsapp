<template>
  <div class="max-w-7xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <!-- Header -->
    <h2 class="text-2xl font-bold text-gray-800 mb-2">
      {{ phase?.title }} von {{ user?.first_name }} {{ user?.last_name }}
    </h2>
    <p class="text-gray-600 mb-2">{{ user?.email }}</p>

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
          <!-- Decrement Button -->
          <BaseButton @click="decrement(c.criterion_id)">
            <MinusIcon class="h-5 w-5" />
          </BaseButton>

          <!-- Current Count -->
          <span class="text-gray-700 font-bold text-lg">{{ c.count_value ?? 0 }}</span>

          <!-- Increment Button -->
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

              <textarea
                v-model="textDraft"
                class="w-full border rounded-md p-2 text-gray-700 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                rows="4"
                placeholder="Enter text..."
              ></textarea>

              <div class="flex justify-between mt-6">
                <BaseButton variant="cancel" @click="cancelText">Cancel</BaseButton>
                <BaseButton @click="saveText">Save</BaseButton>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <p v-else class="text-gray-500 mt-4 text-center">
      No criteria assigned to this user.
    </p>
  </div>
</template>

<script>
import BaseButton from "../BaseComponents/BaseButton.vue";
import { getUser } from "../../api/users";
import { getPhase } from "../../api/phases";
import { DocumentTextIcon, PlusIcon, MinusIcon } from "@heroicons/vue/24/solid";
import {
  getUserCriterias,
  incrementUserCriterion,
  decrementUserCriterion,
  setBooleanValue,
  setTextValue,
} from "../../api/criterias";

export default {
  components: { BaseButton, DocumentTextIcon, PlusIcon, MinusIcon },
  data() {
    return {
      user: null,
      criteria: [],
      showTextModal: false,
      activeCriterion: null,
      textDraft: "",
      phase: null,
    };
  },
  methods: {
    async fetchData() {
      const userId = this.$route.params.id;
      const phaseId = this.$route.query.phase;

      if (!phaseId) return;

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
    async increment(criterionId) {
      const userId = this.$route.params.id;
      const phaseId = this.$route.query.phase;

      // Optimistically update UI
      const crit = this.criteria.find(c => c.criterion_id === criterionId);
      if (crit) crit.count_value = (crit.count_value || 0) + 1;

      // Persist backend change
      await incrementUserCriterion(criterionId, userId, phaseId);
    },

    async decrement(criterionId) {
      const userId = this.$route.params.id;
      const phaseId = this.$route.query.phase;

      // Optimistically update UI
      const crit = this.criteria.find(c => c.criterion_id === criterionId);
      if (crit) crit.count_value = Math.max((crit.count_value || 0) - 1, 0);

      // Persist backend change
      await decrementUserCriterion(criterionId, userId, phaseId);
    },
    async toggleBoolean(criterionId, value) {
      const userId = this.$route.params.id;
      const phaseId = this.$route.query.phase;
      
      // ensure boolean
      const boolValue = value === true || value === "true";
      
      await setBooleanValue(criterionId, userId, phaseId, boolValue);
    },
    openTextModal(criterion) {
      this.activeCriterion = criterion;
      this.textDraft = criterion.text_value || "";
      this.showTextModal = true;
    },
    cancelText() {
      this.showTextModal = false;
      this.activeCriterion = null;
      this.textDraft = "";
    },
    async saveText() {
      if (!this.activeCriterion) return;
      const userId = this.$route.params.id;
      const phaseId = this.$route.query.phase;
      await setTextValue(this.activeCriterion.criterion_id, userId, phaseId, this.textDraft);
      this.activeCriterion.text_value = this.textDraft;
      this.cancelText();
    },
  },
  mounted() {
    this.fetchData();
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
