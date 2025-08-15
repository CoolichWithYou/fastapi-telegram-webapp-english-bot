import {useState, useEffect} from "react";
import PageWrapper from "../PageWrapper/PageWrapper.tsx";
import {backButton, init} from '@telegram-apps/sdk';
import {useNavigate} from "react-router-dom";
import {useTelegram} from "../context/TelegramContext.tsx";
import styles from "./Dictionaries.module.css";

interface Dictionary {
    id: number;
    title: string;
    selected: boolean;
}

const API_URL = import.meta.env.VITE_API_URL;
const defaultChatId = import.meta.env.VITE_DEFAULT_CHAT_ID;
const debug = import.meta.env.DEBUG;

export function Dictionaries() {
    const chatId = useTelegram()
    const [dictionaries, setDictionaries] = useState<Dictionary[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();


    useEffect(() => {
        const id = chatId.chatId ?? defaultChatId;
        console.log(id)
        console.log(defaultChatId)
        fetch(`${API_URL}/api/register_user/${id}`, {
            method: "POST",
        })
    }, [chatId]);

    useEffect(() => {
        if (debug == 'False') {
            init();
            if (backButton.mount.isAvailable()) {
                backButton.mount();
                backButton.isMounted();
            }

            if (backButton.show.isAvailable()) {
                backButton.show();
                backButton.isVisible();
            }

            if (backButton.onClick.isAvailable()) {
                function listener() {
                    backButton.hide()
                    backButton.unmount();
                    navigate('/')
                }

                backButton.onClick(listener);
            }
        }
    }, [navigate]);

    useEffect(() => {

        const id = chatId.chatId ?? defaultChatId;
        setLoading(true);
        fetch(`${API_URL}/api/user_dictionaries/${id}`)
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

    const toggleSelection = (dict_id: number) => {

        const id = chatId.chatId ?? defaultChatId;

        fetch(`${API_URL}/api/update_dictionary`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({chat_id: id, dict_id: dict_id}),
        })
            .then((response) => {
                if (!response.ok) throw new Error("Failed to update selection");
                return response.json();
            })
            .then(() => {
                setDictionaries((prev) =>
                    prev.map((dict) =>
                        dict.id === dict_id ? {...dict, selected: !dict.selected} : dict
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
                <p>Loading...</p>
            ) : error ? (
                <p>Error: {error}</p>
            ) : (
                <div className={styles.list}>
                    {dictionaries.map((dict) => (
                        <div key={dict.id}
                             onClick={() => toggleSelection(dict.id)}>
                            <span>{dict.title}</span>
                            {dict.selected ? <> [✓]</> : <> [ ]</>}
                        </div>
                    ))}
                </div>
            )}
        </PageWrapper>
    );
}
