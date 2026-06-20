import { useEffect, useState, type ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { marketplaceApi, type Seller, type User } from "./api/marketplaceApi";
import MarketplaceLayout from "./layouts/MarketplaceLayout";
import Home from "./pages/Home";
import Profile from "./pages/Profile";
import { getTelegramWebApp, initializeTelegram, type TelegramUser } from "./telegram";

export default function App() {
  const [isOutsideTelegram, setIsOutsideTelegram] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [user, setUser] = useState<User | null>(null);
  const [telegramUser, setTelegramUser] = useState<TelegramUser | null>(null);
  const [seller, setSeller] = useState<Seller | null>(null);

  useEffect(() => {
    const webApp = getTelegramWebApp();
    if (!webApp) {
      setIsOutsideTelegram(true);
      setIsLoading(false);
      return;
    }
    const cleanup = initializeTelegram(webApp);
    const launchUser = webApp.initDataUnsafe.user;
    if (!launchUser) {
      setError("Telegram не передал данные пользователя");
      setIsLoading(false);
      return cleanup;
    }
    setTelegramUser(launchUser);
    marketplaceApi.authenticate(webApp.initData)
      .then(() => Promise.all([marketplaceApi.me(), marketplaceApi.sellerMe()]))
      .then(([currentUser, currentSeller]) => {
        setUser(currentUser);
        setSeller(currentSeller);
      })
      .catch(() => setError("Не удалось подтвердить запуск через Telegram"))
      .finally(() => setIsLoading(false));
    return cleanup;
  }, []);

  if (isOutsideTelegram) {
    return <CenterMessage><span className="gate-icon">↗</span><b>Откройте внутри Telegram</b><span>Маркетплейс доступен только как Mini App.</span></CenterMessage>;
  }
  if (isLoading) return <CenterMessage><span className="loader" />Загружаем витрину…</CenterMessage>;
  if (error || !user || !telegramUser) return <CenterMessage><b>Что-то пошло не так</b><span>{error}</span></CenterMessage>;

  const context = { telegramUser, telegramId: user.telegram_id, seller };
  return (
    <Routes>
      <Route element={<MarketplaceLayout context={context} />}>
        <Route index element={<Home />} />
        <Route path="profile" element={<Profile />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function CenterMessage({ children }: { children: ReactNode }) {
  return <div className="center-message">{children}</div>;
}
