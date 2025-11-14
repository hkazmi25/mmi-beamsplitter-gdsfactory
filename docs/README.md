# 📐 Silicon Photonic 2×2 MMI Beamsplitter – GDSFactory Design

This repository contains a complete, parameterized implementation of:

✔️ A **2×2 50:50 multimode interferometer (MMI) beamsplitter**  
✔️ A **fabrication-ready test circuit** (with grating couplers + routing)  
✔️ A **Design of Experiment (DOE)** sweep generator for optimizing the splitting ratio  
✔️ All final layouts exported as **GDS** files  
✔️ Fully reproducible code using **GDSFactory**

---

# 🖼️ Layout Previews

## **MMI 2×2 Layout**

> Add your screenshot to: `docs/images/mmi_layout.png`

![MMI Layout](docs/images/mmi_layout.png)

---

## **Test Circuit Layout**

> Add your screenshot to: `docs/images/test_circuit.png`

![Test Circuit](docs/images/test_circuit.png)

## **🧱 Functionality Overview**
1. Parameterized 2×2 MMI Beamsplitter

Customizable width, length, gap, taper lengths, and port spacing

Clean geometry suitable for silicon photonics fabrication

Automatically labeled ports

2. Test Circuit for Measurement

The script automatically constructs:

4 × TE elliptical grating couplers

S-bend optical routing

127 µm spacing for fiber-array testing

Right/left-facing GCs suitable for edge alignment

3. DOE Generator

Sweeps MMI dimensions:

Width: 2.0 → 4.0 µm

Length: 20 → 40 µm

Total designs: 9

Output folder:

gds/mmi_doe_gds/
    mmi_w2.00_L20.00.gds
    mmi_w2.00_L30.00.gds
    ...


Useful for:

Splitting ratio optimization

Process variation analysis

Wavelength response studies

## **📦 Viewing Output GDS**

Open in KLayout:

klayout gds/mmi_test_device_fixed.gds &

## **📚 Requirements**

requirements.txt should contain:

gdsfactory
numpy
klayout




