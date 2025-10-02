import axios from "axios";

const API_BASE = process.env.VUE_APP_API_URL || "/api";
const API_URL = `${API_BASE}/phases`;

export const getPhase = (id) => axios.get(`${API_URL}/${id}`);
export const updatePhase = (id, phase) => axios.put(`${API_URL}/${id}`, phase);
