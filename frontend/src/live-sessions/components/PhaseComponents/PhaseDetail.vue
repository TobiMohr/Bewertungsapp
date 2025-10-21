<template>
  <div class="max-w-2xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <!-- Header with Edit & Copy buttons -->
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Edit Phase</h2>

      <div class="flex items-center space-x-3">
        <!-- Edit Phase Button -->
        <BaseButton
          class="p-2 rounded-full"
          variant="edit"
          tooltip="Edit this Phase"
          @click="openEditModal"
        >
          <PencilIcon class="h-5 w-5" />
        </BaseButton>

        <!-- Copy Phase Button -->
        <BaseButton
          class="flex items-center"
          variant="copy"
          tooltip="Copy this phase"
          @click="openCopyDialog"
        >
          <DocumentDuplicateIcon class="h-5 w-5" />
        </BaseButton>
      </div>
    </div>

    <!-- Display Phase Info -->
    <div class="space-y-4">
      <div>
        <label class="block font-bold text-gray-600">Title:</label>
        <p class="text-gray-800">{{ form.title }}</p>
      </div>
      <div>
        <label class="block font-bold text-gray-600">Description:</label>
        <p class="text-gray-800">{{ form.description || "—" }}</p>
      </div>
    </div>

    <!-- Criteria section -->
    <div class="mt-6">
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

          <div class="flex items-center space-x-2 w-1/4 justify-end">
            <label v-if="checkedCriteria[String(crit.id)]" class="text-sm text-gray-600">
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

      <!-- Update Criteria Button -->
      <div class="flex justify-end pt-4">
        <BaseButton @click="updateCriteriaHandler">Update Criteria</BaseButton>
      </div>
    </div>

    <!-- Child Phases Section -->
    <div class="mt-8">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-800">Sub-Phases</h3>
        <BaseButton
          @click="$router.push({ path: '/phases/create', query: { sessionId: phase.session_id, parentId: phase.id } })"
        >
          Add Sub-Phase
        </BaseButton>
      </div>

      <ul v-if="phase.children && phase.children.length" class="divide-y divide-gray-200">
        <li
          v-for="child in phase.children"
          :key="child.id"
          class="py-3 cursor-pointer hover:bg-gray-50 px-2 rounded"
          @click="$router.push(`/phases/${child.id}`)"
        >
          <div class="flex items-center justify-between">
            <span class="font-medium text-gray-700 hover:underline">{{ child.title }}</span>
            <p class="text-gray-500 text-sm">{{ child.description }}</p>
          </div>
        </li>
      </ul>
      <p v-else class="text-gray-500 text-sm italic">No sub-phases yet.</p>
    </div>

    <!-- Copy Phase Dialog -->
    <BaseDialog v-if="showCopyDialog" @close="showCopyDialog = false">
      <template #title>Copy Phase</template>

      <template #content>
        <p class="text-sm text-gray-500 mb-4">
          Enter a name for the copied phase. You can adjust the title if needed.
        </p>
        <BaseInput
          v-model="copyTitleInput"
          label="Title"
          placeholder="Enter new phase title"
          class="w-full mb-4"
        />
      </template>

      <template #actions>
        <BaseButton variant="cancel" @click="showCopyDialog = false">
          Cancel
        </BaseButton>
        <BaseButton variant="primary" @click="confirmCopyPhase">
          Confirm
        </BaseButton>
      </template>
    </BaseDialog>

    <!-- Edit Phase Modal -->
    <BaseDialog v-if="showEditModal" @close="showEditModal = false">
      <template #title>Edit Phase</template>

      <template #content>
        <div class="space-y-4">
          <div>
            <label class="block mb-1 font-semibold">Title</label>
            <input
              v-model="editForm.title"
              type="text"
              class="w-full border border-gray-300 rounded-lg p-2"
              required
            />
          </div>

          <div>
            <label class="block mb-1 font-semibold">Description</label>
            <textarea
              v-model="editForm.description"
              class="w-full border border-gray-300 rounded-lg p-2"
              rows="4"
            ></textarea>
          </div>
        </div>
      </template>

      <template #actions>
        <BaseButton variant="cancel" @click="showEditModal = false">Cancel</BaseButton>
        <BaseButton @click="updatePhaseHandler">Update</BaseButton>
      </template>
    </BaseDialog>
  </div>
