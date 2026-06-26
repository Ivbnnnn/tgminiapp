import { useEffect, useState } from "react";
import { Search, SearchX, X } from "lucide-react";
import { useOutletContext } from "react-router-dom";
import { marketplaceApi, type Product } from "../api/marketplaceApi";
import { ProductCard } from "../components/ProductCard";
import type { MarketplaceContext } from "../layouts/MarketplaceLayout";

const conditionFilters: Array<{ value: "" | Product["condition"]; label: string }> = [
  { value: "", label: "Все" },
  { value: "new", label: "Новое" },
  { value: "used", label: "Б/у" },
  { value: "vintage", label: "Винтаж" },
  { value: "damaged", label: "С дефектом" },
];

export default function Home() {
  const { telegramUser } = useOutletContext<MarketplaceContext>();
  const [query, setQuery] = useState("");
  const [condition, setCondition] = useState<"" | Product["condition"]>("");
  const [products, setProducts] = useState<Product[]>([]);
  const [favoriteIds, setFavoriteIds] = useState<Set<number>>(new Set());
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const timeout = window.setTimeout(async () => {
      setIsLoading(true);
      setError("");
      try {
        const [productList, favorites] = await Promise.all([
          marketplaceApi.products({
            query: query.trim() || undefined,
            condition: condition || undefined,
          }),
          marketplaceApi.favorites(),
        ]);
        setProducts(productList);
        setFavoriteIds(new Set(favorites.map((product) => product.id)));
      } catch {
        setError("Не удалось загрузить объявления");
      } finally {
        setIsLoading(false);
      }
    }, 280);
    return () => window.clearTimeout(timeout);
  }, [query, condition]);

  return (
    <main className="home-page">
      <header className="home-header">
        <div>
          <span className="eyebrow">Добро пожаловать, {telegramUser.first_name}</span>
          <h1>Что ищем сегодня?</h1>
        </div>
        {telegramUser.photo_url ? (
          <img className="avatar" src={telegramUser.photo_url} alt="" />
        ) : (
          <div className="avatar avatar-fallback">{telegramUser.first_name.slice(0, 1)}</div>
        )}
      </header>

      <div className="search-box">
        <span aria-hidden="true"><Search /></span>
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Куртка, кеды, винтаж…"
          autoComplete="off"
        />
        {query && <button onClick={() => setQuery("")} aria-label="Очистить поиск"><X aria-hidden="true" /></button>}
      </div>

      <div className="filter-strip">
        {conditionFilters.map((filter) => (
          <button
            key={filter.value}
            className={condition === filter.value ? "active" : ""}
            onClick={() => setCondition(filter.value)}
          >{filter.label}</button>
        ))}
      </div>

      <section className="catalog-section">
        <div className="section-heading">
          <h2>{query ? `Результаты «${query}»` : "Свежие находки"}</h2>
          {!isLoading && <span>{products.length}</span>}
        </div>

        {isLoading ? (
          <div className="product-grid" aria-label="Загрузка">
            {Array.from({ length: 6 }).map((_, index) => <div className="product-skeleton" key={index} />)}
          </div>
        ) : error ? (
          <div className="empty-state error-text">{error}</div>
        ) : products.length ? (
          <div className="product-grid">
            {products.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                isFavorite={favoriteIds.has(product.id)}
                onFavoriteChange={(id, value) => setFavoriteIds((current) => {
                  const next = new Set(current);
                  if (value) next.add(id); else next.delete(id);
                  return next;
                })}
              />
            ))}
          </div>
        ) : (
          <div className="empty-state"><span><SearchX aria-hidden="true" /></span><b>Ничего не нашли</b><p>Попробуйте изменить запрос или состояние вещи.</p></div>
        )}
      </section>
    </main>
  );
}
