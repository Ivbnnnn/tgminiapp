import { useState } from "react";
import { marketplaceApi, type Product } from "../api/marketplaceApi";

const money = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
  maximumFractionDigits: 0,
});

const conditions: Record<Product["condition"], string> = {
  new: "Новое",
  used: "Б/у",
  vintage: "Винтаж",
  damaged: "С дефектом",
};

export function ProductCard({
  product,
  canDelete = false,
  onDelete,
}: {
  product: Product;
  canDelete?: boolean;
  onDelete?: (id: number) => Promise<void>;
}) {
  const [isFavorite, setIsFavorite] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const photo = [...product.photos].sort((a, b) => a.position - b.position)[0];

  return (
    <article className="product-card">
      <div className="product-image-wrap">
        {photo ? (
          <img className="product-image" src={photo.url} alt={product.title} loading="lazy" />
        ) : (
          <div className="product-placeholder"><span>◇</span>Без фото</div>
        )}
        <span className="condition">{conditions[product.condition]}</span>
        {!canDelete && (
          <button
            type="button"
            className={`favorite-button ${isFavorite ? "is-active" : ""}`}
            aria-label="Добавить в избранное"
            onClick={async () => {
              await marketplaceApi.addFavorite(product.id);
              setIsFavorite(true);
            }}
          >{isFavorite ? "♥" : "♡"}</button>
        )}
      </div>
      <div className="product-copy">
        <div className="product-price-row">
          <strong>{money.format(Number(product.price))}</strong>
          {product.seller_telegram_username && <span>@{product.seller_telegram_username}</span>}
        </div>
        <h2>{product.title}</h2>
        {(product.color || product.material) && (
          <p className="product-meta">{[product.color, product.material].filter(Boolean).join(" · ")}</p>
        )}
        {canDelete && (
          <button
            className="delete-listing"
            disabled={isDeleting}
            onClick={async () => {
              if (!onDelete) return;
              setIsDeleting(true);
              try { await onDelete(product.id); } finally { setIsDeleting(false); }
            }}
          >{isDeleting ? "Удаляем…" : "Снять с публикации"}</button>
        )}
      </div>
    </article>
  );
}
