<template>
  <div class="max-w-2xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-6">Edit Session</h2>

    <form @submit.prevent="updateSessionHandler" class="space-y-6">
      <!-- Title -->
      <div>
        <label class="block mb-2 font-semibold">Title</label>
        <input
          v-model="form.title"
          type="text"
          class="w-full border border-gray-300 rounded-lg p-2"
          required
        />
      </div>

      <!-- Description -->
      <div>
        <label class="block mb-2 font-semibold">Description</label>
        <textarea
          v-model="form.description"
          class="w-full border border-gray-300 rounded-lg p-2"
          rows="4"
        ></textarea>
      </div>

      <!-- Criteria selection -->
      <div>
        <h3 class="text-lg font-semibold text-gray-700 mb-4">
          Select Criteria
        </h3>

        <p class="text-sm text-gray-500 mb-4">
          Existing criteria cannot be deselected. You can add new criteria and adjust weights.
        </p>

        <div class="flex flex-col space-y-3">
          <div
            v-for="crit in criteria"
            :key="crit.id"
            class="flex items-center justify-between space-x-4"
          >
            <!-- Left column: Name + Toggle + Lock -->
            <div class="flex items-center space-x-2 w-3/4">
              <span class="text-gray-800 w-40 truncate">{{ crit.name }}</span>
              
              <div class="flex items-center space-x-1">
                <BaseToggle
                  v-model="checkedCriteria[String(crit.id)]"
                  :disabled="sessionCriteriaIds.includes(crit.id)"
                />
                <LockClosedIcon
                  v-if="sessionCriteriaIds.includes(crit.id)"
                  class="h-4 w-4 text-gray-400"
                />
              </div>
            </div>

            <!-- Right column: Weight Input -->
            <div class="flex items-center space-x-2 w-1/4 justify-end">
              <label
                v-if="checkedCriteria[String(crit.id)]"
                class="text-sm text-gray-600"
              >
                Weight
              </label>
              <input
                v-if="checkedCriteria[String(crit.id)]"
                type="number"
                min="0"
                v-model.number="criteriaWeights[String(crit.id)]"
                class="w-16 border border-gray-300 rounded px-1 py-1 text-center"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Buttons -->
      <div class="flex justify-between pt-4">
        <BaseButton
          type="button"
          class="bg-gray-400 hover:bg-gray-500"
          @click="$router.push('/sessions')"
        >
          Cancel
        </BaseButton>
        <BaseButton type="submit" class="bg-blue-500 hover:bg-blue-600">
          Update Session
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<script>
import { getSession, updateSession } from "../../api/sessions";
import { getCriterias } from "../../api/criterias";
import BaseButton from "../BaseComponents/BaseButton.vue";
import BaseToggle from "../BaseComponents/BaseToggle.vue";
import { LockClosedIcon } from '@heroicons/vue/24/solid';

export default {
  components: { BaseButton, BaseToggle, LockClosedIcon },
  data() {
    return {
      form: {
        title: "",
        description: "",
      },
      criteria: [],               // All available criteria from /criterias
      checkedCriteria: {},        // Mapping string(id) -> boolean
      criteriaWeights: {},        // Mapping string(id) -> number (0 allowed)
      sessionCriteriaIds: [],     // IDs of criteria that already belong to the session
    };
  },
  methods: {
    async updateSessionHandler() {
      const id = this.$route.params.id;

      const payloadCriteria = Object.entries(this.checkedCriteria)
        .filter(([, checked]) => checked)
        .map(([idStr]) => {
          const weight = this.criteriaWeights[idStr] ?? 0;
          return { id: Number(idStr), weight };
        });

      try {
        await updateSession(id, {
          ...this.form,
          criteria: payloadCriteria,
        });
        this.$router.push("/sessions");
      } catch (err) {
        console.error("Failed to update session:", err);
        alert(err.response?.data?.detail || "Failed to update session");
      }
    },
  },
  async mounted() {
    try {
      // 1) fetch all available criteria
      const criteriaRes = await getCriterias();
      this.criteria = criteriaRes.data;

      // init maps with defaults (keys as strings for v-model)
      this.checkedCriteria = Object.fromEntries(this.criteria.map(c => [String(c.id), false]));
      this.criteriaWeights = Object.fromEntries(this.criteria.map(c => [String(c.id), 0]));

      // 2) fetch session
      const sessionRes = await getSession(this.$route.params.id);
      const s = sessionRes.data;
      this.form.title = s.title;
      this.form.description = s.description;

      // backend returns session_criteria_assoc: [{ criterion: {...}, weight: N }, ...]
      if (Array.isArray(s.session_criteria_assoc)) {
        s.session_criteria_assoc.forEach((assoc) => {
          const cid = assoc.criterion.id;
          this.sessionCriteriaIds.push(cid);
          this.checkedCriteria[String(cid)] = true;
          this.criteriaWeights[String(cid)] = assoc.weight ?? 0;
        });
      }

      // defensive: ensure all session criteria are initialized
      this.sessionCriteriaIds.forEach(cid => {
        if (!(String(cid) in this.checkedCriteria)) {
          this.$set(this.checkedCriteria, String(cid), true);
        }
        if (!(String(cid) in this.criteriaWeights)) {
          this.$set(this.criteriaWeights, String(cid), 0);
        }
      });
    } catch (err) {
      console.error("Failed to fetch session or criteria:", err);
      alert("Failed to load session data");
    }
  },
};
</script>
