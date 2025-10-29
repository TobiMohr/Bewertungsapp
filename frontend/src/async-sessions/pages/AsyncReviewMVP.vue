<template>
  <div class="max-w-7xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-md">
    <!-- Header -->
    <div class="flex items-center justify-between mb-2">
      <h2 class="text-2xl font-bold text-gray-800">Async Data Review (MVP)</h2>
      <div class="flex gap-2">
        <BaseButton variant="copy" @click="exportAll" :disabled="loading || !rows.length">Export alle</BaseButton>
        <BaseButton @click="manualRefresh" :disabled="loading">
          {{ loading ? 'Loading…' : 'Neue Daten laden' }}
        </BaseButton>
      </div>
    </div>

    <!-- Info: letzter Refresh -->
    <p class="text-xs text-gray-400 mb-4" v-if="lastRefreshed">
      Zuletzt aktualisiert: {{ new Date(lastRefreshed).toLocaleString() }}
    </p>

    <!-- Tabelle -->
    <div v-if="!rows.length && !loading" class="text-center text-gray-500 py-8">Keine Daten gefunden.</div>
    <div v-else>
      <table class="w-full border border-gray-200 rounded-lg overflow-hidden">
        <thead class="bg-gray-50">
        <tr class="text-left text-sm text-gray-600">
          <th class="p-3">Session</th>
          <th class="p-3">Status</th>
          <th class="p-3">Approved</th>
          <th class="p-3">Updated</th>
          <th class="p-3 text-right">Aktionen</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="s in rows" :key="s.id" class="border-t">
          <td class="p-3">
            <div class="font-medium text-gray-900">{{ s.channelName || ('Session #' + s.id) }}</div>
            <div class="text-gray-500 text-sm">{{ s.summaryText || '—' }}</div>
          </td>
          <td class="p-3">
            <span :class="['px-2 py-0.5 rounded text-sm', badgeClass(s.status)]">{{ s.status }}</span>
          </td>
          <td class="p-3">
              <span :class="['px-2 py-0.5 rounded text-sm', s.approved ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700']">
                {{ s.approved ? 'Yes' : 'No' }}
              </span>
          </td>
          <td class="p-3 text-sm text-gray-500">
            {{ s.updatedAt ? new Date(s.updatedAt).toLocaleString() : (s.createdAt ? new Date(s.createdAt).toLocaleString() : '—') }}
          </td>
          <td class="p-3">
            <div class="flex justify-end gap-2">
              <BaseButton variant="copy" @click="exportOne(s.id)" :disabled="!hasFeedback(s)">Export</BaseButton>
              <BaseButton variant="edit" @click="toggle(s.id)">{{ isOpen(s.id) ? 'Close' : 'Open' }}</BaseButton>
            </div>
          </td>
        </tr>

        <!-- Expandierter Bereich -->
        <tr v-for="s in rows" :key="s.id + '-details'" v-show="isOpen(s.id)" class="bg-gray-50">
          <td colspan="5" class="p-0">
            <div class="p-4">
              <div class="flex items-center justify-between mb-3">
                <div class="text-sm text-gray-600">
                  <strong>Aggregate:</strong> {{ s.aggregateScore ?? '—' }}
                </div>
                <div class="flex gap-2">
                  <BaseButton variant="copy" :disabled="busy[s.id] || s.approved" @click="save(s)">
                    {{ busy[s.id] === 'save' ? 'Saving…' : 'Save' }}
                  </BaseButton>
                  <BaseButton :disabled="busy[s.id] || s.approved" @click="approve(s)">
                    {{ busy[s.id] === 'approve' ? 'Approving…' : 'Approve' }}
                  </BaseButton>
                </div>
              </div>

              <div v-if="!s._editedBreakdown?.length" class="text-gray-500 text-sm">Keine Kriterien vorhanden.</div>
              <ul v-else class="divide-y rounded-lg border border-gray-200 bg-white">
                <li
                    v-for="(c, idx) in s._editedBreakdown"
                    :key="c.criterionId || idx"
                    class="flex items-center justify-between p-3"
                >
                  <div class="text-gray-800 font-medium">{{ c.criterionName }}</div>
                  <div class="flex items-center gap-2">
                    <BaseButton variant="cancel" class="px-2" :disabled="s.approved" @click="changeScore(s, idx, -1)">−</BaseButton>
                    <span :class="['min-w-[3rem] text-center px-2 py-1 rounded', scoreClass(c.score)]">{{ c.score }}</span>
                    <BaseButton class="px-2" :disabled="s.approved" @click="changeScore(s, idx, +1)">+</BaseButton>

                    <!-- Evidenz ansehen -->
                    <BaseButton class="px-2" :disabled="!c.evidence?.length" @click="openEvidence(s, c)">Evidenz</BaseButton>
                  </div>
                </li>
              </ul>
            </div>
          </td>
        </tr>
        </tbody>
      </table>
    </div>

    <!-- Evidenz-Dialog -->
    <div v-if="evDialog.open" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-lg w-full max-w-2xl p-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-lg font-semibold text-gray-800">{{ evDialog.title }}</h3>
          <BaseButton variant="cancel" @click="closeEvidence">Schließen</BaseButton>
        </div>

        <div v-if="!evDialog.items.length" class="text-gray-500 text-sm">Keine Evidenz vorhanden.</div>
        <ul v-else class="divide-y">
          <li v-for="(e, i) in evDialog.items" :key="i" class="py-2">
            <div class="text-sm text-gray-800">
              <span class="font-medium">@{{ e.username ?? 'unknown' }}</span>
              <span class="text-gray-400"> · {{ e.sentAt ? new Date(e.sentAt).toLocaleString() : '—' }}</span>
            </div>
            <div class="text-gray-700">{{ e.content }}</div>
            <div class="text-xs text-gray-500 mt-1">
              messageId: {{ e.messageId }}
              <span v-if="e.countValue != null"> · count: {{ e.countValue }}</span>
              <span v-if="e.isFulfilled != null"> · fulfilled: {{ e.isFulfilled }}</span>
              <span v-if="e.textValue"> · text: {{ e.textValue }}</span>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import BaseButton from '@/BaseComponents/BaseButton.vue';
