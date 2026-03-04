#!/usr/bin/env python3
"""
Traffic Simulation Demo

Shows the continuous learning loop:
1. Generate traffic stream
2. Model makes predictions
3. Outcomes become labels
4. Model retrains and improves

Run: python simulate_traffic.py
"""

import numpy as np
import time
from dataclasses import dataclass
from typing import Tuple


@dataclass
class PacketEvent:
    """A packet with its eventual outcome."""
    features: np.ndarray
    true_label: int  # Ground truth (simulated)
    timestamp: float


class TernaryModel:
    """Simplified ternary model for demo."""

    def __init__(self, n_features: int = 6):
        self.weights = np.random.choice([-1, 0, 1], size=(n_features, 2))
        self.version = 1

    def predict(self, features: np.ndarray) -> Tuple[int, int]:
        """Returns (prediction, confidence)."""
        x = (features * 255).astype(np.int32)
        scores = np.zeros(2, dtype=np.int32)
        for i, f in enumerate(x):
            for j in range(2):
                if self.weights[i, j] == 1:
                    scores[j] += f
                elif self.weights[i, j] == -1:
                    scores[j] -= f
        pred = int(np.argmax(scores))
        conf = abs(scores[pred] - scores[1-pred])
        return pred, conf

    def train(self, events: list, epochs: int = 3):
        """Train on collected events."""
        for _ in range(epochs):
            for e in events:
                pred, _ = self.predict(e.features)
                if pred != e.true_label:
                    # Simple weight adjustment
                    idx = np.argmax(e.features)
                    if self.weights[idx, e.true_label] != 1:
                        self.weights[idx, e.true_label] = min(1, self.weights[idx, e.true_label] + 1)
                    if self.weights[idx, pred] != -1:
                        self.weights[idx, pred] = max(-1, self.weights[idx, pred] - 1)
        self.version += 1


def generate_packet(attack_prob: float = 0.2) -> PacketEvent:
    """Generate a single packet event."""
    is_attack = np.random.random() < attack_prob

    if is_attack:
        features = np.array([
            np.random.uniform(0.02, 0.15),   # Small packet
            np.random.uniform(0.7, 1.0),      # High port
            np.random.uniform(0.0, 0.2),      # Low flags
            np.random.uniform(0.0, 0.01),     # Rapid interval
            np.random.uniform(0.8, 1.0),      # High entropy
            np.random.uniform(0.0, 0.3),      # Few connections
        ])
        label = 1
    else:
        features = np.array([
            np.random.uniform(0.3, 1.0),      # Normal packet size
            np.random.uniform(0.0, 0.3),      # Common ports
            np.random.uniform(0.1, 0.5),      # Normal flags
            np.random.uniform(0.1, 0.8),      # Normal interval
            np.random.uniform(0.2, 0.6),      # Normal entropy
            np.random.uniform(0.5, 1.0),      # Many connections
        ])
        label = 0

    return PacketEvent(features=features, true_label=label, timestamp=time.time())


def main():
    print("=" * 60)
    print("TernaryPhysics Traffic Simulation")
    print("=" * 60)
    print()
    print("Simulating continuous packet stream with learning loop...")
    print()

    model = TernaryModel()
    buffer = []
    stats = {"correct": 0, "total": 0, "attacks_blocked": 0, "false_positives": 0}

    # Simulate time windows
    for window in range(1, 6):
        print(f"[Window {window}] Model v{model.version}")
        print("-" * 40)

        # Generate packets for this window
        window_events = [generate_packet(attack_prob=0.25) for _ in range(100)]

        # Make predictions
        window_correct = 0
        for event in window_events:
            pred, conf = model.predict(event.features)

            if pred == event.true_label:
                window_correct += 1
                stats["correct"] += 1

            if pred == 1 and event.true_label == 1:
                stats["attacks_blocked"] += 1
            elif pred == 1 and event.true_label == 0:
                stats["false_positives"] += 1

            stats["total"] += 1

        accuracy = window_correct / len(window_events) * 100
        print(f"  Packets processed: {len(window_events)}")
        print(f"  Window accuracy:   {accuracy:.1f}%")
        print(f"  Attacks blocked:   {stats['attacks_blocked']}")
        print(f"  False positives:   {stats['false_positives']}")

        # Collect outcomes (in reality, these come from TCP resets, timeouts, etc.)
        buffer.extend(window_events)

        # Retrain if buffer is large enough
        if len(buffer) >= 200:
            print(f"  -> Training on {len(buffer)} samples...")
            model.train(buffer)
            print(f"  -> Deployed model v{model.version}")
            buffer = buffer[-50:]  # Keep recent samples

        print()

    # Final summary
    print("=" * 60)
    print("Simulation Complete")
    print("=" * 60)
    print(f"Total packets:     {stats['total']}")
    print(f"Overall accuracy:  {stats['correct']/stats['total']*100:.1f}%")
    print(f"Attacks blocked:   {stats['attacks_blocked']}")
    print(f"False positives:   {stats['false_positives']}")
    print(f"Model versions:    {model.version}")
    print()
    print("In production, this loop runs continuously:")
    print("  Packets -> Inference -> Outcomes -> Training -> Hot-swap")
    print()


if __name__ == "__main__":
    main()
