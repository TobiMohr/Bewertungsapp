<template>
  <div class="max-w-7xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold text-gray-800">Async Sessions</h2>

      <div class="flex items-center gap-2">
        <!-- Export alle -->
        <BaseButton variant="copy" @click="exportAll" :disabled="loading || !sessions.length">
          Export alle (CSV)
        </BaseButton>

        <router-link to="/async/create">
          <BaseButton class="bg-green-500 hover:bg-green-600">New</BaseButton>
        </router-link>
      </div>
    </div>

    <!-- Filterleiste -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
      <!-- Status -->
      <label class="block">
        <span class="block text-sm font-semibold text-gray-700 mb-1">Status</span>
        <select v-model="filters.status" class="w-full border border-gray-300 rounded-lg p-2">
          <option value="">All</option>
          <option value="PENDING">PENDING</option>
          <option value="RUNNING">RUNNING</option>
          <option value="DONE">DONE</option>
          <option value="FAILED">FAILED</option>
          <option value="APPROVED">APPROVED</option>
        </select>
      </label>

      <!-- Phase -->
      <label class="block">
        <span class="block text-sm font-semibold text-gray-700 mb-1">Phase</span>
        <select v-model="filters.phase" class="w-full border border-gray-300 rounded-lg p-2">
          <option value="">All</option>
          <option v-for="p in phaseOptions" :key="p" :value="p">{{ p }}</option>
        </select>
      </label>

      <!-- Approved -->
      <label class="block">
        <span class="block text-sm font-semibold text-gray-700 mb-1">Approved</span>
        <select v-model="filters.approved" class="w-full border border-gray-300 rounded-lg p-2">
          <option value="">All</option>
          <option value="true">Yes</option>
          <option value="false">No</option>
        </select>
      </label>
    </div>

    <!-- Loading / Empty / List -->
    <div v-if="loading" class="py-6 text-center text-gray-500">Loading…</div>

    <p v-else-if="!filteredSessions.length" class="text-gray-500 mt-4 text-center">
      No async sessions found.
    </p>

    <ul v-else class="divide-y divide-gray-200">
      <li
          v-for="s in filteredSessions"
          :key="s.id"
          class="py-4 flex items-center justify-between"
      >
        <div>
          <!-- Titel / Channel -->
          <p
              class="text-lg font-medium text-gray-900 cursor-pointer hover:underline"
              @click="$router.push(`/async/sessions/${s.id}`)"
          >
            {{ s.channelName }}
          </p>

          <!-- Meta -->
          <p class="text-gray-500 text-sm flex items-center gap-2 flex-wrap">
            <span v-if="s.phase">Phase: <span class="text-gray-700 font-medium">{{ s.phase }}</span></span>

            <span>
              Status:
              <span :class="['px-2 py-0.5 rounded', badgeClass(s.status)]" class="ml-1">
                {{ s.status }}
              </span>
            </span>

            <span>
              Approved:
              <span
                  :class="[
                  'px-2 py-0.5 rounded',
                  (s.approved === true)
                    ? 'bg-green-100 text-green-700'
                    : (s.approved === false)
                    ? 'bg-yellow-100 text-yellow-700'
                    : 'bg-gray-100 text-gray-700'
                ]"
                  class="ml-1"
              >
                {{ approvedLabel(s.approved) }}
              </span>
            </span>

            <span class="text-gray-400">·</span>
            <span>{{ new Date(s.createdAt).toLocaleString() }}</span>
          </p>
        </div>

        <!-- Actions -->
        <div class="flex items-center space-x-2">
          <!-- Details -->
          <router-link :to="`/async/sessions/${s.id}`">
            <BaseButton class="p-2 rounded-full" variant="edit" tooltip="View Details">
              <PencilIcon class="h-5 w-5" />
            </BaseButton>
          </router-link>

          <!-- Feedback -->
          <router-link
              v-if="s.status === 'DONE' || s.status === 'APPROVED'"
              :to="`/async/sessions/${s.id}/feedback`"
          >
            <BaseButton class="p-2 rounded-full" variant="copy" tooltip="View Feedback">
              <DocumentTextIcon class="h-5 w-5" />
            </BaseButton>
          </router-link>

          <!-- Export CSV -->
          <BaseButton
              variant="copy"
              class="p-2 rounded-full"
              :disabled="s.status !== 'DONE' && s.status !== 'APPROVED'"
              @click="exportCsv(s.id)"
              tooltip="Export Feedback (CSV)"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none"
                 viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5m0 0l5-5m-5 5V4"/>
            </svg>
          </BaseButton>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
