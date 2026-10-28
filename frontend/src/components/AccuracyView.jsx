import React, { useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api.js";
import { MetricCards, Status, fmt, useAsync } from "./common.jsx";

export default function AccuracyView() {
  const [start, setStart] = useState("2026-01-01");
  const [end, setEnd] = useState("2026-01-08");
  const [horizon, setHorizon] = useState(24);
  const range = { start: `${start}T00:00:00Z`, end: `${end}T00:00:00Z` };

  const series = useAsync(() => api.series({ ...range, horizon_hours: horizon }), [start, end, horizon]);
  const metrics = useAsync(() => api.metrics({ ...range, horizon_hours: horizon }), [start, end, horizon]);
  const byHorizon = useAsync(() => api.byHorizon(), []);

  const points = series.data?.points.filter((p) => p.forecast !== null || p.actual !== null) ?? [];
  const horizonRows = byHorizon.data?.map((h) => ({ ...h, label: `${h.horizon_from}–${h.horizon_to}h` })) ?? [];

  return (
    <section>
      <div className="controls">
        <label>
          From
          <input type="date" min="2026-01-01" max="2026-01-31" value={start} onChange={(e) => setStart(e.target.value)} />
        </label>
        <label>
          To (exclusive)
          <input type="date" min="2026-01-02" max="2026-02-01" value={end} onChange={(e) => setEnd(e.target.value)} />
        </label>
        <label>
          Forecast horizon: {horizon} h
          <input type="range" min="0" max="48" step="1" value={horizon} onChange={(e) => setHorizon(Number(e.target.value))} />
        </label>
      </div>
      <p className="note">For each target time, uses the latest forecast published at least {horizon} hours earlier.</p>

      <Status state={series} />
      <div className="chart">
        <ResponsiveContainer width="100%" height={340}>
          <LineChart data={points}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="start_time" tickFormatter={(t) => t.slice(5, 10)} minTickGap={50} />
            <YAxis unit=" MW" width={80} />
            <Tooltip labelFormatter={(t) => `${t.replace("T", " ").slice(0, 16)} UTC`} formatter={(v) => `${fmt(v)} MW`} />
            <Legend />
            <Line dataKey="forecast" name="Forecast" stroke="#2563eb" dot={false} connectNulls />
            <Line dataKey="actual" name="Actual" stroke="#16a34a" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <h3>Selected period</h3>
      <Status state={metrics} />
      <MetricCards m={metrics.data?.overall} />

      <h3>Error by time of day (MAE, MW)</h3>
      <div className="chart">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={metrics.data?.by_hour ?? []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" unit="h" />
            <YAxis width={70} />
            <Tooltip formatter={(v) => `${fmt(v)} MW`} />
            <Bar dataKey="mae" name="MAE" fill="#f59e0b" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <h3>Error vs forecast lead time (whole of January)</h3>
      <p className="note">How much worse forecasts get the further ahead they are published.</p>
      <div className="chart">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={horizonRows}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="label" />
            <YAxis width={70} />
            <Tooltip formatter={(v) => `${fmt(v)} MW`} />
            <Legend />
            <Bar dataKey="mae" name="MAE" fill="#2563eb" />
            <Bar dataKey="p90_abs_error" name="P90 abs error" fill="#ef4444" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
