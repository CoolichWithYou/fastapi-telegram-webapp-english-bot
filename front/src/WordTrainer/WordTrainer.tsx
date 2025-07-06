// WordTrainer.tsx
import {useState, useEffect} from "react";
import PageWrapper from "../PageWrapper.tsx";
import {useTelegram} from "../context/TelegramContext.tsx";
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

export default function WordTrainer({mode}: WordTrainerProps) {
    const chatId = useTelegram()
    const [word, setWord] = useState<Word | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [revealed, setRevealed] = useState(false);
    const navigate = useNavigate();

    const route = mode === "learn" ? "word_to_learn" : "word_to_review";

    const fetchWord = () => {
        if (!chatId) return;

        setLoading(true);
        setRevealed(false);
        fetch(`/api/${route}?chat_id=${chatId.chatId}`)
            .then((res) => {
                if (!res.ok) throw new Error("Failed to fetch word");
                return res.json();
            })
            .then((data) => {
                setWord(data.word);
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
        // refetch when mode changes
    }, [mode, chatId]);

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

    const handleResponse = (known: boolean) => {
        if (!word || !chatId) return;

        fetch(`/api/${route}`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                word_id: word.id,
                know_the_word: known,
                chat_id: chatId.chatId,
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
                <p className="text-gray-500">Loading...</p>
            ) : error ? (
                <p className="text-red-500">Error: {error}</p>
            ) : word ? (
                <div className="wrap-content">
                    <div>
                        {mode === "learn" ? (
                            <>
                                <p className="text-4xl font-extrabold text-indigo-900 mb-2">
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
                                <p className="text-2xl text-gray-800 mb-2">{word.russian}</p>
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

                    <div className="flex justify-center gap-6 flex-buttons">
                        <button
                            onClick={() => handleResponse(true)}
                            className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-7 rounded-lg shadow-md transition-transform active:scale-95"
                        >
                            Знаю
                        </button>
                        <button
                            onClick={() => handleResponse(false)}
                            className="bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-7 rounded-lg shadow-md transition-transform active:scale-95"
                        >
                            Не знаю
                        </button>
                    </div>
                </div>
            ) : (
                <p className="text-gray-500">
                    Нет слов для {mode === "learn" ? "изучения" : "повторения"}.
                </p>
            )}
        </PageWrapper>
    );
}