import { fetchReviews } from '@/api/reviews';

// --- lokaler Zustand ---
const rows = ref([]);
const open = ref(new Set());
const busy = ref({});
const loading = ref(true);
const lastRefreshed = ref(null);
const evDialog = ref({ open: false, items: [], title: '' });

// --- helpers ---
const badgeClass = (s) => ({
  PENDING:  'bg-gray-100 text-gray-700',
  RUNNING:  'bg-yellow-100 text-yellow-700',
  DONE:     'bg-green-100 text-green-700',
  APPROVED: 'bg-green-200 text-green-800',
  FAILED:   'bg-red-100 text-red-700',
}[s] || 'bg-gray-100 text-gray-700');

const scoreClass = (s) => (s >= 80 ? 'bg-green-100 text-green-700' : s >= 60 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700');
const isOpen = (id) => open.value.has(id);
const toggle = (id) => (isOpen(id) ? open.value.delete(id) : open.value.add(id));

function changeScore(session, idx, delta) {
  const list = session._editedBreakdown;
  if (!list || !list[idx]) return;
  const s = Math.max(0, Math.min(100, (list[idx].score || 0) + delta));
  list[idx].score = s;
  session._dirty = true;
}

const hasFeedback = (s) => Array.isArray(s._editedBreakdown) && s._editedBreakdown.length > 0;

// CSV Utilities
function esc(v){ if(v==null) return '""'; const s=String(v); return `"${s.replace(/"/g,'""')}"`; }
function toCsv(rows, d=';'){ const h=Object.keys(rows[0]||{}).map(esc).join(d); const b=rows.map(r=>Object.values(r).map(esc).join(d)).join('\n'); return h+'\n'+b; }
function downloadCsv(name, csv){ const blob=new Blob(["\uFEFF"+csv],{type:'text/csv;charset=utf-8;'}); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download=name; a.click(); URL.revokeObjectURL(url); }

async function exportOne(id, d=';') {
  const s = rows.value.find(x => String(x.id) === String(id));
  if (!s || !hasFeedback(s)) return;
  const csvRows = s._editedBreakdown.map(c => ({
    sessionId: s.id,
    channelName: s.channelName ?? '',
    status: s.status ?? '',
    approved: !!s.approved,
    createdAt: s.createdAt ?? '',
    summaryText: s.summaryText ?? '',
    aggregateScore: s.aggregateScore ?? '',
    criterionId: c.criterionId ?? '',
    criterionName: c.criterionName ?? '',
    score: c.score ?? '',
  }));
  const csv = toCsv(csvRows, d);
  const fname = String(s.channelName || `session_${s.id}`).replace(/[^\w\-#]+/g,'_');
  downloadCsv(`${fname}_${s.id}.csv`, csv);
}

function exportAll(d=';') {
  const all = [];
  for (const s of rows.value) {
    if (!hasFeedback(s)) continue;
    for (const c of s._editedBreakdown) {
      all.push({
        sessionId: s.id,
        channelName: s.channelName ?? '',
        status: s.status ?? '',
        approved: !!s.approved,
        createdAt: s.createdAt ?? '',
        summaryText: s.summaryText ?? '',
        aggregateScore: s.aggregateScore ?? '',
        criterionId: c.criterionId ?? '',
        criterionName: c.criterionName ?? '',
        score: c.score ?? '',
      });
    }
  }
  if (!all.length) return;
  downloadCsv(`async_review_all.csv`, toCsv(all, d));
}

// --- Datenzugriff ---
async function loadOnce() {
  loading.value = true;
  try {
    rows.value = await fetchReviews();
    lastRefreshed.value = Date.now();
  } finally {
    loading.value = false;
  }
}
async function manualRefresh() {
  await loadOnce();
}

// Save/Approve lokal
async function save(s) { s._dirty = false; }
async function approve(s) { s.approved = true; s._dirty = false; }

// Evidenz-Dialog
function openEvidence(session, crit) {
  const items = Array.isArray(crit.evidence) ? crit.evidence : [];
  evDialog.value = { open: true, title: `${crit.criterionName} – Evidenz (${items.length})`, items };
}
function closeEvidence() { evDialog.value = { open: false, items: [], title: '' }; }

onMounted(loadOnce);
</script>
