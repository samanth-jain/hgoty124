import React, { useState } from "react";
import DecisionView from "./components/DecisionView.jsx";
import AccuracyView from "./components/AccuracyView.jsx";

export default function App() {
  const [tab, setTab] = useState("decision");
  return (
    <div className="app">
      <header>
        <h1>Wind Forecast Monitor</h1>
        <p>UK national wind generation — Elexon FUELHH actuals vs WINDFOR forecasts, January 2026</p>
        <nav>
          <button className={tab === "decision" ? "on" : ""} onClick={() => setTab("decision")}>
            Day-ahead decision
          </button>
          <button className={tab === "accuracy" ? "on" : ""} onClick={() => setTab("accuracy")}>
            Forecast accuracy
          </button>
        </nav>
      </header>
      {tab === "decision" ? <DecisionView /> : <AccuracyView />}
    </div>
  );
}
