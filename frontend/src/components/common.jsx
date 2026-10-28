import React from "react";

export const fmt = (v, d = 0) => (v === null || v === undefined ? "–" : Number(v).toLocaleString("en-GB", { maximumFractionDigits: d }));

export function useAsync(fn, deps) {
  const [state, setState] = React.useState({ data: null, error: null, loading: true });
  React.useEffect(() => {
    let live = true;
    setState((s) => ({ ...s, loading: true, error: null }));
    fn()
      .then((data) => live && setState({ data, error: null, loading: false }))
      .catch((error) => live && setState({ data: null, error: error.message, loading: false }));
    return () => {
      live = false;
    };
  }, deps);
  return state;
}

export function MetricCards({ m }) {
  if (!m) return <p className="muted">No overlapping forecast/actual data.</p>;
  const items = [
    ["MAE", `${fmt(m.mae)} MW`],
    ["RMSE", `${fmt(m.rmse)} MW`],
    ["Bias (fcst − actual)", `${fmt(m.bias)} MW`],
    ["MAPE", `${fmt(m.mape, 1)} %`],
    ["P90 abs error", `${fmt(m.p90_abs_error)} MW`],
    ["P99 abs error", `${fmt(m.p99_abs_error)} MW`],
    ["Periods", fmt(m.n)],
  ];
  return (
    <div className="cards">
      {items.map(([k, v]) => (
        <div className="card" key={k}>
          <span>{k}</span>
          <strong>{v}</strong>
        </div>
      ))}
    </div>
  );
}

export function Status({ state }) {
  if (state.loading) return <p className="muted">Loading…</p>;
  if (state.error) return <p className="err">Error: {state.error}</p>;
  return null;
}
