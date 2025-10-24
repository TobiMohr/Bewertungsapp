import axios from "axios";

const API_BASE = process.env.VUE_APP_API_URL || "/api";
const API_URL = `${API_BASE}/teams`;

// --- Teams API ---
export const getTeams = () => axios.get(`${API_URL}`);
export const getTeam = (id) => axios.get(`${API_URL}/${id}`);
export const createTeam = (team) => axios.post(`${API_URL}`, team);
export const updateTeam = (id, team) => axios.put(`${API_URL}/${id}`, team);
export const deleteTeam = (id) => axios.delete(`${API_URL}/${id}`);

// --- Assign user to a team ---
export const assignUserToTeam = (teamId, userId) =>
  axios.put(`${API_URL}/${teamId}/assign_user/${userId}`);
