import { api } from "./axios";

export type Person = {
  id?: number;
  lastname?: string;
  firstname?: string;
  middlename?: string | null;
  birthdate?: string;
  passport_serial?: string;
  passport_number?: string;
  passport_issue_date?: string;
  passport_issuer?: string;
  passport_code?: string;
  license_serial?: string;
  license_number?: string;
  license_issue_date?: string;
  license_exp_date?: string;
  licence_foreign?: boolean;
  kbm?: string | number;
  phone?: string;
  email?: string;
  addresses?: Array<{
    full_address?: string;
    region?: string;
    city?: string;
    street?: string;
    house?: string;
    building?: string | null;
    apartment?: string | null;
  }>;
};

export type Vehicle = {
  id?: number;
  type?: number;
  brand?: string;
  model?: string;
  year?: number;
  license_plate?: string;
  vin?: string | null;
  body_number?: string | null;
  chassis_number?: string | null;
  power_hp?: number;
  purpose?: string;
  use_trailer?: boolean;
  sts_documents?: Array<{
    id?: number;
    doc_type?: number;
    serial?: string;
    number?: string;
    issue_date?: string;
  }>;
};

export type InsuranceCompanyInfo = {
  id?: number;
  name?: string;
  commission_percent?: string | number;
  koef?: string | number;
};

export type Calculation = {
  id: number;
  agent_id: number;
  status: string;
  policy_price?: string | number | null;
  policy_start_date?: string;
  created_at?: string;
  use_period?: number;
  driver?: Person[] | Person | null;
  owner?: Person[] | Person | null;
  vehicle?: Vehicle[] | Vehicle | null;
  company?: InsuranceCompanyInfo[] | InsuranceCompanyInfo | null;
};

export type Commission = {
  id: number;
  agent_id: number;
  insurance_company_id?: number;
  calculation_id: number;
  policy_price?: string | number;
  percent?: string | number;
  amount: string | number;
  status: string;
  paid_at?: string | null;
  created_at?: string;
};

export type Payout = {
  id: number;
  agent_id: number;
  total_amount: string | number;
  paid_at?: string;
  status?: string;
};

export const financeApi = {
  async calculations() {
    const response = await api.get<Calculation[]>("/agents/calculations");
    return response.data;
  },

  async commissions() {
    const response = await api.get<Commission[]>("/agents/commissions");
    return response.data;
  },

  async payouts() {
    const response = await api.get<Payout[]>("/agents/payouts");
    return response.data;
  },

  async createPayout() {
    const response = await api.post("/agents/payouts");
    return response.data;
  },
};
