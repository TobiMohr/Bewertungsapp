<template>
  <div class="max-w-2xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-6">Edit Phase</h2>

    <form @submit.prevent="updatePhaseHandler" class="space-y-6">
      <!-- Phase Info -->
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
        <h3 class="text-lg font-semibold text-gray-700 mb-4">Criteria</h3>
        <p class="text-sm text-gray-500 mb-4">
          Existing criteria cannot be deselected. You can add new criteria and adjust weights.
        </p>

        <div class="flex flex-col space-y-3">
          <div
            v-for="crit in allCriteria"
            :key="crit.id"
            class="flex items-center justify-between space-x-4"
          >
            <!-- Left: Name + Toggle + Lock -->
            <div class="flex items-center space-x-2 w-3/4">
              <span class="text-gray-800 w-40 truncate">{{ crit.name }}</span>
              <div class="flex items-center space-x-1">
                <BaseToggle
                  v-model="checkedCriteria[String(crit.id)]"
                  :disabled="phaseCriteriaIds.includes(crit.id)"
                />
                <LockClosedIcon
                  v-if="phaseCriteriaIds.includes(crit.id)"
                  class="h-4 w-4 text-gray-400"
                />
              </div>
            </div>

            <!-- Right: Weight Input -->
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
        <BaseButton type="button" variant="cancel" @click="$router.push('/sessions')">
          Cancel
        </BaseButton>
        <BaseButton type="submit">
          Update Phase
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<script>
import { getCriterias } from "@/api/criterias";
import { getPhase, updatePhase } from "@/api/phases";
import BaseButton from "../BaseComponents/BaseButton.vue";
import BaseToggle from "../BaseComponents/BaseToggle.vue";
import { LockClosedIcon } from "@heroicons/vue/24/solid";

export default {
  components: { BaseButton, BaseToggle, LockClosedIcon },
  data() {
    return {
      phase: {
        id: null,
        title: "",
        description: "",
        criteria: [],
      },
      form: {
        title: "",
        description: "",
      },
      allCriteria: [],
      checkedCriteria: {},
      criteriaWeights: {},
      phaseCriteriaIds: [], // IDs of criteria already in phase
    };
  },
  methods: {
    async updatePhaseHandler() {
      const phaseId = this.phase.id;

      const payloadCriteria = Object.entries(this.checkedCriteria)
        .filter(([, checked]) => checked)
        .map(([idStr]) => ({
          id: Number(idStr),
          weight: this.criteriaWeights[idStr] ?? 0,
        }));

      try {
        await updatePhase(phaseId, {
          title: this.form.title,
          description: this.form.description,
          criteria: payloadCriteria,
        });
        this.$router.push("/sessions");
      } catch (err) {
        console.error("Failed to update phase:", err);
        alert(err.response?.data?.detail || "Failed to update phase");
      }
    },
  },
  async mounted() {
    try {
      const phaseId = Number(this.$route.params.id);

      // 1) fetch all criteria
      const criteriaRes = await getCriterias();
      this.allCriteria = criteriaRes.data;

      // init maps
      this.checkedCriteria = Object.fromEntries(this.allCriteria.map(c => [String(c.id), false]));
      this.criteriaWeights = Object.fromEntries(this.allCriteria.map(c => [String(c.id), 0]));

      // 2) fetch phase
      const phaseRes = await getPhase(phaseId);
      const p = phaseRes.data;

      this.phase = p;
      this.form.title = p.title;
      this.form.description = p.description;

      if (Array.isArray(p.criteria)) {
        p.criteria.forEach(c => {
          const cid = c.criterion?.id;
          if (!cid) return;

          this.phaseCriteriaIds.push(cid);
          this.checkedCriteria[String(cid)] = true;
          this.criteriaWeights[String(cid)] = c.weight ?? 0;
        });
      }
    } catch (err) {
      console.error("Failed to fetch phase or criteria:", err);
      alert("Failed to load phase data");
      this.$router.push("/sessions");
    }
  },
};
</script>
