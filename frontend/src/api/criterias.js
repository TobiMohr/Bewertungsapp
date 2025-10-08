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

// ----- Unified Update Endpoint -----
/**
 * Update a user's criterion.
 * @param {number} criterionId 
 * @param {number} userId 
 * @param {number} phaseId 
 * @param {'increment'|'decrement'|'set_boolean'|'set_text'} action 
 * @param {boolean|string|null} value Optional value for boolean/text
 */
export const updateUserCriterion = (criterionId, userId, phaseId, action, value = null) => {
  const url = `${API_URL}/${criterionId}/${userId}/phase/${phaseId}`;
  
  // For boolean/text actions, send { value } in the body
  if (action === "set_boolean" || action === "set_text") {
    return axios.put(url, { value }, { params: { action } });
  } else {
    axios.put(url, {}, { params: { action } });

  }
};

// ----- Convenience wrappers -----
export const incrementUserCriterion = (criterionId, userId, phaseId) =>
  updateUserCriterion(criterionId, userId, phaseId, "increment");

export const decrementUserCriterion = (criterionId, userId, phaseId) =>
  updateUserCriterion(criterionId, userId, phaseId, "decrement");

export const setBooleanValue = (criterionId, userId, phaseId, value) =>
  updateUserCriterion(criterionId, userId, phaseId, "set_boolean", value);

export const setTextValue = (criterionId, userId, phaseId, value) =>
  updateUserCriterion(criterionId, userId, phaseId, "set_text", value);
