// frontend/src/async-sessions/api/asyncSessions.js

// --- Mini-Persistenz für Mock-Daten (über Browser-Reloads) ---
const LS_KEY_SESSIONS = "async_sessions_mock";
const LS_KEY_FEEDBACKS = "async_feedbacks_mock";

const load = (k, fallback) => {
    try { return JSON.parse(localStorage.getItem(k) || "") ?? fallback; } catch { return fallback; }
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

// --- helpers ---
const delay = (ms) => new Promise((r) => setTimeout(r, ms));

// --- API (Mocks) ---
export const createSession = async ({ channel_id, criteria_ids }) => {
    await delay(300);
    const s = {
        id: idSeq++,
        channelId: channel_id,
        channelName: `#${channel_id}`,
        criteriaIds: criteria_ids ?? [],
        status: "PENDING",
        createdAt: new Date().toISOString(),
    };
    sessions = [s, ...sessions];
    persist();
    return { data: s };
};

export const getSessions = async () => {
    await delay(200);
    return { data: sessions };
};

export const getSession = async (id) => {
    await delay(200);
    const s = sessions.find((x) => String(x.id) === String(id));
    return { data: s ?? null };
};

export const deleteSession = async (id) => {
    await delay(200);
    const nid = Number(id);
    sessions = sessions.filter((s) => s.id !== nid);
    feedbacks.delete(nid);
    persist();
    return { data: true };
};

export const startSession = async (id) => {
    await delay(200);
    const s = sessions.find((x) => String(x.id) === String(id));
    if (!s) return { data: null };
    s.status = "RUNNING";
    persist();

    // Simuliere Abschluss + Ergebnis nach ~6s
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
        });
        persist();
    }, 6000);

    return { data: s };
};

export const getStatus = async (id) => {
    await delay(300);
    const s = sessions.find((x) => String(x.id) === String(id));
    const status = s?.status ?? "PENDING";
    const progress = status === "RUNNING" ? 42 : status === "DONE" ? 100 : 0;
    return { data: { id, status, progress } };
};

export const getFeedback = async (id) => {
    await delay(200);
    return { data: feedbacks.get(Number(id)) ?? null };
};

// --- Hinweise für späteren Wechsel auf echtes Backend ---
// import api from "@/api/http";
// export const createSession = (p) => api.post("/async/sessions", p);
// export const getSessions = () => api.get("/async/sessions");
// export const getSession  = (id) => api.get(`/async/sessions/${id}`);
// export const deleteSession = (id) => api.delete(`/async/sessions/${id}`);
// export const startSession = (id) => api.post(`/async/sessions/${id}/run`);
// export const getStatus    = (id) => api.get(`/async/sessions/${id}/status`);
// export const getFeedback  = (id) => api.get(`/async/sessions/${id}/feedback`);
