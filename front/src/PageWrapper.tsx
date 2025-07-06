import {useEffect} from "react";
import "./App.css"


export default function PageWrapper({ title, children }: { title: string; children: React.ReactNode }) {
  useEffect(() => {
    document.title = title;
  }, [title]);
  return (
    <div className="p-6 rounded-2xl shadow-lg max-w-4xl mx-auto wraper-justify h100">
      <h1 className="text-2xl font-bold text-indigo-800 mb-4">{title}</h1>
      {children}
    </div>
  );
}