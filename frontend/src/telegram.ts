export type TelegramThemeParams = Record<string, string | undefined>;

export type TelegramUser = {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
};

type SafeAreaInset = { top: number; right: number; bottom: number; left: number };
type TelegramEvent =
  | "themeChanged"
  | "viewportChanged"
  | "safeAreaChanged"
  | "contentSafeAreaChanged";

type TelegramWebApp = {
  initData: string;
  initDataUnsafe: { user?: TelegramUser };
  colorScheme: "light" | "dark";
  themeParams: TelegramThemeParams;
  platform?: string;
  safeAreaInset?: SafeAreaInset;
  contentSafeAreaInset?: SafeAreaInset;
  ready: () => void;
  expand: () => void;
  onEvent: (event: TelegramEvent, callback: () => void) => void;
  offEvent: (event: TelegramEvent, callback: () => void) => void;
  openTelegramLink?: (url: string) => void;
};

declare global {
  interface Window {
    Telegram?: { WebApp?: TelegramWebApp };
  }
}

const themeVariables: Record<string, string> = {
  bg_color: "--tg-bg",
  text_color: "--tg-text",
  hint_color: "--tg-hint",
  link_color: "--tg-link",
  button_color: "--tg-button",
  button_text_color: "--tg-button-text",
  secondary_bg_color: "--tg-secondary-bg",
  header_bg_color: "--tg-header-bg",
  accent_text_color: "--tg-accent",
  section_bg_color: "--tg-section-bg",
  section_separator_color: "--tg-separator",
  destructive_text_color: "--tg-destructive",
};

export function getTelegramWebApp() {
  const webApp = window.Telegram?.WebApp;
  return webApp?.initData ? webApp : null;
}

export function applyTelegramTheme(webApp: TelegramWebApp) {
  const root = document.documentElement;
  Object.entries(themeVariables).forEach(([telegramKey, cssVariable]) => {
    const value = webApp.themeParams[telegramKey];
    if (value) root.style.setProperty(cssVariable, value);
  });
  root.dataset.theme = webApp.colorScheme;
}

export function applyTelegramSafeArea(webApp: TelegramWebApp) {
  const root = document.documentElement;
  const safe = webApp.safeAreaInset;
  const content = webApp.contentSafeAreaInset;
  const androidFallback = !safe && !content && webApp.platform === "android" ? 56 : 0;
  const values = {
    top: Math.max(safe?.top ?? 0, content?.top ?? 0, androidFallback),
    right: Math.max(safe?.right ?? 0, content?.right ?? 0),
    bottom: Math.max(safe?.bottom ?? 0, content?.bottom ?? 0),
    left: Math.max(safe?.left ?? 0, content?.left ?? 0),
  };
  Object.entries(values).forEach(([side, value]) => {
    root.style.setProperty(`--app-content-safe-${side}`, `${value}px`);
  });
}

export function initializeTelegram(webApp: TelegramWebApp) {
  const updateTheme = () => applyTelegramTheme(webApp);
  const updateSafeArea = () => applyTelegramSafeArea(webApp);
  updateTheme();
  updateSafeArea();
  webApp.onEvent("themeChanged", updateTheme);
  webApp.onEvent("viewportChanged", updateSafeArea);
  webApp.onEvent("safeAreaChanged", updateSafeArea);
  webApp.onEvent("contentSafeAreaChanged", updateSafeArea);
  webApp.ready();
  webApp.expand();
  return () => {
    webApp.offEvent("themeChanged", updateTheme);
    webApp.offEvent("viewportChanged", updateSafeArea);
    webApp.offEvent("safeAreaChanged", updateSafeArea);
    webApp.offEvent("contentSafeAreaChanged", updateSafeArea);
  };
}

export function openSellerChat(username: string) {
  const url = `https://t.me/${username.replace(/^@/, "")}`;
  const webApp = getTelegramWebApp();
  if (webApp?.openTelegramLink) webApp.openTelegramLink(url);
  else window.open(url, "_blank", "noopener,noreferrer");
}
