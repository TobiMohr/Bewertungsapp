<template>
  <div class="max-w-7xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md flex gap-6">

    <!-- Collapsible SessionTree on the left -->
    <aside
      :class="[
        'transition-all duration-300 bg-gray-50 p-4 rounded-lg border overflow-y-auto',
        isTreeCollapsed ? 'w-16' : 'w-1/4'
      ]"
    >
      <!-- Toggle Button -->
      <button
        @click="isTreeCollapsed = !isTreeCollapsed"
        class="mb-4 p-2 bg-gray-200 hover:bg-gray-300 rounded text-sm font-medium w-full flex items-center justify-center gap-1"
      >
        <ChevronLeftIcon v-if="!isTreeCollapsed" class="w-5 h-5" />
        <span v-if="!isTreeCollapsed">Collapse</span>
        <ChevronRightIcon v-else class="w-5 h-5" />
      </button>

      <!-- Tree only when expanded -->
      <div v-if="!isTreeCollapsed">
        <h3 class="text-lg font-semibold text-gray-800 mb-3">Sessions</h3>
        <SessionTree
          :items="sessions"
          :activeId="session.id"
          @select="handleSelect"
        />
      </div>
    </aside>

    <!-- Main edit form -->
    <main class="flex-1 overflow-hidden">
      <div class="flex flex-col space-y-6">

        <!-- Header with Edit & Copy buttons -->
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold text-gray-800">Edit Session</h2>
          <div class="flex items-center space-x-3">
            <BaseButton class="p-2 rounded-full" variant="edit" tooltip="Edit this Session" @click="openEditModal">
              <PencilIcon class="h-5 w-5" />
            </BaseButton>

            <BaseButton class="flex items-center" variant="copy" tooltip="Copy this Session" @click="openCopyDialog">
              <DocumentDuplicateIcon class="h-5 w-5" />
            </BaseButton>
          </div>
        </div>

        <!-- Display Session Info -->
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

        <!-- Criteria Section -->
        <div class="mt-6">
          <h3 class="text-lg font-semibold text-gray-700 mb-4">Criteria</h3>
          <p class="text-sm text-gray-500 mb-4">
            Existing criteria cannot be deselected. You can add new criteria and adjust weights.
          </p>

          <div class="flex flex-col space-y-3">
            <div
              v-for="crit in allCriteria"
              :key="crit.id"
              class="flex items-center justify-between"
            >
              <!-- Left side: name + toggle -->
              <div class="flex items-center space-x-4 w-2/4">
                <span class="text-gray-800 w-40 truncate">{{ crit.name }}</span>
                <div class="flex items-center space-x-2">
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

              <!-- Right side: weight input -->
              <div class="flex items-center space-x-2 w-2/4">
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

          <div class="flex justify-end pt-4">
            <BaseButton @click="updateCriteriaHandler">Update Criteria</BaseButton>
          </div>
        </div>

        <!-- Child Sessions Section -->
        <div class="mt-8">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-gray-800">Subsessions</h3>
            <BaseButton
              @click="$router.push({ path: '/sessions/create', query: { parentId: session.id } })"
            >
              Add Subsession
            </BaseButton>
          </div>

          <ul v-if="session.children && session.children.length" class="divide-y divide-gray-200">
            <li
              v-for="child in session.children"
              :key="child.id"
              class="py-3 cursor-pointer hover:bg-gray-50 px-2 rounded"
              @click="$router.push(`/sessions/edit/${child.id}`)"
            >
              <div class="flex items-center justify-between">
                <span class="font-medium text-gray-700 hover:underline">{{ child.title }}</span>
                <p class="text-gray-500 text-sm">{{ child.description }}</p>
              </div>
            </li>
          </ul>
          <p v-else class="text-gray-500 text-sm italic">No subsessions yet.</p>
        </div>

        <!-- Copy Session Dialog -->
        <BaseDialog v-if="showCopyDialog" @close="showCopyDialog = false">
          <template #title>Copy Session</template>

          <template #content>
            <p class="text-sm text-gray-500 mb-4">
              Enter a name for the copied session.
            </p>
            <BaseInput
              v-model="copyTitleInput"
              label="Title"
              placeholder="Enter new session title"
              class="w-full mb-4"
            />
          </template>

          <template #actions>
            <BaseButton variant="cancel" @click="showCopyDialog = false">
              Cancel
            </BaseButton>
            <BaseButton variant="primary" @click="confirmCopySession">
              Confirm
            </BaseButton>
          </template>
        </BaseDialog>

        <!-- Edit Session Modal -->
        <BaseDialog v-if="showEditModal" @close="showEditModal = false">
          <template #title>Edit Session</template>

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
            <BaseButton @click="updateSessionHandler">Update</BaseButton>
          </template>
        </BaseDialog>

      </div>
    </main>
  </div>
