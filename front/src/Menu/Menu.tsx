import { FaBook, FaGraduationCap, FaRedo } from 'react-icons/fa';
import type {JSX} from "react";
import {Link} from "react-router-dom"; // Примеры иконок

function NavLink({ to, label, icon }: { to: string; label: string; icon: JSX.Element }) {
    return (
        <Link to={to} className="flex items-center gap-2 text-lg font-medium ac">
            {icon}
            {label}
        </Link>
    );
}

export function Menu() {
    return (
        <>
            <div className={'w100 mc'}>
                <div className={"text-color"}>Spaced repetition</div>
                <div className="widvw mycont bg-cr">
                    <div className="nav-just">
                        <button className="rounded-xl shadow menu-button text-color">
                            <NavLink to="/dictionaries" label="Dictionaries" icon={<FaBook/>}/>
                        </button>
                        <button className="rounded-xl shadow menu-button text-color">
                            <NavLink to="/learning" label="Learning" icon={<FaGraduationCap/>}/>
                        </button>
                        <button className="rounded-xl shadow menu-button text-color">
                            <NavLink to="/repetition" label="Repetition" icon={<FaRedo/>}/>
                        </button>
                    </div>
                </div>
            </div>
        </>
    )
        ;
}
