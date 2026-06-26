import { NavLink, Outlet } from "react-router-dom";
import type { TelegramUser } from "../telegram";
import type { Seller } from "../api/marketplaceApi";

export type MarketplaceContext = {
  telegramUser: TelegramUser;
  telegramId: number;
  seller: Seller | null;
  isAdmin: boolean;
};

export default function MarketplaceLayout({ context }: { context: MarketplaceContext }) {
  return (
    <div className="marketplace-layout">
      <div className="page-container"><Outlet context={context} /></div>
      <nav className="bottom-navigation" aria-label="Основная навигация">
        <NavLink to="/" end className={({ isActive }) => isActive ? "active" : ""}>
          <span className="nav-icon">⌕</span><span>Поиск</span>
        </NavLink>
        <NavLink to="/profile" className={({ isActive }) => isActive ? "active" : ""}>
          <span className="nav-icon">○</span><span>Кабинет</span>
        </NavLink>
      </nav>
    </div>
  );
}