</template>

<script>
import { getCriterias } from "@/live-sessions/api/criterias";
import { getPhase, updatePhase, copyPhase } from "@/live-sessions/api/phases";
import BaseButton from "@/BaseComponents/BaseButton.vue";
import BaseToggle from "@/BaseComponents/BaseToggle.vue";
import BaseDialog from "@/BaseComponents/BaseDialog.vue";
import BaseInput from "@/BaseComponents/BaseInput.vue";
import { LockClosedIcon, DocumentDuplicateIcon, PencilIcon } from "@heroicons/vue/24/solid";

export default {
  components: {
    BaseButton,
    BaseToggle,
    BaseDialog,
    BaseInput,
    LockClosedIcon,
    DocumentDuplicateIcon,
    PencilIcon,
  },
  data() {
    return {
      phase: {},
      form: { title: "", description: "" },
      editForm: { title: "", description: "" },
      allCriteria: [],
      checkedCriteria: {},
      criteriaWeights: {},
      phaseCriteriaIds: [],
      showCopyDialog: false,
      copyTitleInput: "",
      showEditModal: false,
    };
  },
  methods: {
    openCopyDialog() {
      this.copyTitleInput = `${this.form.title} (Copy)`;
      this.showCopyDialog = true;
    },

    async confirmCopyPhase() {
      if (!this.copyTitleInput.trim()) return;
      try {
        await copyPhase(this.phase.id, { title: this.copyTitleInput });
        this.showCopyDialog = false;
        this.$router.push(`/sessions/edit/${this.phase.session_id}`);
      } catch (err) {
        console.error(err);
        alert("Failed to copy phase");
      }
    },

    openEditModal() {
      this.editForm.title = this.form.title;
      this.editForm.description = this.form.description;
      this.showEditModal = true;
    },

    async updatePhaseHandler() {
      try {
        await updatePhase(this.phase.id, {
          title: this.editForm.title,
          description: this.editForm.description,
        });
        this.form.title = this.editForm.title;
        this.form.description = this.editForm.description;
        this.showEditModal = false;
      } catch (err) {
        console.error(err);
        alert("Failed to update phase");
      }
    },

    async updateCriteriaHandler() {
      try {
        const payloadCriteria = Object.entries(this.checkedCriteria)
          .filter(([, checked]) => checked)
          .map(([id]) => ({
            id: Number(id),
            weight: this.criteriaWeights[id] ?? 0,
          }));

        await updatePhase(this.phase.id, {
          title: this.form.title,
          description: this.form.description,
          criteria: payloadCriteria,
        });

        window.location.reload();
      } catch (err) {
        console.error(err);
        alert("Failed to update criteria");
      }
    },

    async loadPhase(phaseId) {
      try {
        const criteriaRes = await getCriterias();
        this.allCriteria = criteriaRes.data;

        this.checkedCriteria = Object.fromEntries(this.allCriteria.map(c => [String(c.id), false]));
        this.criteriaWeights = Object.fromEntries(this.allCriteria.map(c => [String(c.id), 0]));
        this.phaseCriteriaIds = [];

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
        console.error(err);
        alert("Failed to load phase");
        this.$router.push("/sessions");
      }
    },
  },

  async mounted() {
    await this.loadPhase(Number(this.$route.params.id));
  },

  watch: {
    '$route.params.id': {
      immediate: false,
      async handler(newId) {
        await this.loadPhase(Number(newId));
      },
    },
  },
};
</script>
