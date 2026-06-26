import { useEffect, useState, type FormEvent } from "react";
import { useNavigate, useOutletContext, useParams } from "react-router-dom";
import {
  marketplaceApi,
  type Brand,
  type Product,
  type ProductUpdate,
  type Size,
} from "../api/marketplaceApi";
import type { MarketplaceContext } from "../layouts/MarketplaceLayout";
import { openSellerChat } from "../telegram";

const money = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
  maximumFractionDigits: 0,
});

const conditionLabels: Record<Product["condition"], string> = {
  new: "Новое",
  used: "Б/у",
  vintage: "Винтаж",
  damaged: "С дефектом",
};

export default function ProductPage() {
  const { productId } = useParams();
  const { seller, telegramId, isAdmin } = useOutletContext<MarketplaceContext>();
  const navigate = useNavigate();
  const [product, setProduct] = useState<Product | null>(null);
  const [activePhoto, setActivePhoto] = useState(0);
  const [isFavorite, setIsFavorite] = useState(false);
  const [showEdit, setShowEdit] = useState(false);
  const [isActionLoading, setIsActionLoading] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const id = Number(productId);

  async function loadProduct() {
    const [item, favorite] = await Promise.all([
      marketplaceApi.product(id),
      marketplaceApi.favoriteStatus(id),
    ]);
    setProduct(item);
    setIsFavorite(favorite);
  }

  useEffect(() => {
    if (!Number.isInteger(id) || id <= 0) {
      setError("Некорректный товар");
      setIsLoading(false);
      return;
    }
    loadProduct()
      .catch(() => setError("Товар не найден или был удалён"))
      .finally(() => setIsLoading(false));
  }, [id]);

  if (isLoading) return <div className="detail-loading"><span className="loader" /></div>;
  if (error || !product) return <div className="empty-state"><b>{error}</b><button className="secondary-button" onClick={() => navigate(-1)}>Назад</button></div>;

  const photos = [...(product.photos ?? [])].sort((a, b) => a.position - b.position);
  const sellerUsername = product.seller_telegram_username?.replace(/^@/, "") ?? null;
  const isOwner = Boolean(
    seller && (product.seller_id === seller.id || product.seller_telegram_id === telegramId),
  );
  const isHidden = product.status === "hidden";

  async function changeStatus(status: "active" | "hidden", asAdmin = false) {
    setIsActionLoading(true);
    try {
      if (asAdmin) await marketplaceApi.moderateProduct(id, status);
      else await marketplaceApi.updateProduct(id, { status });
      await loadProduct();
    } finally {
      setIsActionLoading(false);
    }
  }

  return (
    <main className="product-detail-page">
      <header className="detail-topbar">
        <button onClick={() => navigate(-1)} aria-label="Назад">‹</button>
        <span>Объявление</span>
        <button
          className={isFavorite ? "is-favorite" : ""}
          aria-label={isFavorite ? "Удалить из избранного" : "Добавить в избранное"}
          onClick={async () => {
            if (isFavorite) await marketplaceApi.removeFavorite(product.id);
            else await marketplaceApi.addFavorite(product.id);
            setIsFavorite((value) => !value);
          }}
        >{isFavorite ? "♥" : "♡"}</button>
      </header>

      <section className="detail-gallery">
        {photos[activePhoto] ? (
          <img src={photos[activePhoto].url} alt={product.title} />
        ) : (
          <div className="detail-placeholder">◇<span>Фотографий пока нет</span></div>
        )}
        {photos.length > 1 && (
          <div className="gallery-dots">
            {photos.map((photo, index) => (
              <button key={photo.id} className={activePhoto === index ? "active" : ""} onClick={() => setActivePhoto(index)} aria-label={`Фото ${index + 1}`} />
            ))}
          </div>
        )}
        {isHidden && <span className="moderation-badge">Скрыто с витрины</span>}
      </section>

      <section className="detail-content">
        <div className="detail-price-row">
          <div><span>{conditionLabels[product.condition]}</span><h1>{product.title}</h1></div>
          <strong>{money.format(Number(product.price))}</strong>
        </div>

        <div className="detail-properties">
          {product.brand && <Property label="Бренд" value={product.brand.name} />}
          {product.size && <Property label="Размер" value={product.size.name} />}
          {product.color && <Property label="Цвет" value={product.color} />}
          {product.material && <Property label="Материал" value={product.material} />}
        </div>

        {product.description && <div className="detail-description"><h2>Описание</h2><p>{product.description}</p></div>}

        <div className="seller-card">
          <div className="seller-card-avatar">{sellerUsername?.[0]?.toUpperCase() ?? "S"}</div>
          <div><small>Продавец</small><b>{sellerUsername ? `@${sellerUsername}` : "Пользователь Telegram"}</b></div>
        </div>

        {isOwner && (
          <div className="management-panel owner-panel">
            <span className="eyebrow">Управление товаром</span>
            <button className="primary-button" onClick={() => setShowEdit(true)}>Редактировать</button>
            <button className="secondary-button" disabled={isActionLoading} onClick={() => void changeStatus(isHidden ? "active" : "hidden")}>{isHidden ? "Вернуть в продажу" : "Снять с продажи"}</button>
          </div>
        )}

        {isAdmin && (
          <div className="management-panel admin-panel">
            <span className="eyebrow">Модерация</span>
            <button className="secondary-button" disabled={isActionLoading} onClick={() => void changeStatus(isHidden ? "active" : "hidden", true)}>{isHidden ? "Одобрить и вернуть" : "Временно скрыть"}</button>
            <button
              className="admin-delete-button"
              disabled={isActionLoading}
              onClick={async () => {
                if (!window.confirm("Удалить товар без возможности восстановления?")) return;
                setIsActionLoading(true);
                try { await marketplaceApi.deleteProduct(id); navigate("/", { replace: true }); }
                finally { setIsActionLoading(false); }
              }}
            >Удалить товар</button>
          </div>
        )}

        {!isOwner && !isAdmin && (
          <button className="primary-button contact-seller" disabled={!sellerUsername} onClick={() => sellerUsername && openSellerChat(sellerUsername)}>
            {sellerUsername ? "Написать продавцу" : "У продавца скрыт username"}
          </button>
        )}
      </section>

      {showEdit && (
        <EditProduct
          product={product}
          onClose={() => setShowEdit(false)}
          onSaved={async () => { setShowEdit(false); await loadProduct(); }}
        />
      )}
    </main>
  );
}

