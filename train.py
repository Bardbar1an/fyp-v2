"""Offline gradient training of a Sugeno neuro-fuzzy network, using NumPy only."""
import argparse
from pathlib import Path
import numpy as np
from src.control import Fuzzy


def teacher(x):
    # Synthetic nonlinear expert, not optimal control or measured human data.
    e, angle = x[:, 0], x[:, 1]
    return np.column_stack((np.clip(1.15*e + 0.12*np.tanh(3*e), -0.3, 0.9),
                            np.clip(2.2*angle + 0.18*np.sin(2*angle), -1.8, 1.8)))


def train(epochs=250, seed=7, output='models/neuro_fuzzy.json'):
    rng = np.random.default_rng(seed)
    x = rng.uniform([-2, -np.pi], [2, np.pi], (5000, 2))
    y = teacher(x)
    validation = rng.uniform([-2, -np.pi], [2, np.pi], (1000, 2))
    target = teacher(validation)
    model = Fuzzy()
    params = [model.consequents, model.centers, model.log_widths]
    m, s = [np.zeros_like(p) for p in params], [np.zeros_like(p) for p in params]
    initial = float(np.mean((model.predict(validation) - target)**2))
    best_loss, best, iteration = initial, [p.copy() for p in params], 0
    for epoch in range(epochs):
        for batch in np.array_split(rng.permutation(len(x)), 20):
            weights, delta, width = model.features(x[batch])
            prediction = weights @ model.consequents
            g = (prediction - y[batch]) / len(batch)  # MSE over 2 outputs
            logits_gradient = weights * np.sum(g[:, None, :] * (model.consequents[None, :, :] - prediction[:, None, :]), axis=2)
            gradients = [weights.T @ g,
                         np.sum(logits_gradient[:, :, None] * delta / width**2, axis=0),
                         np.sum(logits_gradient[:, :, None] * (delta / width)**2, axis=0)]
            iteration += 1
            for i, (p, grad) in enumerate(zip(params, gradients)):
                m[i] = 0.9*m[i] + 0.1*grad
                s[i] = 0.999*s[i] + 0.001*grad**2
                p -= 0.003 * (m[i]/(1-0.9**iteration)) / (np.sqrt(s[i]/(1-0.999**iteration)) + 1e-8)
            np.clip(model.centers, -1.3, 1.3, out=model.centers)
            np.clip(model.log_widths, np.log(0.08), np.log(1.2), out=model.log_widths)
        loss = float(np.mean((model.predict(validation)-target)**2))
        if loss < best_loss:
            best_loss, best = loss, [p.copy() for p in params]
    for p, b in zip(params, best):
        p[:] = b
    metadata = dict(seed=seed, epochs=epochs, train_samples=len(x), validation_samples=len(validation), initial_validation_mse=initial, validation_mse=best_loss, learning='Adam on Gaussian centers, widths and zero-order Sugeno consequents', teacher='Synthetic nonlinear expert; imitation only; no claim of optimality', selection='Lowest validation MSE; benchmark trajectories not used for training')
    model.save(output, metadata)
    print(f'Saved {output}; validation MSE {initial:.6f} -> {best_loss:.6f}')
    return metadata


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--epochs', type=int, default=250)
    p.add_argument('--output', default='models/neuro_fuzzy.json')
    a = p.parse_args()
    if a.epochs < 1:
        p.error('--epochs must be positive')
    train(a.epochs, output=a.output)
