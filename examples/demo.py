#!/usr/bin/env python3
"""
TernaryPhysics Demo

Demonstrates ternary neural networks and the feedback loop
without requiring kernel access.

Run: python demo.py
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class Packet:
    """Simulated packet with features."""
    size: int
    port: int
    flags: int
    interval_ms: float

    def to_features(self) -> np.ndarray:
        """Extract normalized features."""
        return np.array([
            self.size / 1500,           # Normalized by MTU
            self.port / 65535,          # Normalized port
            self.flags / 255,           # Normalized flags
            min(self.interval_ms, 1000) / 1000  # Normalized interval
        ])


class TernaryNetwork:
    """
    Ternary neural network with weights in {-1, 0, +1}.

    No floating point multiplication - just addition and subtraction.
    This is what runs in eBPF.
    """

    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        self.w1 = self._init_ternary(input_size, hidden_size)
        self.w2 = self._init_ternary(hidden_size, output_size)

    def _init_ternary(self, rows: int, cols: int) -> np.ndarray:
        """Initialize random ternary weights."""
        return np.random.choice([-1, 0, 1], size=(rows, cols))

    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        Forward pass using only addition/subtraction.

        In real eBPF, this is implemented as:
        - weight +1: add input
        - weight -1: subtract input
        - weight  0: skip (no operation)
        """
        # Scale input to integers (simulating fixed-point in BPF)
        x_int = (x * 255).astype(np.int32)

        # Layer 1: ternary matmul is just conditional add/subtract
        h = np.zeros(self.w1.shape[1], dtype=np.int32)
        for i in range(len(x_int)):
            for j in range(self.w1.shape[1]):
                if self.w1[i, j] == 1:
                    h[j] += x_int[i]
                elif self.w1[i, j] == -1:
                    h[j] -= x_int[i]

        # ReLU (clamp to positive)
        h = np.maximum(h, 0)

        # Layer 2
        out = np.zeros(self.w2.shape[1], dtype=np.int32)
        for i in range(len(h)):
            for j in range(self.w2.shape[1]):
                if self.w2[i, j] == 1:
                    out[j] += h[i]
                elif self.w2[i, j] == -1:
                    out[j] -= h[i]

        return out

    def predict(self, x: np.ndarray) -> int:
        """Return class prediction."""
        return int(np.argmax(self.forward(x)))

    def update_from_feedback(self, x: np.ndarray, correct_class: int, learning_rate: float = 0.1):
        """
        Simple feedback-based weight update.

        In production, this happens in userspace with full training,
        then weights are hot-swapped into BPF.
        """
        pred = self.predict(x)
        if pred != correct_class:
            # Nudge weights toward correct class (simplified)
            x_int = (x * 255).astype(np.int32)
            for i in range(len(x_int)):
                if x_int[i] > 128:  # Strong feature
                    # Strengthen connection to correct class
                    if self.w2[i % self.w2.shape[0], correct_class] == 0:
                        self.w2[i % self.w2.shape[0], correct_class] = 1
                    # Weaken connection to wrong class
                    if self.w2[i % self.w2.shape[0], pred] == 1:
                        self.w2[i % self.w2.shape[0], pred] = 0


def generate_traffic(n_packets: int, attack_ratio: float = 0.2) -> list:
    """Generate synthetic normal and attack traffic."""
    packets = []
    labels = []

    for _ in range(n_packets):
        if np.random.random() < attack_ratio:
            # Attack pattern: small packets, high port, rapid interval
            p = Packet(
                size=np.random.randint(40, 200),
                port=np.random.randint(40000, 65535),
                flags=np.random.randint(0, 64),
                interval_ms=np.random.uniform(0.1, 5)
            )
            labels.append(1)  # Attack
        else:
            # Normal traffic: varied sizes, common ports, normal intervals
            p = Packet(
                size=np.random.randint(200, 1500),
                port=np.random.choice([80, 443, 8080, 3000, 5432]),
                flags=np.random.randint(0, 32),
                interval_ms=np.random.uniform(10, 500)
            )
            labels.append(0)  # Normal
        packets.append(p)

    return packets, labels


def main():
    print("=" * 60)
    print("TernaryPhysics Demo")
    print("=" * 60)
    print()

    # 1. Show ternary weights
    print("[1] Ternary Neural Network")
    print("-" * 40)
    net = TernaryNetwork(input_size=4, hidden_size=8, output_size=2)
    print("Weight matrix (layer 1):")
    print(net.w1)
    print()
    print("Weights are only {-1, 0, +1}")
    print("No multiplication needed - just add/subtract/skip")
    print()

    # 2. Generate traffic
    print("[2] Simulated Traffic")
    print("-" * 40)
    packets, labels = generate_traffic(100, attack_ratio=0.3)
    print(f"Generated {len(packets)} packets")
    print(f"  Normal: {labels.count(0)}")
    print(f"  Attack: {labels.count(1)}")
    print()

    # 3. Initial inference (untrained)
    print("[3] Initial Classification (untrained)")
    print("-" * 40)
    correct = 0
    for p, label in zip(packets[:20], labels[:20]):
        pred = net.predict(p.to_features())
        if pred == label:
            correct += 1
    print(f"Accuracy: {correct}/20 = {correct/20*100:.0f}%")
    print("(Random weights, expect ~50%)")
    print()

    # 4. Feedback loop
    print("[4] Feedback Loop (learning)")
    print("-" * 40)
    print("Training on packet outcomes...")

    for epoch in range(5):
        for p, label in zip(packets, labels):
            net.update_from_feedback(p.to_features(), label)

        # Evaluate
        correct = sum(
            1 for p, l in zip(packets, labels)
            if net.predict(p.to_features()) == l
        )
        print(f"  Epoch {epoch+1}: {correct}/{len(packets)} = {correct/len(packets)*100:.0f}%")
    print()

    # 5. Final inference
    print("[5] Final Classification")
    print("-" * 40)
    test_packets, test_labels = generate_traffic(50, attack_ratio=0.3)
    correct = sum(
        1 for p, l in zip(test_packets, test_labels)
        if net.predict(p.to_features()) == l
    )
    print(f"Test accuracy: {correct}/{len(test_packets)} = {correct/len(test_packets)*100:.0f}%")
    print()

    # 6. Show inference speed concept
    print("[6] Why This Works in eBPF")
    print("-" * 40)
    print("Traditional NN: 32-bit float multiply-accumulate")
    print("Ternary NN:     Integer add/subtract only")
    print()
    print("BPF constraints satisfied:")
    print("  - No floating point       [check]")
    print("  - Bounded loops            [check]")
    print("  - Small stack (<512 bytes) [check]")
    print("  - Verifier-friendly        [check]")
    print()
    print("Result: Sub-microsecond inference on every packet")
    print()

    print("=" * 60)
    print("Demo complete. See simulate_traffic.py for more.")
    print("=" * 60)


if __name__ == "__main__":
    main()
