import axios from "axios";

const API_BASE = process.env.VUE_APP_API_URL || "/api";
const USER_SESSIONS_URL = `${API_BASE}/user-sessions`;
const ROLES_URL = `${API_BASE}/roles`;

// --- Role CRUD ---
export const getRoles = () => axios.get(`${ROLES_URL}`);
export const getRole = (id) => axios.get(`${ROLES_URL}/${id}`);
export const createRole = (role) => axios.post(`${ROLES_URL}`, role);
export const updateRole = (id, role) => axios.put(`${ROLES_URL}/${id}`, role);
export const deleteRole = (id) => axios.delete(`${ROLES_URL}/${id}`);

// --- Assign or Get Role for a User in a Session ---
export const getUserRoleForSession = (userId, sessionId) =>
  axios.get(`${USER_SESSIONS_URL}/${sessionId}/users/${userId}/role`);

export const assignRoleToUserInSession = (userId, sessionId, roleId) =>
  axios.post(`${USER_SESSIONS_URL}/${sessionId}/users/${userId}/role`, {
    role_id: roleId,
  });
