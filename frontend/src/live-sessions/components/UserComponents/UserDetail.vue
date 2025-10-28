<template>
  <div class="max-w-7xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">

    <!-- Header with session, user, and role -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-4">
        <h2 class="text-2xl font-bold text-gray-800 mb-2">
          {{ session?.title }} from {{ user?.first_name }} {{ user?.last_name }}
        </h2>

        <!-- Current role display -->
        <span v-if="currentRole" class="px-2 py-1 bg-indigo-100 text-indigo-800 rounded font-semibold text-sm">
          {{ currentRole.name }}
        </span>
      </div>

      <div class="flex items-center space-x-2">
        <!-- Switch to Criterion View -->
        <BaseButton
          variant="switch"
          @click="$router.push({ path: `/criterias/1/users`, query: { session: selectedSessionId } })"
          tooltip="Switch to Criterion View"
        >
          <ArrowsRightLeftIcon class="h-5 w-5" />
        </BaseButton>

        <!-- Change Role Button -->
        <BaseButton
          variant="edit"
          @click="showRoleModal = true"
          tooltip="Change Role"
        >
          Change Role
        </BaseButton>
      </div>
    </div>

    <!-- Session & User Selection -->
    <div class="mb-6 flex flex-col md:flex-row md:items-end md:space-x-6">
      <!-- Session Select -->
      <div class="w-full md:w-1/4">
        <label class="block mb-2 font-semibold">Select Session:</label>
        <BaseSelect
          v-model="selectedSessionId"
          :options="flattenedSessions"
          placeholder="-- Select Session --"
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

    <!-- If user has no role -->
    <div v-if="!currentRole" class="text-center p-6 bg-gray-100 rounded-lg">
      <p class="text-gray-500 mb-4">This user has no role yet for {{ session?.title }}.</p>
      <BaseButton @click="showRoleModal = true">Assign Role</BaseButton>
    </div>

    <!-- Criteria grid only if user has a role -->
    <div v-else-if="criteria.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
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
            :title="c.active_text ? 'Edit Text' : 'Add Text'"
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

    <!-- No criteria at all but user has a role -->
    <p v-else class="text-gray-500 mt-4 text-center">
      No criteria assigned to this user.
    </p>

    <h3 class="text-xl font-semibold text-gray-700 mt-6 mb-4">Comments</h3>

    <div v-if="currentRole" class="space-y-3">
      <!-- Add new comment -->
      <div class="relative">
        <textarea
              v-model="newCommentText"
              @input="filterCommentHistory"
              @focus="onCommentFocus"
              @blur="hideCommentDropdown"
              @keydown.down.prevent="navigateCommentSuggestions('down')"
              @keydown.up.prevent="navigateCommentSuggestions('up')"
              @keydown.enter.prevent="confirmCommentSuggestion"
              class="w-full border rounded-md p-2"
              rows="3"
              placeholder="Write a comment..."
            ></textarea>
        <ul v-if="isCommentActive && commentSuggestions.length"
            class="absolute z-10 w-full bg-white border rounded-md mt-1 max-h-40 overflow-y-auto">
          <!-- Header -->
          <li class="bg-indigo-50 text-indigo-700 text-xs font-semibold uppercase px-3 py-1 border-b border-indigo-100">
            Suggestions
          </li>
          <li
            v-for="(item, index) in commentSuggestions"
            :key="index"
            @mousedown.prevent="selectCommentSuggestion(item)"
            :class="[
              'p-2 text-sm cursor-pointer transition-colors duration-100',
              index === commentHighlightIndex
                ? 'bg-indigo-100 text-indigo-800 font-medium'
                : 'hover:bg-indigo-50 text-gray-700'
            ]"
          >
            {{ item }}
          </li>
        </ul>
        <BaseButton @click="addComment">Add</BaseButton>
      </div>

      <!-- Comments list -->
      <div v-if="comments.length" class="space-y-2">
        <BaseCommentComponent
          v-for="c in comments"
          :key="c.id"
          :comment="c"
        />
      </div>

      <p v-else class="text-gray-500 text-center">No comments yet.</p>
    </div>

    <!-- Text Modal -->
    <transition name="fade">
      <div
        v-if="showTextModal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      >
        <div class="bg-white rounded-xl shadow-lg max-w-md w-full p-6">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">
            Text for {{ activeCriterion?.criterion.name }}
          </h3>

          <div class="relative">
            <textarea
              v-model="textDraft"
              @input="filterHistory"
              @focus="() => (isTextareaActive = true)"
              @blur="hideDropdown"
              @keydown.down.prevent="navigateTextHistory('down')"
              @keydown.up.prevent="navigateTextHistory('up')"
              @keydown.enter.prevent="confirmTextHistory"
              class="w-full border rounded-md p-2"
              rows="3"
              placeholder="Write text..."
            ></textarea>

            <ul
              v-if="isTextareaActive && filteredHistory.length"
              class="absolute z-10 w-full bg-white border rounded-md mt-1 max-h-40 overflow-y-auto"
            >
              <li
                v-for="(item, index) in filteredHistory"
                :key="index"
                @mousedown.prevent="selectHistory(item)"
                :class="[
                  'p-2 cursor-pointer',
                  index === textHighlightIndex ? 'bg-indigo-100' : 'hover:bg-gray-100'
                ]"
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

    <!-- Role Modal -->
    <transition name="fade">
      <div
        v-if="showRoleModal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      >
        <div class="bg-white rounded-xl shadow-lg max-w-sm w-full p-6">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">
            Change Role for {{ user?.first_name }} {{ user?.last_name }}
          </h3>

          <BaseSelect
            v-model="selectedRoleInModal"
            :options="roles.map(r => ({ value: r.id.toString(), label: r.name }))"
            placeholder="-- Select Role --"
            :showPlaceholder="true"
          />

          <div class="flex justify-between mt-6">
            <BaseButton variant="cancel" @click="showRoleModal = false">Cancel</BaseButton>
            <BaseButton @click="saveRole">Save</BaseButton>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script>
