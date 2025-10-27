import axios from "axios";

const API_BASE = process.env.VUE_APP_API_URL || "/api";
const USER_SESSIONS_URL = `${API_BASE}/user-sessions`;

export const getCommentsForUserInSession = (userId, sessionId) => axios.get(`${USER_SESSIONS_URL}/${sessionId}/users/${userId}/comments`);
export const addCommentForUserInSession = (userId, sessionId, text) =>
  axios.post(`${USER_SESSIONS_URL}/${sessionId}/users/${userId}/comments`, {
    text,
  });

