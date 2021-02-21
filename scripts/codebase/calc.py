"""Calculate HDD"""

import numpy as np
from scipy.stats import genextreme as gev


def calc_hdd(tmin, tmax, base_temp):
    """Calculate heating degree days"""
    return np.maximum(base_temp - ((tmin + tmax) / 2), 0)


def cold_return_period(val: float, hist: np.ndarray) -> float:
    """Get the return period of `val` given historical data `hist`"""
    c, loc, scale = gev.fit(-hist, 0, loc=0)
    return 1 - gev(c, loc, scale).cdf(-val)


def return_period(val: float, hist: np.ndarray) -> float:
    """Get the return period of `val` given historical data `hist`"""
    c, loc, scale = gev.fit(hist, loc=0)
    return 1 - gev(c, loc, scale).cdf(val)
