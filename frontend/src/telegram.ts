export type TelegramThemeParams = Record<string, string | undefined>;

export type TelegramUser = {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
};

type TelegramWebApp = {
  initData: string;
  initDataUnsafe: { user?: TelegramUser };
  colorScheme: "light" | "dark";
  themeParams: TelegramThemeParams;
  ready: () => void;
  expand: () => void;
  onEvent: (event: "themeChanged", callback: () => void) => void;
  offEvent: (event: "themeChanged", callback: () => void) => void;
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

export function initializeTelegram(webApp: TelegramWebApp) {
  const updateTheme = () => applyTelegramTheme(webApp);
  updateTheme();
  webApp.onEvent("themeChanged", updateTheme);
  webApp.ready();
  webApp.expand();
  return () => webApp.offEvent("themeChanged", updateTheme);
}

export function openSellerChat(username: string) {
  const url = `https://t.me/${username.replace(/^@/, "")}`;
  const webApp = getTelegramWebApp();
  if (webApp?.openTelegramLink) webApp.openTelegramLink(url);
  else window.open(url, "_blank", "noopener,noreferrer");
}
