import axios from "axios";

const API_BASE = process.env.VUE_APP_API_URL || "/api";
const API_URL = `${API_BASE}/criteria`;

// ----- Criterion -----
export const getCriterias = () => axios.get(API_URL);
export const createCriterion = (criterion) => axios.post(API_URL, criterion);
export const getCriterion = (id) => axios.get(`${API_URL}/${id}`);
export const deleteCriterion = (id) => axios.delete(`${API_URL}/${id}`);

// ----- UserCriterion -----
export const getUserCriterias = (userId, sessionId) =>
  axios.get(`${API_URL}/user/${userId}/session/${sessionId}`);

export const assignCriterionToUser = (criterionId, userId, sessionId) =>
  axios.post(`${API_URL}/${criterionId}/assign/${userId}/session/${sessionId}`);

export const incrementUserCriterion = (criterionId, userId, sessionId) =>
  axios.post(`${API_URL}/${criterionId}/increment/${userId}/session/${sessionId}`);

export const setBooleanValue = (criterionId, userId, sessionId, value) =>
  axios.put(
    `${API_URL}/${criterionId}/set/${userId}/session/${sessionId}`,
    null,
    { params: { value } }
  );

export const setTextValue = (criterionId, userId, sessionId, value) =>
  axios.put(
    `${API_URL}/${criterionId}/text/${userId}/session/${sessionId}`,
    { value }
  );
