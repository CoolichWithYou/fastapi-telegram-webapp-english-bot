// Dictionaries.tsx
import {useState, useEffect} from "react";
import PageWrapper from "../PageWrapper.tsx";
import {useTelegram} from "../context/TelegramContext.tsx";
import {backButton, init} from '@telegram-apps/sdk';
import {useNavigate} from "react-router-dom";

interface Dictionary {
    id: number;
    title: string;
    selected: boolean;
}

export function Dictionaries() {
    const chatId = useTelegram()
    const [dictionaries, setDictionaries] = useState<Dictionary[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();


    useEffect(() => {
        fetch(`/api/register_user/${chatId.chatId}`, {
            method: "POST",
        })
    }, [chatId]);

    useEffect(() => {
        init();
        if (backButton.mount.isAvailable()) {
            backButton.mount();
            backButton.isMounted(); // true
        }

        if (backButton.show.isAvailable()) {
          backButton.show();
          backButton.isVisible(); // true
        }

        if (backButton.onClick.isAvailable()) {
            function listener() {
                backButton.hide()
                backButton.unmount();
                navigate('/')
            }
            backButton.onClick(listener);
        }
    }, [navigate]);

    useEffect(() => {
        if (!chatId) return;

        setLoading(true);
        fetch(`/api/user_dictionaries/${chatId.chatId}`)
            .then((response) => {
                if (!response.ok) throw new Error("Failed to fetch dictionaries");
                return response.json();
            })
            .then((data) => {
                setDictionaries(data.dicts);
                setLoading(false);
            })
            .catch((err) => {
                setError(err.message);
                setLoading(false);
            });
    }, [chatId]);

    const toggleSelection = (id: number) => {
        if (!chatId) return;

        fetch("/api/update_dictionary", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({chat_id: chatId.chatId, dict_id: id}),
        })
            .then((response) => {
                if (!response.ok) throw new Error("Failed to update selection");
                return response.json();
            })
            .then(() => {
                setDictionaries((prev) =>
                    prev.map((dict) =>
                        dict.id === id ? {...dict, selected: !dict.selected} : dict
                    )
                );
            })
            .catch((err) => {
                console.error("POST error:", err);
            });
    };

    return (
        <PageWrapper title="Dictionaries">
            {loading ? (
                <p className="text-gray-500">Loading...</p>
            ) : error ? (
                <p className="text-red-500">Error: {error}</p>
            ) : (
                <ul className="">
                    {dictionaries.map((dict) => (
                        <div className="list-item"
                             key={dict.id}
                             onClick={() => toggleSelection(dict.id)}
                        >
                            <span>{dict.title}</span>
                            {dict.selected ? <> [✓]</> : <> [ ]</>}
                        </div>
                    ))}
                </ul>
            )}
        </PageWrapper>
    );
}
