import axios from "axios";

const API_BASE = process.env.VUE_APP_API_URL || "/api";
const FILES_URL = `${API_BASE}/files`;

// Export as XLSX
export const exportUsersXLSX = () =>
  axios.get(`${FILES_URL}/export`, { responseType: "blob" });

// Import XLSX
export const importUsersXLSX = (formData) =>
  axios.post(`${FILES_URL}/import`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
