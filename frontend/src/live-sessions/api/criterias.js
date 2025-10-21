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

// ----- Unified Update Endpoint -----
/**
 * Update a user's criterion.
 * @param {number} criterionId 
 * @param {number} userId 
 * @param {number} sessionId 
 * @param {'increment'|'decrement'|'set_boolean'|'set_text'} action 
 * @param {boolean|string|null} value Optional value for boolean/text
 */
export const updateUserCriterion = (criterionId, userId, sessionId, action, value = null) => {
  const url = `${API_URL}/${criterionId}/${userId}/session/${sessionId}`;
  
  // For boolean/text actions, send { value } in the body
  if (action === "set_boolean" || action === "set_text") {
    return axios.put(url, { value }, { params: { action } });
  } else {
    axios.put(url, {}, { params: { action } });

  }
};

// ----- Convenience wrappers -----
export const incrementUserCriterion = (criterionId, userId, sessionId) =>
  updateUserCriterion(criterionId, userId, sessionId, "increment");

export const decrementUserCriterion = (criterionId, userId, sessionId) =>
  updateUserCriterion(criterionId, userId, sessionId, "decrement");

export const setBooleanValue = (criterionId, userId, sessionId, value) =>
  updateUserCriterion(criterionId, userId, sessionId, "set_boolean", value);

export const setTextValue = (criterionId, userId, sessionId, value) =>
  updateUserCriterion(criterionId, userId, sessionId, "set_text", value);

/**
 * Get all user criteria entries for a specific criterion (optionally filtered by phase)
 * @param {number} criterionId 
 * @param {number|null} sessionId 
 * @returns {Promise<AxiosResponse>}
 */
export const getUserCriteriasForCriterion = (criterionId, sessionId = null) => {
  const params = sessionId ? { sessionId: sessionId } : {};
  return axios.get(`${API_URL}/${criterionId}/users`, { params });
};
