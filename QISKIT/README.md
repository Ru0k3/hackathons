# Qiskit Quantum Computing Bootcamp: From Theory to Implementation

Welcome to the repository documenting my experience and projects completed during the **Qiskit Quantum Bootcamp**. This program provided an intensive deep dive into the world of quantum mechanics, gate-based circuit design, and the practical application of quantum algorithms using the Qiskit SDK.

---

## 🚀 Bootcamp Overview
The bootcamp was structured into three distinct phases designed to take a classical developer into the quantum realm.

### Phase 1: Foundations & Quantum Logic
We began with the mathematical and theoretical underpinnings of quantum computing. Key topics included:
* **Quantum Bits (Qubits):** Understanding superposition, entanglement, and the Bloch Sphere.
* **Gate Operations:** Mastering Pauli gates ($X, Y, Z$), Hadamard ($H$), and controlled gates ($CX/CNOT$).
* **Quantum Algorithms:** Theoretical study of the Deutsch–Jozsa, Grover’s, and Shor’s algorithms.
* **Applications:** Exploring how quantum computing solves problems in cryptography, material science, and optimization.

### Phase 2: Hands-on Implementation
Transitioning from theory to code, we utilized **Google Colab** and **Qiskit** to build and simulate quantum circuits.
* Implemented quantum circuits from scratch using Python.
* Analyzed probability distributions using statevector simulators.
* Explored noise models and the reality of NISQ (Noisy Intermediate-Scale Quantum) devices.

### Phase 3: The Hackathon
The program culminated in a hackathon where the goal was to pick a quantum algorithm and solve it, prove its validity, or create a functional implementation.

For my submission, I focused on the **Deutsch–Jozsa Algorithm**, developing a full-stack Python application that visualizes the quantum advantage in real-time.

---

## 🛠️ Featured Project: Deutsch–Jozsa Visualization GUI
As part of the final hackathon, I developed a Tkinter-based GUI to demonstrate the efficiency of the Deutsch–Jozsa algorithm for $n=3$ input qubits.

### Key Features:
* **Oracle Selection:** Users can toggle between **Constant** and **Balanced** oracles to see how the quantum circuit adapts.
* **Real-time Visualization:** Automatically generates and displays the quantum circuit diagram using Matplotlib.
* **Result Analysis:** Executes the algorithm on a `Statevector` simulator and plots a measurement histogram to verify the output.
* **Quantum Decision Logic:** The application interprets the results to provide a definitive "CONSTANT" or "BALANCED" verdict based on quantum interference patterns.

### Technical Stack:
* **Language:** Python
* **Quantum Framework:** Qiskit
* **GUI:** Tkinter
* **Visualization:** Matplotlib, Pillow (PIL)

---

## 📁 Repository Structure

```text
├── hands_on_sessions/      # Jupyter notebooks from the Google Colab sessions
├── hackathon_project/
│   ├── dj_gui_3input.py    # The main GUI application
│   ├── submission_ppt/     # Presentation slides for the hackathon
│   └── outputs/            # Generated circuit diagrams and histograms
└── README.md
