import axios from "axios";

const API_URL = "http://127.0.0.1:8000/sessions";

export const createSession = (session) => axios.post(API_URL, session);
export const getSessions = () => axios.get(API_URL);
export const getSession = (id) => axios.get(`${API_URL}/${id}`);
export const updateSession = (id, session) => axios.put(`${API_URL}/${id}`, session);
export const deleteSession = (id) => axios.delete(`${API_URL}/${id}`);
