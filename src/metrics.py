import numpy as np
import warnings
from functools import wraps
from sklearn.utils.validation import check_consistent_length

# ====== Decorators ======

def validate_inputs(func):
    @wraps(func)
    def wrapper(y_true, y_pred, *args, sample_weight=None, **kwargs):
        y_true = np.asanyarray(y_true, dtype='float64')
        y_pred = np.asanyarray(y_pred, dtype='float64')
        check_consistent_length(y_true, y_pred)
        if sample_weight is not None:
            sample_weight = np.asanyarray(sample_weight, dtype='float64')
            check_consistent_length(y_true, sample_weight)
        return func(y_true, y_pred, *args, sample_weight=sample_weight, **kwargs)
    return wrapper

def ignore_empty_slice_warning(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', message='Mean of empty slice', category=RuntimeWarning)
            return func(*args, **kwargs)
    return wrapper

# ====== Helper for weighted nanmean ======

def _nanweighted_mean(x, weights=None, axis=None):
    """Compute weighted mean ignoring NaNs."""
    if weights is None:
        return np.nanmean(x, axis=axis)
    mask = np.isfinite(x) & np.isfinite(weights)
    x_masked = np.where(mask, x, 0)
    w_masked = np.where(mask, weights, 0)
    wsum = np.sum(w_masked, axis=axis)
    return np.divide(np.sum(x_masked * w_masked, axis=axis), wsum, where=wsum != 0)

# ====== Metrics ======

@validate_inputs
@ignore_empty_slice_warning
def root_mean_squared_error(y_true, y_pred, *, axis=None, sample_weight=None):
    diff_sq = (y_true - y_pred) ** 2
    mse = _nanweighted_mean(diff_sq, weights=sample_weight, axis=axis)
    return np.sqrt(mse)

@validate_inputs
@ignore_empty_slice_warning
def mean_absolute_error(y_true, y_pred, *, axis=None, sample_weight=None):
    abs_err = np.abs(y_true - y_pred)
    return _nanweighted_mean(abs_err, weights=sample_weight, axis=axis)

@validate_inputs
@ignore_empty_slice_warning
def r2_score(y_true, y_pred, *, axis=None, sample_weight=None):
    mask = np.isfinite(y_true) & np.isfinite(y_pred)
    y_true = np.where(mask, y_true, np.nan)
    y_pred = np.where(mask, y_pred, np.nan)

    if sample_weight is not None:
        sample_weight = np.where(mask, sample_weight, np.nan)
        mean_y = _nanweighted_mean(y_true, weights=sample_weight, axis=axis)
        numerator = np.nansum(sample_weight * (y_true - y_pred) ** 2, axis=axis)
        denominator = np.nansum(sample_weight * (y_true - mean_y) ** 2, axis=axis)
    else:
        mean_y = np.nanmean(y_true, axis=axis, keepdims=True)
        numerator = np.nansum((y_true - y_pred) ** 2, axis=axis)
        denominator = np.nansum((y_true - mean_y) ** 2, axis=axis)

    return np.where(denominator == 0, np.nan, 1 - numerator / denominator)
