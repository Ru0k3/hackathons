"""
dj_gui.py

A Tkinter GUI for the Deutsch–Jozsa algorithm. We're doing n=3 input qubits
plus one ancilla, so 4 qubits total. You can pick a constant oracle (always 0
or always 1) or a balanced one (I'm using x0 XOR x1 XOR x2 here). The circuit
gets built, we run it on the simulator, save two pictures:
  - circuit.png   (the quantum circuit drawing)
  - result.png    (histogram of measurement counts)
The GUI shows both images and prints whether the result says CONSTANT or BALANCED.
"""

# dj_gui_3input.py  (Final version that actually works)

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import numpy as np
import matplotlib
matplotlib.use("Agg")   # don't pop up a window, we're saving to files

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram

# -----------------------------
# Make PIL resizing not explode on older versions
# -----------------------------
try:
    from PIL import Image as _Image
    RESAMPLE = _Image.Resampling.LANCZOS
except:
    RESAMPLE = Image.LANCZOS if hasattr(Image, "LANCZOS") else None


# ============================================================
#  The oracles for 3 inputs + 1 ancilla
# ============================================================

def constant_oracle(qc, value=0):
    """Just a plain constant function. If value=1, flip the ancilla qubit.
       For value=0 we do nothing, so the oracle is just an identity gate."""
    if value == 1:
        qc.x(3)    # flip the ancilla (qubit index 3)
    return qc


def balanced_oracle(qc):
    """
    Balanced oracle for 3 input bits.
    I'm using f(x) = x0 ⊕ x1 ⊕ x2, which is definitely balanced.
    Just a CNOT from each input to the ancilla. Simple enough.
    """
    qc.cx(0, 3)
    qc.cx(1, 3)
    qc.cx(2, 3)
    return qc


# ============================================================
#  Build the whole unitary circuit (no measurements yet)
# ============================================================

def build_dj_unitary(oracle_type):
    """
    Deutsch–Jozsa unitary for 3 input qubits + 1 ancilla (so 4 total).
    This is the standard setup: put ancilla in |1>, H on everything,
    apply the oracle, then H again on just the input qubits.
    """
    qc = QuantumCircuit(4)

    # ancilla: |0> -> X -> |1> -> H -> |-> state
    qc.x(3)
    qc.h([0, 1, 2, 3])   # H on all four qubits

    # Stick the oracle in the middle
    if oracle_type == "constant0":
        constant_oracle(qc, 0)
    elif oracle_type == "constant1":
        constant_oracle(qc, 1)
    elif oracle_type == "balanced":
        balanced_oracle(qc)
    else:
        raise ValueError("Unknown oracle type, buddy")

    # Final H on inputs only (q0, q1, q2)
    qc.h([0, 1, 2])

    return qc


# ============================================================
#  Simulate the unitary, get statevector, and sample counts
# ============================================================

def simulate_and_count(qc_unitary, shots=1024):
    """Given the unitary circuit, calculate the final statevector,
       marginalize over the ancilla to get probabilities for the 3 input bits,
       then sample to produce a fake measurement histogram."""
    sv = Statevector.from_instruction(qc_unitary)
    amps = sv.data
    probs = np.abs(amps)**2   # probability for each basis state

    # We only care about the three input qubits (q2 q1 q0)
    # We'll sum probabilities over the ancilla (q3) to get marginal distribution
    marg = {k: 0.0 for k in ["000","001","010","011","100","101","110","111"]}

    for idx, p in enumerate(probs):
        # Bit order in the index: q3 q2 q1 q0  (q0 is LSB)
        b0 = (idx >> 0) & 1
        b1 = (idx >> 1) & 1
        b2 = (idx >> 2) & 1

        key = f"{b2}{b1}{b0}"   # MSB first -> q2 q1 q0
        marg[key] += p

    # Normalize (should already be close to 1, but floating point)
    total = sum(marg.values())
    if total == 0:
        raise RuntimeError("Total probability is zero. Something's broken.")
    for k in marg:
        marg[k] /= total

    # Sample fake measurement counts
    keys = list(marg.keys())
    values = [marg[k] for k in keys]
    sample = np.random.multinomial(shots, values)
    counts = {k: int(v) for k, v in zip(keys, sample) if v > 0}

    return counts, marg


# ============================================================
#  Save images to disk
# ============================================================

