import { useEffect, useState, type FormEvent } from "react";
import { useOutletContext } from "react-router-dom";
import {
  marketplaceApi,
  type Brand,
  type Product,
  type ProductCreate,
  type Size,
} from "../api/marketplaceApi";
import { ProductCard } from "../components/ProductCard";
import type { MarketplaceContext } from "../layouts/MarketplaceLayout";

type ProfileTab = "listings" | "favorites";

export default function Profile() {
  const { telegramUser, telegramId, seller } = useOutletContext<MarketplaceContext>();
  const [products, setProducts] = useState<Product[]>([]);
  const [favorites, setFavorites] = useState<Product[]>([]);
  const [activeTab, setActiveTab] = useState<ProfileTab>("listings");
  const [isLoading, setIsLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);

  const loadProducts = async () => {
    setIsLoading(true);
    try {
      const [ownProducts, favoriteProducts] = await Promise.all([
        seller
          ? marketplaceApi.myProducts()
          : marketplaceApi.products({ seller_telegram_id: telegramId }),
        marketplaceApi.favorites(),
      ]);
      setProducts(ownProducts);
      setFavorites(favoriteProducts);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { void loadProducts(); }, [telegramId, seller]);

  const visibleProducts = activeTab === "listings" ? products : favorites;

  return (
    <main className="profile-page">
      <header className="profile-header">
        {telegramUser.photo_url ? (
          <img className="profile-avatar" src={telegramUser.photo_url} alt="" />
        ) : (
          <div className="profile-avatar avatar-fallback">{telegramUser.first_name[0]}</div>
        )}
        <div>
          <span className="eyebrow">Личный кабинет</span>
          <h1>{telegramUser.first_name} {telegramUser.last_name ?? ""}</h1>
          {telegramUser.username && <p>@{telegramUser.username}</p>}
        </div>
      </header>

      {seller ? (
        <button className="sell-banner" onClick={() => setShowCreate(true)}>
          <span className="sell-icon">＋</span>
          <span><b>Добавить товар</b><small>Заполните свойства и добавьте до четырёх фото</small></span>
          <span>›</span>
        </button>
      ) : (
        <div className="seller-restricted">
          <span>⌁</span>
          <div><b>Публикация по приглашению</b><p>Размещать вещи могут только подтверждённые продавцы.</p></div>
        </div>
      )}

      <div className="profile-tabs">
        <button className={activeTab === "listings" ? "active" : ""} onClick={() => setActiveTab("listings")}>Мои товары <span>{products.length}</span></button>
        <button className={activeTab === "favorites" ? "active" : ""} onClick={() => setActiveTab("favorites")}>Понравившиеся <span>{favorites.length}</span></button>
      </div>

      <section className="my-products">
        {isLoading ? (
          <div className="product-grid"><div className="product-skeleton" /><div className="product-skeleton" /></div>
        ) : visibleProducts.length ? (
          <div className="product-grid">
            {visibleProducts.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                canDelete={activeTab === "listings" && seller !== null}
                isFavorite={activeTab === "favorites"}
                onDelete={async (id) => { await marketplaceApi.deleteProduct(id); await loadProducts(); }}
                onFavoriteChange={(id, value) => {
                  if (!value) setFavorites((current) => current.filter((item) => item.id !== id));
                }}
              />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <span>{activeTab === "favorites" ? "♡" : "◇"}</span>
            <b>{activeTab === "favorites" ? "Нет понравившихся товаров" : "Здесь пока пусто"}</b>
            <p>{activeTab === "favorites" ? "Нажмите на сердечко в каталоге — товар сохранится здесь." : "Добавьте первую вещь — она появится в общей ленте."}</p>
          </div>
        )}
      </section>

      {showCreate && seller && (
        <CreateProduct
          onClose={() => setShowCreate(false)}
          onCreated={async () => { setShowCreate(false); await loadProducts(); }}
        />
      )}
    </main>
  );
}

function CreateProduct({ onClose, onCreated }: { onClose: () => void; onCreated: () => Promise<void> }) {
  const [files, setFiles] = useState<File[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [sizes, setSizes] = useState<Size[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([marketplaceApi.brands(), marketplaceApi.sizes()])
      .then(([brandList, sizeList]) => { setBrands(brandList); setSizes(sizeList); })
      .catch(() => setError("Не удалось загрузить бренды и размеры"));
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setError("");
    const form = new FormData(event.currentTarget);
    const brandId = Number(form.get("brand_id"));
    const sizeId = Number(form.get("size_id"));
    const payload: ProductCreate = {
      title: String(form.get("title")),
      description: String(form.get("description") || "") || undefined,
      price: String(form.get("price")),
      condition: String(form.get("condition")) as ProductCreate["condition"],
      color: String(form.get("color") || "") || undefined,
      material: String(form.get("material") || "") || undefined,
      brand_id: brandId > 0 ? brandId : undefined,
      size_id: sizeId > 0 ? sizeId : undefined,
    };
    try {
      const product = await marketplaceApi.createProduct(payload);
      for (const [index, file] of files.entries()) {
        await marketplaceApi.uploadPhoto(product.id, file, index + 1);
      }
      await onCreated();
    } catch {
      setError("Не удалось опубликовать товар. Проверьте данные и фотографии.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <form className="product-form" onSubmit={submit}>
        <div className="form-heading">
          <div><span className="eyebrow">Новое объявление</span><h2>Расскажите о вещи</h2></div>
          <button type="button" onClick={onClose}>×</button>
        </div>

        <label className="photo-picker">
          <input type="file" accept="image/jpeg,image/png,image/webp" multiple onChange={(event) => setFiles(Array.from(event.target.files ?? []).slice(0, 4))} />
          <span>＋</span><b>{files.length ? `Выбрано фото: ${files.length}` : "Добавить фотографии"}</b><small>JPEG, PNG или WebP · до 4 файлов</small>
        </label>

        <label>Название<input name="title" placeholder="Например, винтажная куртка" maxLength={255} required /></label>
        <div className="form-row">
          <label>Бренд<select name="brand_id" defaultValue=""><option value="">Не указан</option>{brands.map((brand) => <option key={brand.id} value={brand.id}>{brand.name}</option>)}</select></label>
          <label>Размер<select name="size_id" defaultValue=""><option value="">Не указан</option>{sizes.map((size) => <option key={size.id} value={size.id}>{size.name} · {size.type}</option>)}</select></label>
        </div>
        <div className="form-row">
          <label>Цена, ₽<input name="price" inputMode="decimal" type="number" min="0" step="0.01" placeholder="4500" required /></label>
          <label>Состояние<select name="condition" defaultValue="used"><option value="new">Новое</option><option value="used">Б/у</option><option value="vintage">Винтаж</option><option value="damaged">С дефектом</option></select></label>
        </div>
        <div className="form-row"><label>Цвет<input name="color" placeholder="Чёрный" maxLength={64} /></label><label>Материал<input name="material" placeholder="Кожа" maxLength={128} /></label></div>
        <label>Описание<textarea name="description" rows={4} placeholder="Состояние, особенности, посадка…" maxLength={10000} /></label>
        {error && <p className="error-text">{error}</p>}
        <button className="primary-button publish-button" disabled={isSaving}>{isSaving ? "Публикуем…" : "Опубликовать"}</button>
      </form>
    </div>
  );
}
