import {BrowserRouter as Router, Routes, Route} from "react-router-dom";
import {Dictionaries} from "./Dictionaries/Dictionaries";
import WordTrainer from "./WordTrainer/WordTrainer";
import "./App.css"
import {Menu} from "./Menu/Menu.tsx";

export default function App() {

    return (
        <Router>
            <main className={"main_container"}>
                <Routes>
                    <Route path="/" element={<Menu/>}/>
                    <Route path="/dictionaries" element={<Dictionaries/>}/>
                    <Route path="/learning" element={<WordTrainer mode="learn"/>}/>
                    <Route path="/repetition" element={<WordTrainer mode="repeat"/>}/>
                    <Route path="*" element={<Dictionaries/>}/>
                </Routes>
            </main>
        </Router>
    );
}
