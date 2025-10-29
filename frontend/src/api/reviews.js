// src/async-sessions/api/reviews.js
import axios from "axios";
import { buildChannelReviews } from "@/async-sessions/adapters/reviewAdapter";
import { MESSAGES, MESSAGE_CRITERIA, CRITERIAS, USERS } from "@/async-sessions/mock/backendShape.sample";

// Toggle: Sobald dein Endpoint steht -> auf true setzen ODER Logik unten auf Backend umstellen
const USE_BACKEND = false;

// Basis-URL wie im Projekt üblich
const API_BASE = process.env.VUE_APP_API_URL || "/api";

/**
 * Liefert die Datensätze für die MVP-Tabelle.
 * - Mock: baut aus Messages/MessageCriteria/Criterias (+Users) die UI-Struktur
 * - Backend: ruft später deinen Endpoint auf
 */
export async function fetchReviews() {
    if (!USE_BACKEND) {
        // MOCK-PFAD (heute)
        return buildChannelReviews(
            MESSAGES,
            MESSAGE_CRITERIA,
            CRITERIAS,
            undefined,  // cfg
            true,       // includeEvidence
            USERS
        );
    }

    // BACKEND-PFAD (morgen) – Beispiel:
    // Erwartet: Der Endpoint liefert bereits die "UI-Form" (id, channelName, status, approved, summaryText, aggregateScore, _editedBreakdown[], updatedAt, createdAt)
    const { data } = await axios.get(`${API_BASE}/messages/reviews`, {
        // Cache-Busting, damit der Klick sichtbar „neu lädt“
        params: { _: Date.now() },
    });
    return data ?? [];
}
