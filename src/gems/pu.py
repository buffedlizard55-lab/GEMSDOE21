"""Non-negative positive–unlabeled logistic risk, with analytic gradient.

Kiryo et al. 2017, https://arxiv.org/abs/1703.00593 . No y=0 target is
constructed for uncatalogued pixels. Fixed prior and SCAR assumptions are explicit.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit


def risk_and_grad(w, xp, xu, prior=0.03, l2=0.001):
    if not 0 < prior < 1:
        raise ValueError("PU class prior must be in (0,1)")
    zp, zu = xp @ w, xu @ w
    sp, su = expit(zp), expit(zu)
    positive = prior * np.logaddexp(0, -zp).mean()
    negative = np.logaddexp(0, zu).mean() - prior * np.logaddexp(0, zp).mean()
    grad = prior * (xp.T @ (sp - 1)) / len(xp)
    if negative > 0:
        grad += (xu.T @ su) / len(xu) - prior * (xp.T @ sp) / len(xp)
    reg = 0.5 * l2 * np.dot(w[1:], w[1:])  # intercept is not regularized
    grad[1:] += l2 * w[1:]
    return float(positive + max(0, negative) + reg), grad


class NNPULogistic:
    def __init__(self, prior=0.03, l2=0.001, max_iter=150):
        self.prior, self.l2, self.max_iter = prior, l2, max_iter

    def _design(self, x):
        a = np.arcsinh(np.asarray(x, dtype=np.float64))
        z = np.clip((a - self.center) / self.scale, -8, 8)
        return np.column_stack([np.ones(len(z)), z, z * z])

    def fit(self, positive, unlabeled):
        positive, unlabeled = np.asarray(positive), np.asarray(unlabeled)
        if (
            positive.ndim != 2
            or unlabeled.ndim != 2
            or positive.shape[1] != unlabeled.shape[1]
            or len(positive) == 0
            or len(unlabeled) == 0
        ):
            raise ValueError("Need nonempty matched P and U feature matrices")
        if not np.isfinite(positive).all() or not np.isfinite(unlabeled).all():
            raise ValueError("Features must be finite")
        u = np.arcsinh(unlabeled.astype(np.float64))
        self.center = np.median(u, axis=0)
        lo, hi = np.percentile(u, [25, 75], axis=0)
        self.scale = np.maximum(hi - lo, 0.01)
        xp, xu = self._design(positive), self._design(unlabeled)
        initial = np.zeros(xp.shape[1])
        initial[0] = np.log(self.prior / (1 - self.prior))
        result = minimize(
            risk_and_grad,
            initial,
            args=(xp, xu, self.prior, self.l2),
            jac=True,
            method="L-BFGS-B",
            options={"maxiter": self.max_iter, "ftol": 1e-8},
        )
        self.coef = result.x
        self.fit_report = {
            "success": bool(result.success),
            "message": str(result.message),
            "iterations": int(result.nit),
            "risk": float(result.fun),
            "class_prior_assumption": self.prior,
            "confirmed_negative_targets": 0,
            "assumption": "SCAR/constant prior; catalogue mapping bias can violate this",
        }
        return self

    def predict(self, x):
        if not np.isfinite(x).all():
            raise ValueError("Features must be finite")
        return expit(self._design(x) @ self.coef).astype(np.float32)
