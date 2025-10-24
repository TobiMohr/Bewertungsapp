import axios from "axios";

const API_BASE = process.env.VUE_APP_API_URL || "/api";
const API_URL = `${API_BASE}/auth`;

export const registerUser = (user) => axios.post(`${API_URL}/register/`, user);
export const loginUser = (credentials) => axios.post(`${API_URL}/login/`, credentials);
