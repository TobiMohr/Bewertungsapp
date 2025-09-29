import axios from "axios";

const API_BASE = process.env.VUE_APP_API_URL || "/api";
const API_URL = `${API_BASE}/sessions`;

export const createSession = (session) => axios.post(`${API_URL}`, session);
export const getSessions = () => axios.get(`${API_URL}`);
export const getSession = (id) => axios.get(`${API_URL}/${id}`);
export const updateSession = (id, session) => axios.put(`${API_URL}/${id}`, session);
export const deleteSession = (id) => axios.delete(`${API_URL}/${id}`);
