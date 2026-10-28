import React, { useState } from "react";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api.js";
import { MetricCards, Status, fmt, useAsync } from "./common.jsx";

const tick = (t) => t.slice(11, 16);

export default function DecisionView() {
  const [date, setDate] = useState("2026-01-15");
  const [cutoff, setCutoff] = useState(9);
  const state = useAsync(() => api.decision({ delivery_date: date, cutoff_hour_utc: cutoff }), [date, cutoff]);
  const d = state.data;
  const rows = d?.points.filter((p) => p.forecast !== null || p.actual !== null) ?? [];

  return (
    <section>
      <div className="controls">
        <label>
          Delivery day
          <input type="date" min="2026-01-01" max="2026-01-31" value={date} onChange={(e) => setDate(e.target.value)} />
        </label>
        <label>
          Decision cutoff (UTC hour on D-1)
          <input type="number" min="0" max="23" value={cutoff} onChange={(e) => setCutoff(Number(e.target.value))} />
        </label>
      </div>
      <Status state={state} />
      {d && (
        <>
          <p className="note">
            Forecast shown is the latest published on or before <b>{d.decision_deadline.replace("T", " ").slice(0, 16)} UTC</b>.
          </p>
          <div className="chart">
            <ResponsiveContainer width="100%" height={340}>
              <LineChart data={rows}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="start_time" tickFormatter={tick} minTickGap={30} />
                <YAxis unit=" MW" width={80} />
                <Tooltip
                  labelFormatter={(t) => `${t.replace("T", " ").slice(0, 16)} UTC`}
                  formatter={(v) => `${fmt(v)} MW`}
                />
                <Legend />
                <Line dataKey="forecast" name="Forecast" stroke="#2563eb" dot={false} connectNulls />
                <Line dataKey="actual" name="Actual" stroke="#16a34a" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <h3>Error for this delivery day</h3>
          <MetricCards m={d.realised_metrics} />
          <h3>Error history before this day (what you could have known)</h3>
          <MetricCards m={d.trailing_metrics} />
        </>
      )}
    </section>
  );
}
