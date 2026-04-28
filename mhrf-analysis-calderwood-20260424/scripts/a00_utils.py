"""
Utility functions: logistic regression, AUC, train/test split, k-modes
Implemented from scratch using numpy only.
"""
import numpy as np
import pandas as pd

# ── Train/Test Split ──────────────────────────────────────────────────
def train_test_split(X, y, test_size=0.3, random_state=42):
    np.random.seed(random_state)
    n = len(y)
    idx = np.random.permutation(n)
    split = int(n * (1 - test_size))
    train_idx, test_idx = idx[:split], idx[split:]
    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]

# ── Logistic Regression (gradient descent) ────────────────────────────
def sigmoid(z):
    z = np.clip(z, -500, 500)
    return 1.0 / (1.0 + np.exp(-z))

def logistic_regression_fit(X, y, lr=0.01, max_iter=10000, tol=1e-7, l2=0.01):
    """Fit logistic regression with L2 regularization via gradient descent."""
    n, p = X.shape
    # Add intercept
    X_b = np.column_stack([np.ones(n), X])
    w = np.zeros(X_b.shape[1])

    for i in range(max_iter):
        z = X_b @ w
        pred = sigmoid(z)
        # Gradient with L2 regularization (don't regularize intercept)
        grad = X_b.T @ (pred - y) / n
        grad[1:] += l2 * w[1:]
        w -= lr * grad
        if np.max(np.abs(grad)) < tol:
            break

    return w  # w[0] is intercept, w[1:] are coefficients

def logistic_regression_predict_proba(X, w):
    n = X.shape[0]
    X_b = np.column_stack([np.ones(n), X])
    return sigmoid(X_b @ w)

def logistic_regression_coefficients(X, y, feature_names, lr=0.01, max_iter=15000, l2=0.01):
    """Fit and return coefficients with standard errors via bootstrap."""
    w = logistic_regression_fit(X, y, lr=lr, max_iter=max_iter, l2=l2)

    # Bootstrap for standard errors and p-values
    n_boot = 500
    boot_coefs = []
    n = len(y)
    for _ in range(n_boot):
        idx = np.random.choice(n, n, replace=True)
        w_b = logistic_regression_fit(X[idx], y[idx], lr=lr, max_iter=5000, l2=l2)
        boot_coefs.append(w_b[1:])  # Exclude intercept

    boot_coefs = np.array(boot_coefs)
    se = boot_coefs.std(axis=0)
    coefs = w[1:]
    z_scores = coefs / (se + 1e-10)
    # Two-tailed p-value approximation using normal distribution
    p_values = 2 * (1 - _norm_cdf(np.abs(z_scores)))

    results = pd.DataFrame({
        'feature': feature_names,
        'coefficient': coefs,
        'std_error': se,
        'z_score': z_scores,
        'p_value': p_values,
        'significant': p_values < 0.05
    }).sort_values('coefficient', ascending=False)

    return results, w

def _norm_cdf(x):
    """Standard normal CDF approximation."""
    return 0.5 * (1 + np.vectorize(_erf)(x / np.sqrt(2)))

def _erf(x):
    """Error function approximation (Abramowitz and Stegun)."""
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    sign = np.sign(x)
    x = np.abs(x)
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * np.exp(-x * x)
    return sign * y

# ── AUC/ROC ───────────────────────────────────────────────────────────
def roc_curve(y_true, y_score, n_thresholds=200):
    thresholds = np.linspace(1, 0, n_thresholds)
    tpr_list, fpr_list = [], []
    for t in thresholds:
        y_pred = (y_score >= t).astype(int)
        tp = np.sum((y_pred == 1) & (y_true == 1))
        fp = np.sum((y_pred == 1) & (y_true == 0))
        fn = np.sum((y_pred == 0) & (y_true == 1))
        tn = np.sum((y_pred == 0) & (y_true == 0))
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        tpr_list.append(tpr)
        fpr_list.append(fpr)
    return np.array(fpr_list), np.array(tpr_list), thresholds

def auc_score(y_true, y_score):
    fpr, tpr, _ = roc_curve(y_true, y_score)
    # Trapezoidal rule
    return np.trapz(tpr, fpr)

# ── Chi-Square Test ───────────────────────────────────────────────────
def chi_square_test(observed_table):
    """Chi-square test of independence on a contingency table (numpy array)."""
    row_totals = observed_table.sum(axis=1, keepdims=True)
    col_totals = observed_table.sum(axis=0, keepdims=True)
    total = observed_table.sum()
    expected = row_totals * col_totals / total
    chi2 = np.sum((observed_table - expected) ** 2 / (expected + 1e-10))
    df = (observed_table.shape[0] - 1) * (observed_table.shape[1] - 1)
    # p-value approximation using chi-square CDF
    p_value = 1 - _chi2_cdf(chi2, df)
    return chi2, p_value, df

def _chi2_cdf(x, k):
    """Chi-square CDF approximation using Wilson-Hilferty."""
    if k <= 0: return 0.0
    z = ((x / k) ** (1/3) - (1 - 2/(9*k))) / np.sqrt(2/(9*k))
    return float(_norm_cdf(z))

# ── K-Modes Clustering ────────────────────────────────────────────────
def hamming_distance(a, b):
    return np.sum(a != b, axis=1)

def kmodes_fit(X, k=3, max_iter=100, n_init=10, random_state=42):
    """K-modes clustering for categorical/binary data."""
    np.random.seed(random_state)
    n, p = X.shape
    best_labels = None
    best_cost = np.inf

    for init in range(n_init):
        # Random initialization
        idx = np.random.choice(n, k, replace=False)
        centroids = X[idx].copy()

        for _ in range(max_iter):
            # Assign clusters
            distances = np.array([hamming_distance(X, centroids[j]) for j in range(k)]).T
            labels = np.argmin(distances, axis=1)

            # Update centroids (mode of each cluster)
            new_centroids = np.zeros_like(centroids)
            for j in range(k):
                mask = labels == j
                if mask.sum() > 0:
                    # Mode: most frequent value per column
                    cluster_data = X[mask]
                    for col in range(p):
                        vals, counts = np.unique(cluster_data[:, col], return_counts=True)
                        new_centroids[j, col] = vals[np.argmax(counts)]
                else:
                    new_centroids[j] = centroids[j]

            if np.array_equal(new_centroids, centroids):
                break
            centroids = new_centroids

        cost = sum(hamming_distance(X[labels == j], centroids[j]).sum() for j in range(k))
        if cost < best_cost:
            best_cost = cost
            best_labels = labels.copy()
            best_centroids = centroids.copy()

    return best_labels, best_centroids, best_cost

# ── Standardization ──────────────────────────────────────────────────
def standardize(X):
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd[sd == 0] = 1
    return (X - mu) / sd, mu, sd
