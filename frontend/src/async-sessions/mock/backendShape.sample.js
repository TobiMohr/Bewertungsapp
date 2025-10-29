// src/async-sessions/mock/backendShape.sample.js
// --- USERS (aus CSV 1)
export const USERS = [
    { id: 1, first_name: "Alice", last_name: "Demo",   email: "alice@example.com", username: "alice",
        created_at: "2025-10-27T11:37:03.808764+00:00" },
    { id: 2, first_name: "Bob",   last_name: "Beispiel", email: "bob@example.com",   username: "bob",
        created_at: "2025-10-27T11:37:03.816126+00:00" },
    { id: 3, first_name: "Carol", last_name: "Test",   email: "carol@example.com", username: "carol",
        created_at: "2025-10-27T11:37:03.819061+00:00" },
    { id: 4, first_name: "Dave",  last_name: "Mustermann", email: "dave@example.com", username: "dave",
        created_at: "2025-10-27T11:37:03.821952+00:00" },
    { id: 5, first_name: "Eve",   last_name: "Musterfrau", email: "eve@example.com",  username: "eve",
        created_at: "2025-10-27T11:37:03.824502+00:00" },
];

// --- CRITERIA (aus CSV 4)
export const CRITERIAS = [
    { id: 1,  name: "Antwortzeit",        type: "countable" },
    { id: 2,  name: "Frequenz",           type: "countable" },
    { id: 3,  name: "Fachliches Eingehen", type: "countable" },
    { id: 4,  name: "Ergebnisorientierung", type: "countable" },
    { id: 5,  name: "Form und Wortwahl",  type: "countable" },
    { id: 6,  name: "Adressatengerecht",  type: "countable" },
    { id: 7,  name: "Selbstaeusserung",   type: "countable" },
    { id: 8,  name: "Quantität",          type: "countable" },
    { id: 9,  name: "Qualität",           type: "countable" },
    { id: 10, name: "Verständnis 1",      type: "countable" },
    { id: 11, name: "Identifikation 1",   type: "countable" },
    { id: 12, name: "Verständnis 2",      type: "countable" },
    { id: 13, name: "Identifikation 2",   type: "countable" },
    { id: 14, name: "Teamziele",          type: "countable" },
    { id: 15, name: "Valenz",             type: "countable" },
    { id: 16, name: "Instrumentalität",   type: "countable" },
    { id: 17, name: "Selbstwirksamkeit",  type: "countable" },
    { id: 18, name: "Vertrauen",          type: "countable" },
    { id: 19, name: "Teamgeist",          type: "countable" },
    { id: 20, name: "Smalltalk",          type: "countable" },
];

// --- MESSAGES (aus CSV 2)
export const MESSAGES = [
    { id: 1,  content: "Dies ist ein Test aus der CI!", user_id: 1, channel: "ci-test",
        message_id: "ci-msg-123",  channel_id: "ci-chan-1", sent_at: "2025-10-27T12:34:56Z",
        platform: "ci", roles: "tester", created_at: "2025-10-27T11:37:19.694092+00:00" },
    { id: 2,  content: "Dies ist ein Test aus der CI!", user_id: 1, channel: "ci-test",
        message_id: "ci-msg-1234", channel_id: "ci-chan-1", sent_at: "2025-10-27T12:34:56Z",
        platform: "ci", roles: "tester", created_at: "2025-10-27T11:38:15.510655+00:00" },
    { id: 3,  content: "Dies ist ein Test aus der CI!", user_id: 1, channel: "ci-test",
        message_id: "ci-msg-12345", channel_id: "ci-chan-1", sent_at: "2025-10-27T12:34:56Z",
        platform: "ci", roles: "tester", created_at: "2025-10-27T11:40:12.141000+00:00" },
    { id: 4,  content: "Dies ist ein Test aus der CI!", user_id: 1, channel: "ci-test",
        message_id: "ci-msg-123456", channel_id: "ci-chan-1", sent_at: "2025-10-27T12:34:56Z",
        platform: "ci", roles: "tester", created_at: "2025-10-27T11:41:54.095995+00:00" },
    { id: 5,  content: "Dies ist ein Test aus der CI!", user_id: 1, channel: "ci-test",
        message_id: "ci-msg-1234567", channel_id: "ci-chan-1", sent_at: "2025-10-27T12:34:56Z",
        platform: "ci", roles: "tester", created_at: "2025-10-27T11:42:22.994252+00:00" },
];

// --- MESSAGE_CRITERIA (aus CSV 3; stark gekürzt – ergänze ggf. weitere Zeilen)
export const MESSAGE_CRITERIA = [
    // message 1
    { id: 1,  message_id: 1, criterion_id: 1, reviewed: false, count_value: 0, is_fulfilled: null, text_value: null,
        created_at: "2025-10-27T11:37:29.221446+00:00" },
    { id: 2,  message_id: 1, criterion_id: 2, reviewed: false, count_value: 1, is_fulfilled: null, text_value: null,
        created_at: "2025-10-27T11:37:29.221455+00:00" },
    // message 2
    { id: 21, message_id: 2, criterion_id: 1, reviewed: false, count_value: 0, is_fulfilled: null, text_value: null,
        created_at: "2025-10-27T11:38:19.411296+00:00" },
    { id: 22, message_id: 2, criterion_id: 2, reviewed: false, count_value: 1, is_fulfilled: null, text_value: null,
        created_at: "2025-10-27T11:38:19.411308+00:00" },
    // … (fülle gemäß deiner CSV alle Zeilen weiter aus)
];
