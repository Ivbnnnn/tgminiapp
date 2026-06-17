import { api } from "./axios";

export type AgentRead = {
  id: number;
  lastname: string;
  firstname: string;
  middlename: string | null;
  phone: string;
  email: string;
  passport_serial: string;
  passport_number: string;
  passport_issue_date: string | null;
  passport_issuer: string;
  passport_code: string;
  birthdate: string | null;
  status: string;
  inn: string;
  ogrnip: string;
  is_verified: boolean;
};

export type AgentUpdate = Partial<Omit<AgentRead, "id">>;

export const agentApi = {
  async me() {
    const response = await api.get<AgentRead>("/agents/me");
    return response.data;
  },

  async update(data: AgentUpdate) {
    const response = await api.patch<AgentRead>("/agents/", data);
    return response.data;
  },
};
