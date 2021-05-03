"""Calculate HDD"""

import numpy as np
from scipy.optimize import minimize
from scipy.stats import genextreme as gev


def calc_hdd(tmin, tmax, base_temp):
    """Calculate heating degree days"""
    return np.maximum(base_temp - ((tmin + tmax) / 2), 0)


def optimizer(func, x0, args, disp):
    """Define the optimization method to use when fitting the GEV"""
    res = minimize(func, x0, args, method="Nelder-Mead")
    return res.x


def return_period(y: float, x: np.ndarray) -> float:
    """
    Get the return period of `val` given historical data `hist` where
    both are block MAXIMA
    """

    # Fit GEV with initial guess
    theta = gev.fit(x, 0, loc=40, scale=10, optimizer=optimizer)

    # get the CDF of the 2021 event using pre-2021 data
    y_cdf = gev(*theta).cdf(y)

    # do not return a value >500
    if y_cdf > 0.999:
        period = 500
    else:
        period = 1 / (1 - y_cdf)

    return period


def cold_return_period(y: float, x: np.ndarray) -> float:
    """
    Get the return period of `val` given historical data `hist` where both
    are annual MINIMA rather than MAXIMA
    """
    return return_period(-y, -x)


def calc_plotposition_return_level(X, T):
    """
    Use an empirical formula for plot position rather than MLE GEV fit

    https://www.itl.nist.gov/div898/handbook/eda/section3/eda366g.htm
    https://www.engr.colostate.edu/~ramirez/ce_old/classes/cive322-Ramirez/IDF-Procedure.pdf
    """
    KT = -np.sqrt(6) / np.pi * (0.5772 + np.log(np.log(T / (T - 1))))
    Xbar = np.mean(X)
    S = np.std(X)
    return Xbar + KT * S


def calc_mle_return_level(X, T):
    """Calculate the GEV return level using MLE"""
    theta = gev.fit(
        X,
        0,  # guess for shape
        loc=40,  # guess for location
        scale=10,  # guess for scale
        optimizer=optimizer,
    )
    return gev(*theta).isf(1 / T)


def calculate_anomaly(da, groupby_type="time.month"):
    """Function to calculate anomalies from xarray docs"""
    clim = da.groupby(groupby_type).mean(dim="time")
    return da.groupby(groupby_type) - clim
