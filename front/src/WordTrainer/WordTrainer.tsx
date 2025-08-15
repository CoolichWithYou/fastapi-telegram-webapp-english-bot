import {useState, useEffect} from "react";
import PageWrapper from "../PageWrapper/PageWrapper.tsx";
import {useTelegram} from "../context/TelegramContext.tsx";
import styles from "./WordTrainer.module.css";
import {backButton, init} from "@telegram-apps/sdk";
import {useNavigate} from "react-router-dom";

interface Word {
    id: number;
    russian: string;
    english: string;
}

interface WordTrainerProps {
    mode: "learn" | "repeat";
}


const API_URL = import.meta.env.VITE_API_URL;
const defaultChatId = import.meta.env.VITE_DEFAULT_CHAT_ID;
const debug = import.meta.env.DEBUG;

export default function WordTrainer({mode}: WordTrainerProps) {
    const chatId = useTelegram()
    const [word, setWord] = useState<Word | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [revealed, setRevealed] = useState(false);
    const route = mode === "learn" ? "word_to_learn" : "word_to_review";
    const navigate = useNavigate();

    const fetchWord = () => {
        const id = chatId?.chatId ?? defaultChatId;

        setLoading(true);
        setRevealed(false);
        fetch(`${API_URL}/api/${route}/${id}`)
            .then((res) => {
                if (!res.ok) throw new Error("Failed to fetch word");
                return res.json();
            })
            .then((data) => {
                if (!data.word) {
                    setWord(null);
                    setError(null);
                } else {
                    setWord(data.word);
                    setError(null);
                }
                setLoading(false);
            })
            .catch((err) => {
                setError(err.message);
                setLoading(false);
            });
    };

    useEffect(() => {
        if (chatId) {
            fetchWord();
        }
    }, [mode, chatId]);

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
    const handleResponse = (known: boolean) => {
        if (!word) return;
        const id = chatId?.chatId ?? defaultChatId;

        fetch(`${API_URL}/api/${route}`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                word_id: word.id,
                know_the_word: known,
                chat_id: id,
            }),
        })
            .then((res) => {
                if (!res.ok) throw new Error("Failed to send result");
                return res.json();
            })
            .then(() => {
                fetchWord();
            })
            .catch((err) => {
                console.error(err);
            });
    };


    return (
        <PageWrapper title={mode === "learn" ? "Learning" : "Repetition"}>
            {loading ? (
                <p>Loading...</p>
            ) : error ? (
                <p>Error: {error}</p>
            ) : word ? (
                <div>
                    <div>
                        {mode === "learn" ? (
                            <>
                                <p>
                                    {word.english}
                                </p>
                                <p
                                    onClick={() => setRevealed(true)}
                                    className={`text-xl italic cursor-pointer transition-opacity duration-300 ${
                                        revealed ? "text-gray-700 opacity-100" : "text-gray-400 opacity-50"
                                    }`}
                                >
                                    {revealed ? word.russian : "Нажми, чтобы показать перевод"}
                                </p>
                            </>
                        ) : (
                            <>
                                <p>{word.russian}</p>
                                <p
                                    onClick={() => setRevealed(true)}
                                    className={`text-3xl font-bold cursor-pointer transition-opacity duration-300 ${
                                        revealed ? "text-indigo-800 opacity-100" : "text-gray-400 opacity-50"
                                    }`}
                                >
                                    {revealed ? word.english : "Нажми, чтобы показать слово"}
                                </p>
                            </>
                        )}
                    </div>

                    <div className={styles.knowledge_container}>
                        <button className={styles.knowledge}
                                onClick={() => handleResponse(true)}
                        >
                            Знаю
                        </button>
                        <button className={styles.knowledge}
                                onClick={() => handleResponse(false)}>
                            Не знаю
                        </button>
                    </div>
                </div>
            ) : (
                <p>
                    Нет слов для {mode === "learn" ? "изучения" : "повторения"}.
                </p>
            )}
        </PageWrapper>
    );
}