import BaseButton from "@/BaseComponents/BaseButton.vue";
import BaseSelect from "@/BaseComponents/BaseSelect.vue";
import BaseCommentComponent from "@/BaseComponents/BaseCommentComponent.vue";
import { getUsers, getUser } from "@/live-sessions/api/users";
import { getSessions, getSession } from "@/live-sessions/api/sessions";
import {
  getUserCriterias,
  incrementUserCriterion,
  decrementUserCriterion,
  setBooleanValue,
  setTextValue,
} from "@/live-sessions/api/criterias";
import {
  getRoles,
  assignRoleToUserInSession,
  getUserRoleForSession
} from "@/live-sessions/api/roles";
import { getCommentsForUserInSession, addCommentForUserInSession } from "@/live-sessions/api/comments";
import { DocumentTextIcon, PlusIcon, MinusIcon, ArrowsRightLeftIcon } from "@heroicons/vue/24/solid";

export default {
  components: { BaseCommentComponent, BaseButton, BaseSelect, DocumentTextIcon, PlusIcon, MinusIcon, ArrowsRightLeftIcon },
  data() {
    return {
      sessions: [],
      selectedSessionId: "",
      users: [],
      user: null,
      selectedUserId: "",
      criteria: [],
      showTextModal: false,
      activeCriterion: null,
      textDraft: "",
      filteredHistory: [],
      isTextareaActive: false,
      session: null,
      roles: [],
      currentRole: null,
      showRoleModal: false,
      selectedRoleInModal: "",
      comments: [],
      newCommentText: "",
      commentSuggestions: [],
      isCommentActive: false,
      commentHighlightIndex: -1,
      textHighlightIndex: -1,
    };
  },
  computed: {
    flattenedSessions() {
      const flatten = (sessions, depth = 0) => {
        return sessions.flatMap(s => [
          { value: s.id.toString(), label: `${'— '.repeat(depth)}${s.title}` },
          ...(s.children?.length ? flatten(s.children, depth + 1) : []),
        ]);
      };
      return flatten(this.sessions);
    },
    userOptions() {
      return this.users.map(u => ({ value: u.id.toString(), label: `${u.first_name} ${u.last_name}` }));
    },
  },
  watch: {
    selectedUserId(newVal) {
      if (!newVal || !this.selectedSessionId) return;
      this.$router.replace({ params: { id: newVal }, query: { session: this.selectedSessionId } });
      this.fetchData(newVal, this.selectedSessionId);
      this.fetchUserRole(newVal, this.selectedSessionId);
      this.fetchComments();
    },
    selectedSessionId(newVal) {
      if (!newVal || !this.selectedUserId) return;
      this.$router.replace({ params: { id: this.selectedUserId }, query: { session: newVal } });
      this.fetchData(this.selectedUserId, newVal);
      this.fetchUserRole(this.selectedUserId, newVal);
      this.fetchComments();
    },
  },
  methods: {
    async fetchSessions() {
      const res = await getSessions();
      this.sessions = res.data;
      const routeSessionId = this.$route.query.session;
      if (routeSessionId) this.selectedSessionId = routeSessionId.toString();
    },
    async fetchUsers() {
      const res = await getUsers();
      this.users = res.data;
      const routeUserId = this.$route.params.id;
      if (!this.selectedUserId && routeUserId)
        this.selectedUserId = routeUserId.toString();
    },
    async fetchRoles() {
      const res = await getRoles();
      this.roles = res.data;
    },
    async fetchComments() {
      if (!this.selectedUserId || !this.selectedSessionId) return;
      const res = await getCommentsForUserInSession(this.selectedUserId, this.selectedSessionId);
      this.comments = res.data;
    },
    async fetchUserRole(userId, sessionId) {
      if (!userId || !sessionId) return;
      try {
        const res = await getUserRoleForSession(userId, sessionId);
        const roleId = res.data.role_id;
        this.currentRole = this.roles.find(r => r.id === roleId) || null;
        this.selectedRoleInModal = roleId?.toString() || "";
      } catch (err) {
        this.currentRole = null;
        this.selectedRoleInModal = "";
      }
    },
    async saveRole() {
      if (!this.selectedRoleInModal) return;
      await assignRoleToUserInSession(this.selectedUserId, this.selectedSessionId, this.selectedRoleInModal);
      await this.fetchUserRole(this.selectedUserId, this.selectedSessionId);
      this.showRoleModal = false;
    },
    async addComment() {
      if (!this.newCommentText.trim()) return;
      await addCommentForUserInSession(
        this.selectedUserId,
        this.selectedSessionId,
        this.newCommentText
      );
      this.newCommentText = "";
      this.commentHighlightIndex = -1;
      await this.fetchComments();
    },
    filterHistory() {
      if (!this.activeCriterion || !this.activeCriterion.last_texts) {
        this.filteredHistory = [];
        this.textHighlightIndex = -1;
        return;
      }
      const search = this.textDraft.toLowerCase();
      this.filteredHistory = this.activeCriterion.last_texts.filter(
        t => t && t.toLowerCase().includes(search)
      );
      this.textHighlightIndex = -1;
    },
    hideDropdown() { setTimeout(() => (this.isTextareaActive = false), 100); },
    hideCommentDropdown() { setTimeout(() => (this.isCommentActive = false), 100); },
    onCommentFocus() {
      if (!this.comments.length) {
        this.commentSuggestions = [];
        return;
      }
      this.commentSuggestions = [...new Set(this.comments.map(c => c.text))];
      this.isCommentActive = true;
      this.commentHighlightIndex = -1;
    },
    selectHistory(item) { this.textDraft = item; this.filteredHistory = []; },
    async fetchData(userIdOverride, sessionIdOverride) {
      const userId = userIdOverride || this.selectedUserId;
      const sessionId = sessionIdOverride || this.selectedSessionId;
      if (!sessionId || !userId) return;

      const [userRes, critRes, sessionRes] = await Promise.all([
        getUser(userId),
        getUserCriterias(userId, sessionId),
        getSession(sessionId),
      ]);

      this.user = userRes.data;
      this.session = sessionRes.data;
      this.criteria = critRes.data.sort((a, b) =>
        a.criterion.name.localeCompare(b.criterion.name, "en", { sensitivity: "base" })
      );
    },
    async increment(id) {
      const crit = this.criteria.find(c => c.criterion_id === id);
      if (crit) crit.count_value = (crit.count_value || 0) + 1;
      await incrementUserCriterion(id, this.selectedUserId, this.selectedSessionId);
    },
    async decrement(id) {
      const crit = this.criteria.find(c => c.criterion_id === id);
      if (crit) crit.count_value = Math.max((crit.count_value || 0) - 1, 0);
      await decrementUserCriterion(id, this.selectedUserId, this.selectedSessionId);
    },
    async toggleBoolean(id, value) {
      await setBooleanValue(id, this.selectedUserId, this.selectedSessionId, !!value);
    },
    openTextModal(c) {
      this.activeCriterion = c;
      this.textDraft = c.active_text || "";
      this.showTextModal = true;
      this.textHighlightIndex = -1;
      this.filterHistory();
    },
    cancelText() {
      this.showTextModal = false;
      this.activeCriterion = null;
      this.textDraft = "";
      this.filteredHistory = [];
    },
    navigateTextHistory(direction) {
      if (!this.filteredHistory.length) return;

      if (direction === 'down') {
        this.textHighlightIndex =
          (this.textHighlightIndex + 1) % this.filteredHistory.length;
      } else if (direction === 'up') {
        this.textHighlightIndex =
          (this.textHighlightIndex - 1 + this.filteredHistory.length) %
          this.filteredHistory.length;
      }
    },

    confirmTextHistory() {
      if (
        this.textHighlightIndex >= 0 &&
        this.textHighlightIndex < this.filteredHistory.length
      ) {
        const selected = this.filteredHistory[this.textHighlightIndex];
        this.selectHistory(selected);
      } else {
        // Optional: close dropdown on enter when nothing highlighted
        this.isTextareaActive = false;
      }
    },
    async saveText() {
      if (!this.activeCriterion) return;
      await setTextValue(
        this.activeCriterion.criterion_id,
        this.selectedUserId,
        this.selectedSessionId,
        this.textDraft
      );
      const updated = await getUserCriterias(this.selectedUserId, this.selectedSessionId);
      this.criteria = updated.data.sort((a, b) =>
        a.criterion.name.localeCompare(b.criterion.name, "en", { sensitivity: "base" })
      );
      this.cancelText();
    },
    navigateCommentSuggestions(direction) {
      if (!this.commentSuggestions.length) return;

      if (direction === 'down') {
        this.commentHighlightIndex =
          (this.commentHighlightIndex + 1) % this.commentSuggestions.length;
      } else if (direction === 'up') {
        this.commentHighlightIndex =
          (this.commentHighlightIndex - 1 + this.commentSuggestions.length) %
          this.commentSuggestions.length;
      }
    },

    confirmCommentSuggestion() {
      if (
        this.commentHighlightIndex >= 0 &&
        this.commentHighlightIndex < this.commentSuggestions.length
      ) {
        const selected = this.commentSuggestions[this.commentHighlightIndex];
        this.selectCommentSuggestion(selected);
      } else {
        this.addComment();
      }
      this.commentHighlightIndex = -1;
    },
    filterCommentHistory() {
      if (!this.comments.length) {
        this.commentSuggestions = [];
        this.commentHighlightIndex = -1;
        return;
      }
      const search = this.newCommentText.toLowerCase();
      this.commentSuggestions = [...new Set(this.comments.map(c => c.text))]
        .filter(t => t.toLowerCase().includes(search));
      this.commentHighlightIndex = -1;
    },
    selectCommentSuggestion(item) {
      this.newCommentText = item;
      this.commentSuggestions = [];
    },
  },
  async mounted() {
    await Promise.all([this.fetchSessions(), this.fetchUsers(), this.fetchRoles()]);
    await this.fetchData();
    await this.fetchUserRole(this.selectedUserId, this.selectedSessionId);
    await this.fetchComments();
  },
};
</script>