def save_circuit_image(qc, filename="circuit.png"):
    """Draw the circuit (with measurements added so it looks nice) and save it."""
    # Qiskit drawing likes to have measurements, so we tack them on for the picture
    draw_circ = QuantumCircuit(4, 3)
    draw_circ.append(qc.to_instruction(), [0,1,2,3])
    draw_circ.measure([0,1,2], [0,1,2])

    fig = draw_circ.draw(output="mpl", fold=60)
    fig.savefig(filename, dpi=140, bbox_inches="tight")


def save_histogram(counts, filename="result.png"):
    """Plot a histogram of the measurement counts and save it."""
    fig = plot_histogram(counts)
    fig.savefig(filename, dpi=140, bbox_inches="tight")


# ============================================================
#  The main GUI class
# ============================================================

class DJ_GUI:
    def __init__(self, root):
        self.root = root
        root.title("Deutsch–Jozsa Algorithm (3 Input Qubits)")
        root.geometry("980x700")

        # Top bar with oracle selection
        top = ttk.Frame(root)
        top.pack(fill="x", padx=10, pady=8)

        ttk.Label(top, text="Select Oracle:", font=("Arial", 12)).pack(side="left")
        self.o_var = tk.StringVar(value="balanced")

        ttk.Radiobutton(top, text="Balanced (x0 ⊕ x1 ⊕ x2)",
                        variable=self.o_var, value="balanced").pack(side="left", padx=5)

        ttk.Radiobutton(top, text="Constant 0",
                        variable=self.o_var, value="constant0").pack(side="left", padx=5)

        ttk.Radiobutton(top, text="Constant 1",
                        variable=self.o_var, value="constant1").pack(side="left", padx=5)

        ttk.Button(top, text="Run", command=self.run).pack(side="left", padx=10)

        self.info = ttk.Label(top, text="")
        self.info.pack(side="left", padx=15)

        # Middle area: left for circuit image, right for histogram
        mid = ttk.Frame(root)
        mid.pack(fill="both", expand=True)

        left = ttk.LabelFrame(mid, text="Circuit")
        left.pack(side="left", expand=True, fill="both", padx=8, pady=8)
        self.circ_label = tk.Label(left)
        self.circ_label.pack(expand=True)

        right = ttk.LabelFrame(mid, text="Histogram")
        right.pack(side="left", expand=True, fill="both", padx=8, pady=8)
        self.hist_label = tk.Label(right)
        self.hist_label.pack(expand=True)

        # Bottom text box for counts and probabilities
        bottom = ttk.LabelFrame(root, text="Counts")
        bottom.pack(fill="x", padx=8, pady=8)
        self.tbox = tk.Text(bottom, height=6)
        self.tbox.pack(fill="x")

        # Keep references to the PhotoImage objects so they don't get garbage collected
        self.img_circ = None
        self.img_hist = None

    def run(self):
        """The main action: build circuit, simulate, save images, update GUI."""
        otype = self.o_var.get()
        self.info.config(text="Running...")

        try:
            qc = build_dj_unitary(otype)
            counts, probs = simulate_and_count(qc)

            save_circuit_image(qc)
            save_histogram(counts)

            # Display circuit image
            img = Image.open("circuit.png")
            img = self.resize(img, 440, 440)
            self.img_circ = ImageTk.PhotoImage(img)
            self.circ_label.config(image=self.img_circ)

            # Display histogram
            img2 = Image.open("result.png")
            img2 = self.resize(img2, 440, 440)
            self.img_hist = ImageTk.PhotoImage(img2)
            self.hist_label.config(image=self.img_hist)

            # Dump counts and probabilities into the text box
            self.tbox.delete("1.0", tk.END)
            self.tbox.insert(tk.END, "Counts (3-bit input):\n")
            for k, v in sorted(counts.items(), key=lambda x: -x[1]):
                self.tbox.insert(tk.END, f"{k}: {v}\n")

            self.tbox.insert(tk.END, "\nProbabilities:\n")
            for k in probs:
                self.tbox.insert(tk.END, f"{k}: {probs[k]:.4f}\n")

            # Tell the user what we got
            if probs.get("000",0) > 0.98:
                self.info.config(text="Result: CONSTANT")
            else:
                self.info.config(text="Result: BALANCED")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.info.config(text="Error")

    def resize(self, im, wmax, hmax):
        """Scale an image to fit within wmax x hmax, keeping aspect ratio."""
        w, h = im.size
        s = min(wmax/w, hmax/h, 1.0)
        if s < 1:
            im = im.resize((int(w*s), int(h*s)), RESAMPLE)
        return im


# ============================================================
#  Kick it off
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    DJ_GUI(root)
    root.mainloop()