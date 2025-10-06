<template>
  <div class="max-w-2xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Edit Phase</h2>

      <!-- ✅ Copy Phase Button -->
      <BaseButton
        class="flex items-center space-x-2 bg-blue-500 hover:bg-blue-600 text-white"
        @click="openCopyDialog"
      >
        <DocumentDuplicateIcon class="h-5 w-5" />
        <span>Copy Phase</span>
      </BaseButton>
    </div>

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

    <!-- ✅ Copy Phase Modal -->
    <CopyPhaseModal
      :show="showCopyDialog"
      :defaultTitle="copyTitle"
      @confirm="confirmCopy"
      @cancel="showCopyDialog = false"
    />
  </div>
</template>

<script>
import { getCriterias } from "@/api/criterias";
import { getPhase, updatePhase, copyPhase } from "@/api/phases";
import BaseButton from "../BaseComponents/BaseButton.vue";
import BaseToggle from "../BaseComponents/BaseToggle.vue";
import CopyPhaseModal from "./PhaseCopyModal.vue";
import { LockClosedIcon, DocumentDuplicateIcon } from "@heroicons/vue/24/solid";

export default {
  components: {
    BaseButton,
    BaseToggle,
    CopyPhaseModal,
    LockClosedIcon,
    DocumentDuplicateIcon,
  },
  data() {
    return {
      phase: {
        id: null,
        title: "",
        description: "",
        session_id: null,
        criteria: [],
      },
      form: {
        title: "",
        description: "",
      },
      allCriteria: [],
      checkedCriteria: {},
      criteriaWeights: {},
      phaseCriteriaIds: [],
      showCopyDialog: false,
      copyTitle: "",
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
        this.$router.push(`/sessions/edit/${this.phase.session_id}`);
      } catch (err) {
        console.error("Failed to update phase:", err);
        alert(err.response?.data?.detail || "Failed to update phase");
      }
    },

    openCopyDialog() {
      this.copyTitle = `${this.form.title} (Copy)`;
      this.showCopyDialog = true;
    },

    async confirmCopy(newTitle) {
      try {
        await copyPhase(this.phase.id, { title: newTitle });
        this.showCopyDialog = false;
        this.$router.push(`/sessions/edit/${this.phase.session_id}`);
      } catch (err) {
        console.error("Failed to copy phase:", err);
        alert(err.response?.data?.detail || "Failed to copy phase");
      }
    },
  },
  async mounted() {
    try {
      const phaseId = Number(this.$route.params.id);

      // Fetch all criteria
      const criteriaRes = await getCriterias();
      this.allCriteria = criteriaRes.data;

      this.checkedCriteria = Object.fromEntries(this.allCriteria.map(c => [String(c.id), false]));
      this.criteriaWeights = Object.fromEntries(this.allCriteria.map(c => [String(c.id), 0]));

      // Fetch phase
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
