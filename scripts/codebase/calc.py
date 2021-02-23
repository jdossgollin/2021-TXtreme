"""Calculate HDD"""

import numpy as np
from scipy.optimize import minimize
from scipy.stats import genextreme as gev


def calc_hdd(tmin, tmax, base_temp):
    """Calculate heating degree days"""
    return np.maximum(base_temp - ((tmin + tmax) / 2), 0)


def optimizer(func, x0, args, disp):
    res = minimize(func, x0, args, method="Nelder-Mead")
    return res.x


def return_period(y: float, x: np.ndarray) -> float:
    """Get the return period of `val` given historical data `hist`"""

    theta = gev.fit(x, 0, loc=40, scale=10, optimizer=optimizer)
    y_cdf = gev(*theta).cdf(y)

    # do not return a value >500
    if y_cdf > 0.999:
        period = 500
    else:
        period = 1 / (1 - y_cdf)

    return period
