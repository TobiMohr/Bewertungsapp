import axios from "axios";

const API_URL = "http://127.0.0.1:8000/criteria";

// ----- Criterion -----
export const getCriterias = () => axios.get(API_URL);
export const createCriterion = (criterion) => axios.post(API_URL, criterion);
export const getCriterion = (id) => axios.get(`${API_URL}/${id}`);
export const deleteCriterion = (id) => axios.delete(`${API_URL}/${id}`);

// ----- UserCriterion -----
export const getUserCriterias = (userId) => axios.get(`${API_URL}/user/${userId}`);
export const assignCriterionToUser = (criterionId, userId) =>
  axios.post(`${API_URL}/${criterionId}/assign/${userId}`);
export const incrementUserCriterion = (criterionId, userId) =>
  axios.post(`${API_URL}/${criterionId}/increment/${userId}`);
export const setBooleanValue = (criterionId, userId, value) =>
  axios.put(`${API_URL}/${criterionId}/set/${userId}`, null, { params: { value } });
