import axios from "axios";

const API_BASE = process.env.VUE_APP_API_URL || "/api";
const API_URL = `${API_BASE}/users`;

export const getUsers = (teamId = null) => {
  const url = teamId ? `${API_URL}?team_id=${teamId}` : API_URL;
  return axios.get(url);
};

export const getUser = (id) => axios.get(`${API_URL}/${id}`);
export const createUser = (user) => axios.post(`${API_URL}`, user);
export const updateUser = (id, user) => axios.put(`${API_URL}/${id}`, user);
export const deleteUser = (id) => axios.delete(`${API_URL}/${id}`);
export const getUserEvaluation = (userId) =>  axios.get(`${API_URL}/${userId}/evaluation`);
