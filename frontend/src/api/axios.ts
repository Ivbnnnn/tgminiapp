import axios from "axios";

let accessToken: string | null = null;

export const api = axios.create({
  baseURL: "/api",
  timeout: 15000,
  withCredentials: true,
});

export function setAccessToken(token: string | null) {
  accessToken = token;
}

api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});
