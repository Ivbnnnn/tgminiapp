import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { marketplaceApi, type Product } from "../api/marketplaceApi";
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
  const navigate = useNavigate();
  const [product, setProduct] = useState<Product | null>(null);
  const [activePhoto, setActivePhoto] = useState(0);
  const [isFavorite, setIsFavorite] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const id = Number(productId);
    if (!Number.isInteger(id) || id <= 0) {
      setError("Некорректный товар");
      setIsLoading(false);
      return;
    }
    Promise.all([marketplaceApi.product(id), marketplaceApi.favoriteStatus(id)])
      .then(([item, favorite]) => {
        setProduct(item);
        setIsFavorite(favorite);
      })
      .catch(() => setError("Товар не найден или был удалён"))
      .finally(() => setIsLoading(false));
  }, [productId]);

  if (isLoading) return <div className="detail-loading"><span className="loader" /></div>;
  if (error || !product) return <div className="empty-state"><b>{error}</b><button className="secondary-button" onClick={() => navigate(-1)}>Назад</button></div>;

  const photos = [...(product.photos ?? [])].sort((a, b) => a.position - b.position);
  const sellerUsername = product.seller_telegram_username?.replace(/^@/, "") ?? null;

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
              <button
                key={photo.id}
                className={activePhoto === index ? "active" : ""}
                onClick={() => setActivePhoto(index)}
                aria-label={`Фото ${index + 1}`}
              />
            ))}
          </div>
        )}
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

        {product.description && (
          <div className="detail-description"><h2>Описание</h2><p>{product.description}</p></div>
        )}

        <div className="seller-card">
          <div className="seller-card-avatar">{sellerUsername?.[0]?.toUpperCase() ?? "S"}</div>
          <div><small>Продавец</small><b>{sellerUsername ? `@${sellerUsername}` : "Пользователь Telegram"}</b></div>
        </div>

        <button
          className="primary-button contact-seller"
          disabled={!sellerUsername}
          onClick={() => sellerUsername && openSellerChat(sellerUsername)}
        >{sellerUsername ? "Написать продавцу" : "У продавца скрыт username"}</button>
      </section>
    </main>
  );
}

function Property({ label, value }: { label: string; value: string }) {
  return <div><span>{label}</span><b>{value}</b></div>;
}
