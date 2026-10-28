import math


def _percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return math.nan
    k = (len(sorted_vals) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


def compute_metrics(forecasts: list[float], actuals: list[float]) -> dict | None:
    """Error = forecast - actual (positive = over-forecast)."""
    n = len(actuals)
    if n == 0:
        return None
    errors = [f - a for f, a in zip(forecasts, actuals)]
    abs_err = sorted(abs(e) for e in errors)
    mean_actual = sum(actuals) / n
    mae = sum(abs_err) / n
    nonzero = [(abs(e) / a) for e, a in zip(errors, actuals) if a > 0]
    return {
        "n": n,
        "mae": mae,
        "rmse": math.sqrt(sum(e * e for e in errors) / n),
        "bias": sum(errors) / n,
        "mape": 100 * sum(nonzero) / len(nonzero) if nonzero else None,
        "nmae": 100 * mae / mean_actual if mean_actual else None,
        "p50_abs_error": _percentile(abs_err, 0.5),
        "p90_abs_error": _percentile(abs_err, 0.9),
        "p99_abs_error": _percentile(abs_err, 0.99),
        "max_abs_error": abs_err[-1],
    }
