# Ligand’s Electron Density–Driven Quantum Loop (ED-QLoop) for Molecular Dynamics

## 🔍 Problem

In most protein–ligand molecular dynamics (MD) simulations, the ligand’s atomic charges are **calculated once** before the run and remain fixed.  
In reality, a ligand’s **electron density changes dynamically** inside the binding pocket due to hydrogen bonding, metal coordination, solvent effects, and conformational changes.  
Static charges mean the protein binding site responds to an outdated electrostatic profile, leading to inaccuracies in binding dynamics and energetics.

---

## ✅ Solution: ED-QLoop

**ED-QLoop** (Electron Density–Driven Quantum Loop) is an **automated QM/MM workflow** that updates ligand charges during MD based on its **current electron density**:

1. **Select QM Region** – The ligand (or part of it) is extracted from the protein–ligand system in YASARA.
2. **QM Calculation** – ORCA performs a semi-empirical PM3 RHF calculation to obtain Mulliken charges.
3. **Charge Injection** – Updated charges are merged with atom indices and reassigned in the MM topology via YASARA macros.
4. **MD Relaxation** – A short MD run lets the protein respond to the updated ligand electrostatics.
5. **Iteration** – The cycle repeats at user-defined intervals.

This **continuous QM–MM feedback loop** ensures the protein experiences the ligand’s real-time electrostatic environment, capturing **induced fit, polarization,** and **environment-driven charge redistribution**.

---

## ⚡ How It Differs from Typical QM/MM

| Aspect | Traditional Protein–Ligand MD | ED-QLoop |
|--------|------------------------------|----------|
| Ligand charges | Fixed | Updated dynamically |
| Binding pocket response | To static field | To evolving electrostatics |
| QM integration | Manual, one-off | Automated, iterative |
| Feedback | One-way | Continuous QM↔MM loop |

---

## 📦 Requirements

- [YASARA](https://www.yasara.org/) (with macro support)
- [ORCA](https://orcaforum.cec.mpg.de/) in `$PATH`
- Python 3.x

---

## 🚀 Installation

```bash
git clone https://github.com/yourusername/ED-QLoop.git
cd ED-QLoop
pip install -r requirements.txt  # if applicable
```

▶️ Usage
bash
Copy
Edit
python qm_charge.py \
  --structure protein_ligand.pdb \
  --simulation_time 10
Arguments:

--structure : Path to the protein–ligand complex

--simulation_time : Number of QM/MM cycles

🔄 Workflow Overview
Load protein–ligand complex in YASARA

Extract ligand as QM region

ORCA → Mulliken charges

Assign charges in MM topology

MD relaxation

Repeat until simulation ends

📂 Output Files
QM.xyz, QM.inp, QM.out – QM files

qm_charge.txt – Mulliken charges

merged_qm_atom_info.txt – Charges + atom indices

.sce – YASARA scene files

📌 Use Cases
Charged/polar ligands

Metal-coordinating inhibitors

Electrostatics-driven binding pockets
