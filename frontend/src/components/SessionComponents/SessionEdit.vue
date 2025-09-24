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
            Existing criteria cannot be deselected. You can add new criteria.
        </p>

        <div class="flex flex-col space-y-3">
          <div v-for="crit in criteria" :key="crit.id" class="flex items-center justify-between">
            <span class="text-gray-800">{{ crit.name }}</span>
            <BaseToggle
              v-model="checkedCriteria[crit.id]"
              :disabled="sessionCriteria.includes(crit.id)"
              @update:modelValue="val => {
                console.log('Toggled criteria', crit.id, 'new value:', val);
                checkedCriteria[crit.id] = val;
              }"
            />
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
import BaseButton from "../BaseComponents/BaseButton.vue";
import BaseToggle from "../BaseComponents/BaseToggle.vue";
import { getCriterias } from "../../api/criterias";

export default {
  components: { BaseButton, BaseToggle },
  data() {
    return {
      form: {
        title: "",
        description: "",
      },
      criteria: [],           // All available criteria
      checkedCriteria: {},    // Mapping crit.id -> true/false
      sessionCriteria: [],    // IDs of criteria selected in the session
    };
  },
  watch: {
    checkedCriteria: {
      handler(newVal) {
        console.log("checkedCriteria changed:", newVal);
      },
      deep: true,
    },
  },
  methods: {
    async updateSessionHandler() {
      const id = this.$route.params.id;

      // Collect newly selected criteria (not part of original sessionCriteria)
      const newSelectedCriteria = Object.entries(this.checkedCriteria)
        .filter(([critId, value]) => value && !this.sessionCriteria.includes(Number(critId)))
        .map(([critId]) => Number(critId));

      // Merge with existing session criteria
      const mergedCriteriaIds = [...this.sessionCriteria, ...newSelectedCriteria];

      console.log("Updating session with criteria IDs:", mergedCriteriaIds);

      await updateSession(id, {
        ...this.form,
        criteria: mergedCriteriaIds,
      });

      this.$router.push("/sessions");
    },
  },
  async mounted() {
    try {
      // 1️⃣ Fetch all criteria
      const criteriaRes = await getCriterias();
      this.criteria = criteriaRes.data;

      // Initialize all as false
      this.checkedCriteria = Object.fromEntries(
        this.criteria.map(c => [c.id, false])
      );

      console.log("All criteria fetched:", this.criteria);

      // 2️⃣ Fetch session data
      const sessionRes = await getSession(this.$route.params.id);
      this.form.title = sessionRes.data.title;
      this.form.description = sessionRes.data.description;

      if (sessionRes.data.criteria) {
        this.sessionCriteria = sessionRes.data.criteria.map(c => c.id);
      }

      console.log("Fetched session:", sessionRes.data);
      console.log("Session criteria IDs:", this.sessionCriteria);

      // 3️⃣ Apply session-selected criteria to checkedCriteria
      this.sessionCriteria.forEach(id => {
        if (id in this.checkedCriteria) {
          this.checkedCriteria[id] = true;
        }
      });

      console.log("Checked criteria mapping:", this.checkedCriteria);

    } catch (err) {
      console.error("Failed to fetch session or criteria:", err);
    }
  },
};
</script>
