<template>
  <div class="max-w-4xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-800 mb-6">
      {{ "Create Session" }}
    </h2>

    <!-- Show info if child session -->
    <div v-if="session.parent_id" class="mb-4 text-sm text-gray-600 bg-gray-50 p-3 rounded">
      This session will be created as a <strong>subsession</strong> of:
      <span class="font-semibold">{{ parentSessionTitle }}</span>
    </div>

    <form @submit.prevent="submitForm" class="space-y-6">
      <!-- Session Title -->
      <div>
        <label class="block mb-2 font-semibold">Title</label>
        <input
          v-model="session.title"
          type="text"
          class="w-full border border-gray-300 rounded-lg p-2"
          placeholder="Session Title"
          required
        />
      </div>

      <!-- Session Description -->
      <div>
        <label class="block mb-2 font-semibold">Description</label>
        <textarea
          v-model="session.description"
          class="w-full border border-gray-300 rounded-lg p-2"
          rows="4"
          placeholder="Description (optional)"
        ></textarea>
      </div>

      <!-- Criteria Selection -->
      <div>
        <h3 class="text-lg font-semibold text-gray-700 mb-4">Select Criteria & Weights per Role</h3>

        <div class="grid grid-cols-2 gap-4">
          <div
            v-for="crit in criteria"
            :key="crit.id"
            class="border rounded p-3 bg-gray-50"
          >
            <div class="flex justify-between items-center mb-2">
              <span class="font-semibold">{{ crit.name }}</span>
              <BaseToggle v-model="checkedCriteria[crit.id]" />
            </div>

            <div v-if="checkedCriteria[crit.id]" class="mt-2">
              <div class="font-semibold mb-1">Weights:</div>
              <div v-for="role in roles" :key="role.id" class="flex items-center justify-between mb-1">
                <span>{{ role.name }}:</span>
                <input
                  type="number"
                  min="1"
                  v-model.number="criteriaWeightsByRole[crit.id][role.id]"
                  class="w-16 border rounded px-1 text-center"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Buttons -->
      <div class="flex justify-between pt-4">
        <BaseButton type="button" variant="cancel" @click="$router.push('/sessions')">
          Cancel
        </BaseButton>
        <BaseButton type="submit">{{ "Create Session" }}</BaseButton>
      </div>
    </form>
  </div>
</template>

<script>
import BaseButton from "@/BaseComponents/BaseButton.vue";
import BaseToggle from "@/BaseComponents/BaseToggle.vue";
import { getCriterias } from "@/live-sessions/api/criterias";
import { getRoles } from "@/live-sessions/api/roles";
import { getSession, createSession } from "@/live-sessions/api/sessions";

export default {
  components: { BaseButton, BaseToggle },
  data() {
    return {
      session: {
        title: "",
        description: "",
        parent_id: null,
      },
      parentSessionTitle: null,
      criteria: [],
      roles: [],
      checkedCriteria: {},
      criteriaWeightsByRole: {},
    };
  },
  methods: {
    async fetchRoles() {
      const res = await getRoles();
      this.roles = res.data || [];
    },
    async fetchCriteria() {
      const res = await getCriterias();
      this.criteria = res.data || [];

      // Initialize checkedCriteria defaults
      this.checkedCriteria = Object.fromEntries(this.criteria.map(c => [c.id, true]));

      // Initialize weights for all roles
      this.criteria.forEach(c => {
        if (!this.criteriaWeightsByRole[c.id]) this.criteriaWeightsByRole[c.id] = {};
        this.roles.forEach(r => {
          if (!this.criteriaWeightsByRole[c.id][r.id]) this.criteriaWeightsByRole[c.id][r.id] = 1;
        });
      });
    },
    async applyParentCriteria(parentId) {
      if (!parentId) return;
      try {
        const res = await getSession(parentId);
        const parent = res.data;
        this.parentSessionTitle = parent?.title ?? "(unknown)";

        // Map parent's criteria: { criterionId -> { roleId: weight } }
        const parentMap = {};
        (parent?.criteria || []).forEach(c => {
          const cid = c.criterion.id;
          if (!parentMap[cid]) parentMap[cid] = {};
          parentMap[cid][c.role_id] = c.weight;
        });

        // Initialize checkedCriteria
        this.checkedCriteria = Object.fromEntries(
          this.criteria.map(c => [c.id, parentMap[c.id] !== undefined])
        );

        // Apply parent's weights
        this.criteria.forEach(c => {
          this.roles.forEach(r => {
            this.criteriaWeightsByRole[c.id][r.id] = (parentMap[c.id] && parentMap[c.id][r.id]) ?? 1;
          });
        });
      } catch (err) {
        console.warn("Failed to fetch parent session or apply criteria:", err);
      }
    },
    async submitForm() {
      try {
        const criteriaPayload = [];
        Object.entries(this.checkedCriteria)
          .filter(([, checked]) => checked)
          .forEach(([critId]) => {
            const weights = this.criteriaWeightsByRole[critId];
            Object.entries(weights).forEach(([roleId, weight]) => {
              criteriaPayload.push({
                id: Number(critId),
                role_id: Number(roleId),
                weight,
              });
            });
          });

        const payload = {
          ...this.session,
          criteria: criteriaPayload,
        };

        const res = await createSession(payload);
        const newSession = res.data;
        this.$router.push(`/sessions/edit/${newSession.id}`);
      } catch (err) {
        console.error(err);
        alert(err.response?.data?.detail || "Failed to submit session");
      }
    },
  },
  async mounted() {
    await this.fetchRoles();
    await this.fetchCriteria();

    const parentId = this.$route.query.parentId ? Number(this.$route.query.parentId) : null;

    if (parentId) {
      // Create child session
      this.session.parent_id = parentId;
      await this.applyParentCriteria(parentId);
    }
  },
};
</script>
