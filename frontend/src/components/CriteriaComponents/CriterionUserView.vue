<template>
  <div class="max-w-7xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <!-- Header with button inline -->
    <div class="flex items-center justify-between mb-4">
        <h2 class="text-2xl font-bold text-gray-800">
        {{ criterion?.name }} — Edit for All Users
        </h2>

        <BaseButton
        variant="switch"
        @click="$router.push({ path: `/users/${userCriteria[0]?.user?.id}`, query: { phase: selectedPhaseId } })"
        tooltip="Switch to User View"
        >
        <ArrowsRightLeftIcon class="h-5 w-5" />
        </BaseButton>
    </div>

    <!-- Phase & Criterion Selection -->
    <div class="mb-6 flex flex-col md:flex-row md:items-end md:space-x-6">
      <!-- Criterion Select -->
      <div class="w-full md:w-1/3">
        <label class="block mb-2 font-semibold">Select Criterion:</label>
        <BaseSelect
          v-model="selectedCriterionId"
          :options="criterionOptions"
          placeholder="-- Select Criterion --"
        />
      </div>

      <!-- Phase Select -->
      <div class="w-full md:w-1/3 mt-4 md:mt-0">
        <label class="block mb-2 font-semibold">Select Phase:</label>
        <BaseSelect
          v-model="selectedPhaseId"
          :groups="phaseGroups"
          placeholder="-- Select Phase --"
        />
      </div>
    </div>

    <!-- Show message if no phase selected -->
    <p v-if="!selectedPhaseId" class="text-gray-500 text-center mt-4">
      Please select a phase to display criteria for users.
    </p>

    <!-- User List -->
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
            v-for="uc in userCriteria"
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
              <div v-else-if="criterion?.type === 'text'">
                <textarea
                  v-model="uc.text_value"
                  @blur="updateText(uc)"
                  class="border rounded-md p-2 w-full text-gray-700 resize-y"
                  placeholder="Enter text..."
                ></textarea>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- No users for this criterion -->
    <p v-else class="text-gray-500 text-center mt-4">
      No users found for this criterion.
    </p>
  </div>
</template>

<script>
import BaseSelect from "../BaseComponents/BaseSelect.vue";
import BaseButton from "../BaseComponents/BaseButton.vue";
import { PlusIcon, MinusIcon, ArrowsRightLeftIcon } from "@heroicons/vue/24/solid";
import {
  getCriterias,
  getUserCriteriasForCriterion,
  incrementUserCriterion,
  decrementUserCriterion,
  setBooleanValue,
  setTextValue,
} from "../../api/criterias";
import { getSessions } from "../../api/sessions";

export default {
  components: { BaseSelect, BaseButton, PlusIcon, MinusIcon, ArrowsRightLeftIcon     },
  data() {
    return {
      criterion: null,
      selectedCriterionId: this.$route.params.id || "",
      selectedPhaseId: this.$route.query.phase || "",
      userCriteria: [],
      criterias: [],
      sessions: [],
    };
  },
  computed: {
    criterionOptions() {
      return this.criterias.map((c) => ({
        value: c.id.toString(),
        label: c.name,
      }));
    },
    phaseGroups() {
      return this.sessions.map((session) => ({
        label: session.title,
        options: session.phases.map((p) => ({
          value: p.id.toString(),
          label: p.title,
        })),
      }));
    },
  },
  watch: {
    async selectedCriterionId() {
      await this.fetchData();
    },
    async selectedPhaseId() {
      await this.fetchData();
    },
  },
  methods: {
    async fetchSessions() {
      const res = await getSessions();
      this.sessions = res.data;
    },
    async fetchCriterias() {
      const res = await getCriterias();
      this.criterias = res.data;
    },
    async fetchData() {
      if (!this.selectedCriterionId || !this.selectedPhaseId) {
        this.userCriteria = [];
        return;
      }

      const res = await getUserCriteriasForCriterion(
        this.selectedCriterionId,
        this.selectedPhaseId
      );
      this.userCriteria = res.data;
      this.criterion = this.criterias.find(
        (c) => c.id.toString() === this.selectedCriterionId
      );
    },
    async updateCount(uc, delta) {
      const newValue = (uc.count_value || 0) + delta;
      uc.count_value = Math.max(0, newValue);
      if (delta > 0)
        await incrementUserCriterion(this.selectedCriterionId, uc.user.id, this.selectedPhaseId);
      else
        await decrementUserCriterion(this.selectedCriterionId, uc.user.id, this.selectedPhaseId);
    },
    async updateBoolean(uc) {
      await setBooleanValue(
        this.selectedCriterionId,
        uc.user.id,
        this.selectedPhaseId,
        uc.is_fulfilled
      );
    },
    async updateText(uc) {
      await setTextValue(
        this.selectedCriterionId,
        uc.user.id,
        this.selectedPhaseId,
        uc.text_value || ""
      );
    },
  },
  async mounted() {
    await Promise.all([this.fetchCriterias(), this.fetchSessions()]);
    if (this.$route.query.criterion) this.selectedCriterionId = this.$route.query.criterion;
    if (this.$route.query.phase) this.selectedPhaseId = this.$route.query.phase;
    await this.fetchData();
  },
};
</script>
