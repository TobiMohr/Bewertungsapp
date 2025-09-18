import axios from "axios";

const API_URL = "http://127.0.0.1:8000/auth";

export const registerUser = (user) => axios.post(`${API_URL}/register`, user);
export const loginUser = (credentials) => axios.post(`${API_URL}/login`, credentials);
