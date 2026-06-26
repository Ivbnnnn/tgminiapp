import { useEffect, useState } from "react";
import { Heart, ImageOff } from "lucide-react";
import { Link } from "react-router-dom";
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
  isFavorite = false,
  onDelete,
  onFavoriteChange,
}: {
  product: Product;
  canDelete?: boolean;
  isFavorite?: boolean;
  onDelete?: (id: number) => Promise<void>;
  onFavoriteChange?: (id: number, value: boolean) => void;
}) {
  const [favorite, setFavorite] = useState(isFavorite);
  const [isFavoriteLoading, setIsFavoriteLoading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const photo = [...(product.photos ?? [])].sort((a, b) => a.position - b.position)[0];

  useEffect(() => setFavorite(isFavorite), [isFavorite]);

  async function toggleFavorite() {
    if (isFavoriteLoading) return;
    setIsFavoriteLoading(true);
    try {
      if (favorite) await marketplaceApi.removeFavorite(product.id);
      else await marketplaceApi.addFavorite(product.id);
      const nextValue = !favorite;
      setFavorite(nextValue);
      onFavoriteChange?.(product.id, nextValue);
    } finally {
      setIsFavoriteLoading(false);
    }
  }

  return (
    <article className="product-card">
      <div className="product-image-wrap">
        <Link to={`/products/${product.id}`} className="product-image-link">
          {photo ? (
            <img className="product-image" src={photo.url} alt={product.title} loading="lazy" />
          ) : (
            <div className="product-placeholder"><span><ImageOff aria-hidden="true" /></span>Без фото</div>
          )}
          <span className="condition">{conditions[product.condition]}</span>
        </Link>
        {!canDelete && (
          <button
            type="button"
            className={`favorite-button ${favorite ? "is-active" : ""}`}
            aria-label={favorite ? "Удалить из избранного" : "Добавить в избранное"}
            disabled={isFavoriteLoading}
            onClick={() => void toggleFavorite()}
          ><Heart aria-hidden="true" fill={favorite ? "currentColor" : "none"} /></button>
        )}
      </div>
      <div className="product-copy">
        <div className="product-price-row">
          <strong>{money.format(Number(product.price))}</strong>
          {product.seller_telegram_username && <span>@{product.seller_telegram_username}</span>}
        </div>
        <Link to={`/products/${product.id}`} className="product-title-link"><h2>{product.title}</h2></Link>
        {(product.brand || product.size || product.color || product.material) && (
          <p className="product-meta">
            {[product.brand?.name, product.size?.name, product.color, product.material].filter(Boolean).join(" · ")}
          </p>
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
