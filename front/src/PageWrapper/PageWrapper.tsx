import {useEffect} from "react";
import "../App.css"
import styles from "./PageWrapper.module.css";


export default function PageWrapper({title, children}: { title: string; children: React.ReactNode }) {
    useEffect(() => {
        document.title = title;
    }, [title]);
    return (
        <div className={styles.container}>
            <h1>{title}</h1>
            <div className={styles.content_alignment}>
                {children}
            </div>
        </div>
    );
}