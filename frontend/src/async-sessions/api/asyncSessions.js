// frontend/src/async-sessions/api/asyncSessions.js

// --- Mini-Persistenz für Mock-Daten (über Browser-Reloads) ---
const LS_KEY_SESSIONS  = "async_sessions_mock";
const LS_KEY_FEEDBACKS = "async_feedbacks_mock";

const load = (k, fallback) => {
    try { return JSON.parse(localStorage.getItem(k) || "") ?? fallback; }
    catch { return fallback; }
};
const save = (k, v) => localStorage.setItem(k, JSON.stringify(v));

// In-Memory-Store (mit Restore aus localStorage)
let sessions = load(LS_KEY_SESSIONS, []);
let idSeq = sessions.reduce((max, s) => Math.max(max, Number(s.id) || 0), 0) + 1;

// Map kann nicht direkt in LS – wir serialisieren simple
let _feedbacksObj = load(LS_KEY_FEEDBACKS, {}); // { [id]: feedback }
const feedbacks = new Map(Object.entries(_feedbacksObj).map(([k, v]) => [Number(k), v]));

const persist = () => {
    save(LS_KEY_SESSIONS, sessions);
    save(LS_KEY_FEEDBACKS, Object.fromEntries(feedbacks.entries()));
};

// Helper
const delay = (ms) => new Promise((r) => setTimeout(r, ms));

// --- API (Mocks) ---

// Session anlegen
export const createSession = async ({ channel_id, criteria_ids }) => {
    await delay(300);
    const s = {
        id: idSeq++,
        channelId: channel_id,
        channelName: `#${channel_id}`,
        criteriaIds: criteria_ids ?? [],
        status: "PENDING",
        approved: false,            // Anzeige in der Liste
        createdAt: new Date().toISOString(),
    };
    sessions = [s, ...sessions];
    persist();
    return { data: s };
};

// Liste laden
export const getSessions = async () => {
    await delay(200);
    return { data: sessions };
};

// Details laden
export const getSession = async (id) => {
    await delay(200);
    const s = sessions.find((x) => String(x.id) === String(id));
    return { data: s ?? null };
};

// Session löschen
export const deleteSession = async (id) => {
    await delay(200);
    const nid = Number(id);
    sessions = sessions.filter((s) => s.id !== nid);
    feedbacks.delete(nid);
    persist();
    return { data: true };
};

// Analyse starten (und Ergebnis nach ~6s simulieren)
export const startSession = async (id) => {
    await delay(200);
    const s = sessions.find((x) => String(x.id) === String(id));
    if (!s) return { data: null };

    s.status = "RUNNING";
    persist();

    setTimeout(() => {
        s.status = "DONE";
        const crits = s.criteriaIds.length ? s.criteriaIds : ["clarity", "tone", "relevance"];
        feedbacks.set(s.id, {
            sessionId: s.id,
            summaryText: `Automatisches Feedback für ${s.channelName}`,
            aggregateScore: 82,
            criteriaBreakdown: crits.map((cid, i) => ({
                criterionId: cid,
                criterionName: String(cid),
                score: 60 + i * 10,
                evidence: [],
            })),
            approved: false,
            approvedAt: null,
        });
        persist();
    }, 6000);

    return { data: s };
};

// Status/Polling
export const getStatus = async (id) => {
    await delay(300);
    const s = sessions.find((x) => String(x.id) === String(id));
    const status = s?.status ?? "PENDING";
    const progress = status === "RUNNING" ? 42 : status === "DONE" ? 100 : 0;
    return { data: { id, status, progress } };
};

// Feedback laden
export const getFeedback = async (id) => {
    await delay(200);
    return { data: feedbacks.get(Number(id)) ?? null };
};

// --- Editieren & Approven (bestehende Funktionen) ---

// Score eines Kriteriums anpassen (delta kann +1/-1 o.ä. sein)
export const updateFeedbackScore = async (sessionId, criterionId, delta) => {
    await delay(120);
    const fb = feedbacks.get(Number(sessionId));
    if (!fb) return { data: null };

    const item = fb.criteriaBreakdown.find(c => String(c.criterionId) === String(criterionId));
    if (!item) return { data: fb };

    // einfache Grenzen (0..100)
    item.score = Math.max(0, Math.min(100, (item.score || 0) + Number(delta || 0)));

    // Bearbeitung hebt Approval auf
    fb.approved = false;
    fb.approvedAt = null;

    feedbacks.set(Number(sessionId), fb);
    persist();
    return { data: fb };
};

