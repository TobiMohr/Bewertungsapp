import { ref } from "vue";

const token = ref(localStorage.getItem("token"));
const isLoggedIn = ref(!!token.value);

export function useAuth() {
  function login(newToken) {
    token.value = newToken;
    localStorage.setItem("token", newToken);
    isLoggedIn.value = true;
  }

  function logout() {
    token.value = null;
    localStorage.removeItem("token");
    isLoggedIn.value = false;
  }

  return { token, isLoggedIn, login, logout };
}
