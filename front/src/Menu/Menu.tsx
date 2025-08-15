import {FaBook, FaGraduationCap, FaRedo} from 'react-icons/fa';
import type {JSX} from "react";
import {Link} from "react-router-dom";
import styles from "./Menu.module.css";

function NavLink({to, label, icon}: { to: string; label: string; icon: JSX.Element }) {
    return (
        <Link to={to}>
            <button className={styles.nav_link}>
                {icon}
                {label}
            </button>
        </Link>
    );
}

export function Menu() {
    return (
        <div className={styles.menu_container}>
            <div>Spaced repetition</div>
            <div className={styles.nav_just}>
                <NavLink to="/dictionaries" label="Dictionaries" icon={<FaBook/>}/>
                <NavLink to="/learning" label="Learning" icon={<FaGraduationCap/>}/>
                <NavLink to="/repetition" label="Repetition" icon={<FaRedo/>}/>
            </div>
        </div>
    )
        ;
}