import { onMounted, ref, computed } from "vue";
import { getSessions, getSession, getFeedback } from "../api/asyncSessions";
import BaseButton from "@/BaseComponents/BaseButton.vue";
import { PencilIcon, DocumentTextIcon } from "@heroicons/vue/24/solid";

export default {
  components: { BaseButton, PencilIcon, DocumentTextIcon },
  setup() {
    const sessions = ref([]);
    const loading = ref(true);

    // Filtermodelle
    const filters = ref({ status: "", phase: "", approved: "" });

    // --- CSV Export Helfer ---
    const esc = (v) => {
      if (v === null || v === undefined) return '""';
      const s = String(v);
      return `"${s.replace(/"/g, '""')}"`;
    };

    function toCsv(rows, delimiter = ";") {
      const header = Object.keys(rows[0] ?? {}).map(esc).join(delimiter);
      const body = rows.map(r => Object.values(r).map(esc).join(delimiter)).join("\n");
      return header + "\n" + body;
    }

    function downloadCsv(filename, csvString) {
      const blob = new Blob(["\uFEFF" + csvString], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.style.display = "none";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }

    async function exportCsv(sessionId, delimiter = ";") {
      const [sRes, fbRes] = await Promise.all([getSession(sessionId), getFeedback(sessionId)]);
      const s = sRes.data;
      const fb = fbRes.data;
      if (!s) return alert(`Session ${sessionId} nicht gefunden.`);
      if (!fb?.criteriaBreakdown?.length) return alert(`Kein Feedback für Session ${sessionId} vorhanden.`);

      const rows = fb.criteriaBreakdown.map((c) => ({
        sessionId: s.id,
        channelName: s.channelName ?? "",
        status: s.status ?? "",
        approved: !!(s.approved || fb.approved),
        createdAt: s.createdAt ?? "",
        summaryText: fb.summaryText ?? "",
        aggregateScore: fb.aggregateScore ?? "",
        criterionId: c.criterionId ?? "",
        criterionName: c.criterionName ?? "",
        score: c.score ?? "",
      }));

      const csv = toCsv(rows, delimiter);
      const fnameSafe = String(s.channelName || `session_${s.id}`).replace(/[^\w\-#]+/g, "_");
      downloadCsv(`${fnameSafe}_${s.id}.csv`, csv);
    }

    async function exportAll(delimiter = ";") {
      const all = (await getSessions()).data || [];
      const rows = [];
      for (const s of all) {
        const fb = (await getFeedback(s.id)).data;
        if (!fb?.criteriaBreakdown?.length) continue;
        for (const c of fb.criteriaBreakdown) {
          rows.push({
            sessionId: s.id,
            channelName: s.channelName ?? "",
            status: s.status ?? "",
            approved: !!(s.approved || fb.approved),
            createdAt: s.createdAt ?? "",
            summaryText: fb.summaryText ?? "",
            aggregateScore: fb.aggregateScore ?? "",
            criterionId: c.criterionId ?? "",
            criterionName: c.criterionName ?? "",
            score: c.score ?? "",
          });
        }
      }
      if (!rows.length) return alert("Keine exportierbaren Feedbacks gefunden.");
      const csv = toCsv(rows, delimiter);
      downloadCsv(`async_sessions_all.csv`, csv);
    }

    // --- Filter/Anzeige ---
    const badgeClass = (s) =>
        ({
          PENDING: "bg-gray-100 text-gray-700",
          RUNNING: "bg-yellow-100 text-yellow-700",
          DONE: "bg-green-100 text-green-700",
          APPROVED: "bg-green-200 text-green-800",
          FAILED: "bg-red-100 text-red-700",
        }[s] || "bg-gray-100 text-gray-700");

    const approvedLabel = (val) => (val === true ? "Yes" : val === false ? "No" : "—");

    const phaseOptions = computed(() => {
      const set = new Set(
          sessions.value
              .map((s) => s.phase)
              .filter((p) => typeof p === "string" && p.trim().length > 0)
      );
      return Array.from(set).sort();
    });

    const filteredSessions = computed(() => {
      return sessions.value.filter((s) => {
        if (filters.value.status && s.status !== filters.value.status) return false;
        if (filters.value.phase && s.phase !== filters.value.phase) return false;
        if (filters.value.approved !== "") {
          const want = filters.value.approved === "true";
          if (s.approved !== want) return false;
        }
        return true;
      });
    });

    onMounted(async () => {
      const { data } = await getSessions();
      sessions.value = data;
      loading.value = false;
    });

    return {
      sessions,
      loading,
      filters,
      phaseOptions,
      filteredSessions,
      badgeClass,
      approvedLabel,
      exportCsv,
      exportAll,
    };
  },
};
</script>