// Feedback approven (setzt auch Session.approved = true)
export const approveFeedback = async (sessionId) => {
    await delay(120);
    const fb = feedbacks.get(Number(sessionId));
    const s  = sessions.find(x => Number(x.id) === Number(sessionId));
    if (fb) {
        fb.approved = true;
        fb.approvedAt = new Date().toISOString();
        feedbacks.set(Number(sessionId), fb);
    }
    if (s) s.approved = true; // für Anzeige in der Liste
    persist();
    return { data: fb ?? null };
};

// --- NEU: Wrapper für kompatible Imports aus der Vue-Seite ---

// Vollständiges Feedback aktualisieren (Breakdown, Summary, Score, etc.)
// Bearbeitung hebt Approval auf (wie oben).
export const updateFeedback = async (sessionId, payload) => {
    await delay(120);
    const nid = Number(sessionId);

    // Bestehendes Feedback oder leere Struktur
    const fb = feedbacks.get(nid) ?? {
        sessionId: nid,
        summaryText: "",
        aggregateScore: null,
        criteriaBreakdown: [],
        approved: false,
        approvedAt: null,
    };

    if (payload && Object.prototype.hasOwnProperty.call(payload, "summaryText")) {
        fb.summaryText = payload.summaryText ?? "";
    }
    if (payload && Object.prototype.hasOwnProperty.call(payload, "aggregateScore")) {
        fb.aggregateScore = payload.aggregateScore;
    }
    if (Array.isArray(payload?.criteriaBreakdown)) {
        fb.criteriaBreakdown = payload.criteriaBreakdown;
    }

    // Jede Bearbeitung hebt Approval auf
    fb.approved = false;
    fb.approvedAt = null;

    feedbacks.set(nid, fb);
    persist();
    return { data: fb };
};

// Approve-Workflow kompatibel zur Vue-Seite:
// optionales payload (z. B. aktuelle Edits) übernehmen, dann approven.
export const approveSession = async (sessionId, payload) => {
    await delay(120);
    const nid = Number(sessionId);

    if (Array.isArray(payload?.criteriaBreakdown) || payload?.summaryText !== undefined || payload?.aggregateScore !== undefined) {
        const existing = feedbacks.get(nid) ?? {
            sessionId: nid,
            summaryText: "",
            aggregateScore: null,
            criteriaBreakdown: [],
            approved: false,
            approvedAt: null,
        };
        if (Array.isArray(payload?.criteriaBreakdown)) existing.criteriaBreakdown = payload.criteriaBreakdown;
        if (payload?.summaryText !== undefined)       existing.summaryText = payload.summaryText ?? "";
        if (payload?.aggregateScore !== undefined)    existing.aggregateScore = payload.aggregateScore;
        feedbacks.set(nid, existing);
        persist();
    }

    // Re-Use bestehender Logik (setzt auch Session.approved)
    return await approveFeedback(nid);
};

// --- Hinweise für späteren Wechsel auf echtes Backend ---
// import api from "@/api/http";
// export const createSession   = (p)                 => api.post("/async/sessions", p);
// export const getSessions     = ()                  => api.get("/async/sessions");
// export const getSession      = (id)                => api.get(`/async/sessions/${id}`);
// export const deleteSession   = (id)                => api.delete(`/async/sessions/${id}`);
// export const startSession    = (id)                => api.post(`/async/sessions/${id}/run`);
// export const getStatus       = (id)                => api.get(`/async/sessions/${id}/status`);
// export const getFeedback     = (id)                => api.get(`/async/sessions/${id}/feedback`);
// export const approveFeedback = (id)                => api.post(`/async/sessions/${id}/approve`);
// export const updateFeedback  = (id, payload)       => api.patch(`/async/sessions/${id}/feedback`, payload);
// export const approveSession  = (id, payload)       => api.post(`/async/sessions/${id}/approve`, payload);
