import { useEffect, useState, type ReactNode } from "react";
import { ExternalLink } from "lucide-react";
import { Navigate, Route, Routes } from "react-router-dom";
import { marketplaceApi, type Seller, type User } from "./api/marketplaceApi";
import MarketplaceLayout from "./layouts/MarketplaceLayout";
import Home from "./pages/Home";
import Profile from "./pages/Profile";
import ProductPage from "./pages/ProductPage";
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
    const cleanup = webApp ? initializeTelegram(webApp) : undefined;

    async function bootstrap() {
      try {
        let launchUser: TelegramUser;
        if (webApp) {
          const telegramLaunchUser = webApp.initDataUnsafe.user;
          if (!telegramLaunchUser) throw new Error("Telegram did not provide user data");
          await marketplaceApi.authenticate(webApp.initData);
          launchUser = telegramLaunchUser;
        } else {
          try {
            launchUser = await marketplaceApi.devAuthenticate();
          } catch {
            setIsOutsideTelegram(true);
            return;
          }
        }

        setTelegramUser(launchUser);
        const [currentUser, currentSeller] = await Promise.all([
          marketplaceApi.me(),
          marketplaceApi.sellerMe(),
        ]);
        setUser(currentUser);
        setSeller(currentSeller);
      } catch {
        setError("Не удалось подтвердить запуск через Telegram");
      } finally {
        setIsLoading(false);
      }
    }

    void bootstrap();
    return cleanup;
  }, []);

  if (isOutsideTelegram) {
    return <CenterMessage><span className="gate-icon"><ExternalLink aria-hidden="true" /></span><b>Откройте внутри Telegram</b><span>Маркетплейс доступен только как Mini App.</span></CenterMessage>;
  }
  if (isLoading) return <CenterMessage><span className="loader" />Загружаем витрину…</CenterMessage>;
  if (error || !user || !telegramUser) return <CenterMessage><b>Что-то пошло не так</b><span>{error}</span></CenterMessage>;

  const context = {
    telegramUser,
    telegramId: user.telegram_id,
    seller,
    isAdmin: user.is_admin,
  };
  return (
    <Routes>
      <Route element={<MarketplaceLayout context={context} />}>
        <Route index element={<Home />} />
        <Route path="profile" element={<Profile />} />
        <Route path="products/:productId" element={<ProductPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function CenterMessage({ children }: { children: ReactNode }) {
  return <div className="center-message">{children}</div>;
}
