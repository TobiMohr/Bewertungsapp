import axios from "axios";

const API_BASE = process.env.VUE_APP_API_URL || "/api";
const API_URL = `${API_BASE}/criteria`;

// ----- Criterion -----
export const getCriterias = () => axios.get(API_URL);
export const createCriterion = (criterion) => axios.post(API_URL, criterion);
export const getCriterion = (id) => axios.get(`${API_URL}/${id}`);
export const deleteCriterion = (id) => axios.delete(`${API_URL}/${id}`);

// ----- UserCriterion -----
export const getUserCriterias = (userId, phaseId) =>
  axios.get(`${API_URL}/user/${userId}/phase/${phaseId}`);

export const assignCriterionToUser = (criterionId, userId, phaseId) =>
  axios.post(`${API_URL}/${criterionId}/assign/${userId}/phase/${phaseId}`);

export const incrementUserCriterion = (criterionId, userId, phaseId) =>
  axios.post(`${API_URL}/${criterionId}/increment/${userId}/phase/${phaseId}`);

export const setBooleanValue = (criterionId, userId, phaseId, value) =>
  axios.put(
    `${API_URL}/${criterionId}/set/${userId}/phase/${phaseId}`,
    null,
    { params: { value } }
  );

export const setTextValue = (criterionId, userId, phaseId, value) =>
  axios.put(
    `${API_URL}/${criterionId}/text/${userId}/phase/${phaseId}`,
    { value }
  );