</template>

<script>
import { getCriterias } from "@/live-sessions/api/criterias";
import { getSessions } from "@/live-sessions/api/sessions";
import { getSession, updateSession, copySession } from "@/live-sessions/api/sessions";
import BaseButton from "@/BaseComponents/BaseButton.vue";
import BaseToggle from "@/BaseComponents/BaseToggle.vue";
import BaseDialog from "@/BaseComponents/BaseDialog.vue";
import BaseInput from "@/BaseComponents/BaseInput.vue";
import SessionTree from "../SessionTree.vue";
import { LockClosedIcon, DocumentDuplicateIcon, PencilIcon, ChevronLeftIcon, ChevronRightIcon } from "@heroicons/vue/24/solid";

export default {
  components: { BaseButton, BaseToggle, BaseDialog, BaseInput, LockClosedIcon, DocumentDuplicateIcon, PencilIcon, SessionTree, ChevronLeftIcon, ChevronRightIcon },
  data() {
    return {
      session: {},
      sessions: [],
      isTreeCollapsed: false,
      form: { title: "", description: "" },
      editForm: { title: "", description: "" },
      allCriteria: [],
      checkedCriteria: {},
      criteriaWeights: {},
      sessionCriteriaIds: [],
      showCopyDialog: false,
      copyTitleInput: "",
      showEditModal: false,
    };
  },
  methods: {
    handleSelect(item) {
      this.$router.push(`/sessions/edit/${item.id}`);
    },
    async loadSessionsTree() {
      try {
        const res = await getSessions();
        this.sessions = res.data;
      } catch (err) {
        console.error("Failed to load sessions tree", err);
      }
    },
    openCopyDialog() {
      this.copyTitleInput = `${this.form.title} (Copy)`;
      this.showCopyDialog = true;
    },
    async confirmCopySession() {
      if (!this.copyTitleInput.trim()) return;
      try {
        await copySession(this.session.id, this.copyTitleInput);
        this.showCopyDialog = false;
        this.$router.push(`/sessions/edit/${this.session.id}`);
      } catch (err) {
        console.error(err);
        alert("Failed to copy session");
      }
    },
    openEditModal() {
      this.editForm.title = this.form.title;
      this.editForm.description = this.form.description;
      this.showEditModal = true;
    },
    async updateSessionHandler() {
      try {
        await updateSession(this.session.id, {
          title: this.editForm.title,
          description: this.editForm.description,
        });
        this.form.title = this.editForm.title;
        this.form.description = this.editForm.description;
        this.showEditModal = false;
      } catch (err) {
        console.error(err);
        alert("Failed to update session");
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

        await updateSession(this.session.id, {
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
    async loadSession(sessionId) {
      try {
        const criteriaRes = await getCriterias();
        this.allCriteria = criteriaRes.data;

        this.checkedCriteria = Object.fromEntries(this.allCriteria.map(c => [String(c.id), false]));
        this.criteriaWeights = Object.fromEntries(this.allCriteria.map(c => [String(c.id), 0]));
        this.sessionCriteriaIds = [];

        const sessionRes = await getSession(sessionId);
        const s = sessionRes.data;

        this.session = s;
        this.form.title = s.title;
        this.form.description = s.description;

        if (Array.isArray(s.criteria)) {
          s.criteria.forEach(crit => {
            const cid = crit.criterion?.id;
            if (!cid) return;
            this.sessionCriteriaIds.push(cid);
            this.checkedCriteria[String(cid)] = true;
            this.criteriaWeights[String(cid)] = crit.weight ?? 0;
          });
        }
      } catch (err) {
        console.error(err);
        alert("Failed to load session");
        this.$router.push("/sessions");
      }
    },
  },
  async mounted() {
    await this.loadSessionsTree();
    await this.loadSession(Number(this.$route.params.id));
  },
  watch: {
    '$route.params.id': {
      immediate: false,
      async handler(newId) {
        await this.loadSession(Number(newId));
      },
    },
  },
};
</script>
