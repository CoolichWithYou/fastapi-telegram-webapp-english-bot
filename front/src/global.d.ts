interface TelegramWebApp {
  initData: string;
  initDataUnsafe?: {
    user?: {
      id: number;
      first_name?: string;
      last_name?: string;
      username?: string;
    };
    auth_date?: number;
    query_id?: string;
    [key: string]: any;
  };
  ready: () => void;
  // можно добавить другие методы и свойства, если нужно
}

interface Telegram {
  WebApp: TelegramWebApp;
}

interface Window {
  Telegram?: Telegram;
}
