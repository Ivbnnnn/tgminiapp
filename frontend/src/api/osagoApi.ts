import { api } from "./axios";

export type InsuranceCompany = {
  id: number;
  name: string;
  commission_percent?: string | number;
  koef?: string | number;
};

export type CalculationRequest = {
  lastname: string;
  firstname: string;
  middlename?: string | null;
  insurance_companies?: string[] | null;
  license_plate?: string | null;
  vin?: string | null;
  body_number?: string | null;
  chassis_number?: string | null;
  license_serial?: string | null;
  license_number?: string | null;
  use_period: number;
  policy_start_date: string;
};

export type TestCalculationData = CalculationRequest;

export type Offer = {
  id?: number;
  company_id?: number;
  insurance_company_id?: number;
  name?: string;
  company_name?: string;
  policy_price?: string | number;
  price?: string | number;
  commission_percent?: string | number;
  koef?: string | number;
};

export type OffersResponse = {
  calculation_id?: number;
  agent_id?: number;
  status?: string;
  offers: Offer[];
};

export type SearchFilter = {
  field: string;
  value: string;
};

export type SearchRequest = {
  model_name: string;
  relations: string[];
  filters: SearchFilter[];
};

export const osagoApi = {
  async companies() {
    const response = await api.get<InsuranceCompany[]>("/osago/companies");
    return response.data;
  },

  async getOffers(data: CalculationRequest) {
    const response = await api.post<OffersResponse>("/osago/get_offers", data);
    return response.data;
  },

  async testData() {
    const response = await api.get<TestCalculationData>("/osago/test-data");
    return response.data;
  },

  async chooseOffer(companyId: number, calculationId: number) {
    const response = await api.post("/osago/choose_offer", {
      company_id: companyId,
      calculation_id: calculationId,
    });
    return response.data;
  },

  async payOffer(calculationId: number) {
    const response = await api.post("/osago/pay_offer", {
      calculation_id: calculationId,
    });
    return response.data;
  },

  async cancelOffer(companyId: number, calculationId: number) {
    const response = await api.post("/osago/cancel_offer", {
      company_id: companyId,
      calculation_id: calculationId,
    });
    return response.data;
  },

  async search(data: SearchRequest) {
    const response = await api.post<unknown[]>("/osago/search", data);
    return response.data;
  },
};
