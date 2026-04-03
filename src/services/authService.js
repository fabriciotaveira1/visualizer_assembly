import api from "./api";

const TOKEN_KEY = "visualizer_access_token";

export async function loginUser(credentials) {
  const response = await api.post("/auth/login", credentials);
  const token = response.data.access_token;

  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
    window.dispatchEvent(new Event("auth-changed"));
  }

  return response.data;
}

export function getAuthToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function clearAuthToken() {
  localStorage.removeItem(TOKEN_KEY);
  window.dispatchEvent(new Event("auth-changed"));
}