function Property({ label, value }: { label: string; value: string }) {
  return <div><span>{label}</span><b>{value}</b></div>;
}

function EditProduct({ product, onClose, onSaved }: { product: Product; onClose: () => void; onSaved: () => Promise<void> }) {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [sizes, setSizes] = useState<Size[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([marketplaceApi.brands(), marketplaceApi.sizes()])
      .then(([brandList, sizeList]) => { setBrands(brandList); setSizes(sizeList); })
      .catch(() => setError("Не удалось загрузить справочники"));
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setError("");
    const form = new FormData(event.currentTarget);
    const brandId = Number(form.get("brand_id"));
    const sizeId = Number(form.get("size_id"));
    const data: ProductUpdate = {
      title: String(form.get("title")),
      description: String(form.get("description") || ""),
      price: String(form.get("price")),
      condition: String(form.get("condition")) as Product["condition"],
      color: String(form.get("color") || ""),
      material: String(form.get("material") || ""),
      brand_id: brandId > 0 ? brandId : null,
      size_id: sizeId > 0 ? sizeId : null,
    };
    try {
      await marketplaceApi.updateProduct(product.id, data);
      await onSaved();
    } catch {
      setError("Не удалось сохранить изменения");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <form className="product-form" onSubmit={submit}>
        <div className="form-heading"><div><span className="eyebrow">Редактирование</span><h2>{product.title}</h2></div><button type="button" onClick={onClose}>×</button></div>
        <label>Название<input name="title" defaultValue={product.title} maxLength={255} required /></label>
        <div className="form-row">
          <label>Бренд<select name="brand_id" defaultValue={product.brand?.id ?? ""}><option value="">Не указан</option>{brands.map((brand) => <option key={brand.id} value={brand.id}>{brand.name}</option>)}</select></label>
          <label>Размер<select name="size_id" defaultValue={product.size?.id ?? ""}><option value="">Не указан</option>{sizes.map((size) => <option key={size.id} value={size.id}>{size.name}</option>)}</select></label>
        </div>
        <div className="form-row">
          <label>Цена, ₽<input name="price" type="number" min="0" step="0.01" defaultValue={product.price} required /></label>
          <label>Состояние<select name="condition" defaultValue={product.condition}><option value="new">Новое</option><option value="used">Б/у</option><option value="vintage">Винтаж</option><option value="damaged">С дефектом</option></select></label>
        </div>
        <div className="form-row"><label>Цвет<input name="color" defaultValue={product.color ?? ""} /></label><label>Материал<input name="material" defaultValue={product.material ?? ""} /></label></div>
        <label>Описание<textarea name="description" rows={5} defaultValue={product.description ?? ""} /></label>
        {error && <p className="error-text">{error}</p>}
        <button className="primary-button publish-button" disabled={isSaving}>{isSaving ? "Сохраняем…" : "Сохранить"}</button>
      </form>
    </div>
  );
}
