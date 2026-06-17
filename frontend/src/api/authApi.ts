import { api } from "./axios";

export type SignUpRequest = {
  lastname: string;
  firstname: string;
  middlename: string;
  phone: string;
  email: string;
  passport_serial: string;
  passport_number: string;
  passport_issue_date: string;
  passport_issuer: string;
  passport_code: string;
  birthdate: string;
  status: string;
  inn: string;
  ogrnip: string;
  password: string;
};

export type LoginRequest = {
  email: string;
  password: string;
};

export type AuthResponse = {
  detail: string;
};

export const authApi = {
  async signup(data: SignUpRequest) {
    const response = await api.post<AuthResponse>("/auth/register", data);
    return response.data;
  },

  async login(data: LoginRequest) {
    const response = await api.post<AuthResponse>("/auth/login", data);
    return response.data;
  },

  async refresh() {
    const response = await api.post<AuthResponse>("/auth/refresh");
    return response.data;
  },

  async logout() {
    const response = await api.post<AuthResponse>("/auth/logout");
    return response.data;
  },
};