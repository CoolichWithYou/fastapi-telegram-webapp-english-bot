import { createContext, useEffect, useState, useContext } from "react";

interface TelegramContextType {
  chatId: number | null;
  isReady: boolean;
}

const TelegramContext = createContext<TelegramContextType>({
  chatId: null,
  isReady: false,
});

export const useTelegram = () => useContext(TelegramContext);

export const TelegramProvider = ({ children }: { children: React.ReactNode }) => {
  const [chatId, setChatId] = useState<number | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;

    if (!tg) {
      console.warn("Telegram WebApp not found.");
      return;
    }

    tg.ready();

    const id = tg.initDataUnsafe?.user?.id;
    if (id) {
      setChatId(id);
      setIsReady(true);
    } else {
      console.error("User not found in initDataUnsafe");
    }
  }, []);

  return (
    <TelegramContext.Provider value={{ chatId, isReady }}>
      {children}
    </TelegramContext.Provider>
  );
};