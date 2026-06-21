import { api, setAccessToken } from "./axios";

export type User = {
  id: number;
  telegram_id: number;
  username: string | null;
};

export type ProductPhoto = { id: number; url: string; position: number };

export type Brand = { id: number; name: string; normalized_name: string };
export type Size = { id: number; name: string; type: "clothes" | "shoes" | "accessory" };

export type Product = {
  id: number;
  seller_id: number | null;
  title: string;
  description: string | null;
  price: string;
  condition: "new" | "used" | "vintage" | "damaged";
  status: string;
  seller_telegram_id: number;
  seller_telegram_username: string | null;
  color?: string | null;
  material?: string | null;
  created_at: string;
  photos: ProductPhoto[];
  brand: Brand | null;
  size: Size | null;
};

export type Seller = {
  id: number;
  user_id: number | null;
  telegram_id: number;
  username: string | null;
  display_name: string | null;
  is_active: boolean;
};

export type ProductCreate = {
  title: string;
  description?: string;
  price: string;
  condition: Product["condition"];
  color?: string;
  material?: string;
  brand_id?: number;
  size_id?: number;
};

export type ProductSearch = {
  query?: string;
  condition?: Product["condition"];
  seller_telegram_id?: number;
  min_price?: string;
  max_price?: string;
};

export const marketplaceApi = {
  async authenticate(initData: string) {
    const response = await api.post<{ access_token: string }>("/auth/telegram", {
      initData,
    });
    setAccessToken(response.data.access_token);
  },

  async me() {
    return (await api.get<User>("/users/me")).data;
  },

  async sellerMe() {
    try {
      return (await api.get<Seller>("/sellers/me")).data;
    } catch (error: unknown) {
      if (typeof error === "object" && error !== null && "response" in error) {
        const response = (error as { response?: { status?: number } }).response;
        if (response?.status === 403) return null;
      }
      throw error;
    }
  },

  async products(params: ProductSearch = {}) {
    return (await api.get<Product[]>("/products", { params })).data;
  },

  async product(productId: number) {
    return (await api.get<Product>(`/products/${productId}`)).data;
  },

  async brands() {
    return (await api.get<Brand[]>("/catalog/brands")).data;
  },

  async sizes() {
    return (await api.get<Size[]>("/catalog/sizes")).data;
  },

  async createProduct(data: ProductCreate) {
    return (await api.post<Product>("/products", data)).data;
  },

  async uploadPhoto(productId: number, file: File, position: number) {
    const form = new FormData();
    form.append("file", file);
    form.append("position", String(position));
    return (await api.post<ProductPhoto>(`/products/${productId}/photos`, form)).data;
  },

  async deleteProduct(productId: number) {
    await api.delete(`/products/${productId}`);
  },

  async addFavorite(productId: number) {
    await api.post("/favorites", { product_id: productId });
  },

  async removeFavorite(productId: number) {
    await api.delete(`/favorites/${productId}`);
  },

  async favorites() {
    return (await api.get<Product[]>("/favorites")).data;
  },

  async favoriteStatus(productId: number) {
    return (await api.get<{ is_favorite: boolean }>(`/favorites/${productId}`)).data.is_favorite;
  },
};
