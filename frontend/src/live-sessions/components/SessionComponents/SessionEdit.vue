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

        <!-- Header -->
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

        <!-- Session Info -->
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
            Existing criteria cannot be deselected. You can add new criteria and adjust weights per role.
          </p>

          <div class="flex flex-col space-y-3">
            <div
              v-for="crit in allCriteria"
              :key="crit.id"
              class="flex flex-col border-b border-gray-200 pb-2"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
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
              </div>

              <!-- Role-specific weights -->
              <div class="flex flex-wrap gap-2 mt-2" v-if="checkedCriteria[String(crit.id)]">
                <div
                  v-for="role in roles"
                  :key="role.id"
                  class="flex items-center space-x-1"
                >
                  <label class="text-sm text-gray-600">{{ role.name }}:</label>
                  <input
                    type="number"
                    min="0"
                    v-model.number="criteriaRoleWeights[crit.id][role.id]"
                    class="w-16 border border-gray-300 rounded px-1 py-1 text-center"
                  />
                </div>
              </div>
            </div>
          </div>

          <div class="flex justify-end pt-4">
            <BaseButton
              @click="updateCriteriaHandler"
              :disabled="!hasCriteriaChanges"
              :variant="hasCriteriaChanges ? 'primary' : 'disabled'"
              tooltip="Add new Criteria to session or change weights"
            >
              Update Criteria
            </BaseButton>
          </div>
        </div>

        <!-- Subsessions Section -->
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
            <BaseButton variant="cancel" @click="showCopyDialog = false">Cancel</BaseButton>
            <BaseButton variant="primary" @click="confirmCopySession">Confirm</BaseButton>
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
import { getSessions, getSession, updateSession, copySession } from "@/live-sessions/api/sessions";
import { getRoles } from "@/live-sessions/api/roles";

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
      criteriaRoleWeights: {},
      sessionCriteriaIds: [],
      roles: [],
      showCopyDialog: false,
      copyTitleInput: "",
      showEditModal: false,
    };
  },
  computed: {
    hasCriteriaChanges() {
      // Compare current toggled state and weights
      const original = Object.fromEntries(this.sessionCriteriaIds.map(id => [String(id), true]));
      const toggledChanged = Object.keys(this.checkedCriteria).some(id => this.checkedCriteria[id] !== (original[id] || false));
      const weightChanged = Object.entries(this.criteriaRoleWeights).some(([cid, roleMap]) =>
        Object.entries(roleMap).some(([rid, w]) => {
          const crit = this.session.criteria?.find(c => c.criterion?.id === Number(cid) && c.role_id === Number(rid));
          return this.checkedCriteria[cid] && (w !== (crit?.weight ?? 0));
        })
      );
      return toggledChanged || weightChanged;
    }
  },
  methods: {
    handleSelect(item) { this.$router.push(`/sessions/edit/${item.id}`); },
    async loadSessionsTree() {
      try { this.sessions = (await getSessions()).data; } catch (err) { console.error(err); }
    },
    openCopyDialog() { this.copyTitleInput = `${this.form.title} (Copy)`; this.showCopyDialog = true; },
    async confirmCopySession() {
      if (!this.copyTitleInput.trim()) return;
      try { await copySession(this.session.id, this.copyTitleInput); this.showCopyDialog = false; this.$router.push(`/sessions/edit/${this.session.id}`); }
      catch (err) { console.error(err); alert("Failed to copy session"); }
    },
    openEditModal() { this.editForm.title = this.form.title; this.editForm.description = this.form.description; this.showEditModal = true; },
    async updateSessionHandler() {
      try { await updateSession(this.session.id, { title: this.editForm.title, description: this.editForm.description }); this.form.title = this.editForm.title; this.form.description = this.editForm.description; this.showEditModal = false; }
      catch (err) { console.error(err); alert("Failed to update session"); }
    },
    async updateCriteriaHandler() {
      try {
        const payloadCriteria = [];
        Object.entries(this.criteriaRoleWeights).forEach(([cid, roleMap]) => {
          Object.entries(roleMap).forEach(([rid, weight]) => {
            if (weight > 0) payloadCriteria.push({ id: Number(cid), role_id: Number(rid), weight: Number(weight) });
          });
        });
        await updateSession(this.session.id, { title: this.form.title, description: this.form.description, criteria: payloadCriteria });
        window.location.reload();
      } catch (err) { console.error(err); alert("Failed to update criteria"); }
    },
    async loadSession(sessionId) {
      try {
        const [criteriaRes, rolesRes] = await Promise.all([getCriterias(), getRoles()]);
        this.allCriteria = criteriaRes.data;
        this.roles = rolesRes.data;

        // init weights
        this.criteriaRoleWeights = {};
        this.allCriteria.forEach(c => {
          this.criteriaRoleWeights[c.id] = {};
          this.roles.forEach(r => { this.criteriaRoleWeights[c.id][r.id] = 0; });
        });

        const sessionRes = await getSession(sessionId);
        const s = sessionRes.data;
        this.session = s;
        this.form.title = s.title;
        this.form.description = s.description;
        this.checkedCriteria = Object.fromEntries(this.allCriteria.map(c => [String(c.id), false]));
        this.sessionCriteriaIds = [];

        if (Array.isArray(s.criteria)) {
          s.criteria.forEach(crit => {
            const cid = crit.criterion?.id;
            if (!cid) return;
            this.sessionCriteriaIds.push(cid);
            this.checkedCriteria[String(cid)] = true;
            const rid = crit.role_id ?? 0;
            this.criteriaRoleWeights[cid][rid] = crit.weight ?? 0;
          });
        }
      } catch (err) { console.error(err); alert("Failed to load session"); this.$router.push("/sessions"); }
    }
  },
  async mounted() { await this.loadSessionsTree(); await this.loadSession(Number(this.$route.params.id)); },
  watch: {
    '$route.params.id': { immediate: false, async handler(newId) { await this.loadSession(Number(newId)); } }
  }
};
</script>
