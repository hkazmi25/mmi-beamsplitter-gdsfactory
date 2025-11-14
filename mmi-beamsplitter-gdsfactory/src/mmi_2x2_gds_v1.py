"""
Cleaned & optimized gdsfactory script for a parameterized 2x2 MMI beamsplitter, a measurement test circuit
(with grating couplers and bundled S-bend routing), and a DOE generator.

Notes:
 - Tested with modern gdsfactory API (>=7.x). Adjust cross_section/layer mappings for your foundry PDK.
 - Run: python mmi_2x2_gds_clean.py
 - Requirements: pip install gdsfactory klayout numpy

Outputs:
 - mmi_test_device_fixed.gds
 - mmi_doe_gds/* (DOE GDS files)

"""

import gdsfactory as gf
from gdsfactory.components import grating_coupler_elliptical_te
import numpy as np, os

# -----------------------------
# Parameterized MMI 2x2
# -----------------------------
@gf.cell
def mmi_2x2(width_mmi: float = 3.0, length_mmi: float = 30.0,
           input_width: float = 0.5, output_width: float = 0.5,
           taper_length: float = 10.0, gap_mmi: float = 0.20,
           layer=(1, 0)) -> gf.Component:

    width_taper = (width_mmi - gap_mmi) / 2  # Entry width for proper mode excitation
    pitch = gap_mmi + width_taper  # Spacing between taper centers

    c = gf.Component("MMI_2x2")

    # Input tapers (widening from narrow to entry width)
    taper_in1 = c << gf.components.taper(length=taper_length, width1=input_width, width2=width_taper, layer=layer)
    taper_in2 = c << gf.components.taper(length=taper_length, width1=input_width, width2=width_taper, layer=layer)

    taper_in1.move((0, -pitch / 2))
    taper_in2.move((0, pitch / 2))

    # MMI rectangle, centered at y=0
    mmi_rect = c << gf.components.rectangle(size=(length_mmi, width_mmi), centered=False, layer=layer)
    mmi_rect.move((taper_length, -width_mmi / 2))

    # Output tapers (narrowing from entry width to output width)
    taper_out1 = c << gf.components.taper(length=taper_length, width1=width_taper, width2=output_width, layer=layer)
    taper_out2 = c << gf.components.taper(length=taper_length, width1=width_taper, width2=output_width, layer=layer)
    taper_out1.move((length_mmi + taper_length, -pitch / 2))
    taper_out2.move((length_mmi + taper_length, pitch / 2))

    c.add_port("in1", port=taper_in1.ports["o1"])
    c.add_port("in2", port=taper_in2.ports["o1"])
    c.add_port("out1", port=taper_out1.ports["o2"])
    c.add_port("out2", port=taper_out2.ports["o2"])

    # Set info as attributes (to avoid dict overwrite error)
    c.info.width_mmi = width_mmi
    c.info.length_mmi = length_mmi
    c.info.input_width = input_width
    c.info.output_width = output_width
    c.info.taper_length = taper_length
    c.info.gap_mmi = gap_mmi
    return c

# -----------------------------
# Test circuit: fiber array + routing
# -----------------------------
@gf.cell
def test_circuit_mmi(mmi_component, fiber_pitch=127.0, gc=grating_coupler_elliptical_te):
    """
    Build a measurement test circuit: two input grating couplers, route to MMI, two output grating couplers.
    fiber_pitch: distance between fibre array channels (um), default 127um for V-groove arrays
    """
    c = gf.Component("mmi_test_circuit")
    mmi = c << mmi_component
    mmi.move((0, fiber_pitch / 2))  # Center MMI vertically for symmetry with fiber pitch

    # Create grating couplers
    gc1 = c << gc()
    gc2 = c << gc()
    gc3 = c << gc()
    gc4 = c << gc()

    # Mirror inputs to face right (toward MMI)
    gc1.mirror(p1=(0, 0), p2=(0, 1))
    gc2.mirror(p1=(0, 0), p2=(0, 1))

    # Move input GCs to the left
    gc1.move((-200, 0))
    gc2.move((-200, fiber_pitch))

    # Move output GCs to the right (default orientation faces left, toward MMI)
    gc3.move((200, 0))
    gc4.move((200, fiber_pitch))

    # Cross-section for routing
    xs_sc = gf.cross_section.strip(width=0.5, layer=(1, 0))

    # Create routes
    route1 = gf.routing.route_single(component=c, port1=gc1.ports["o1"], port2=mmi.ports["in1"], radius=10, cross_section=xs_sc)
    route2 = gf.routing.route_single(component=c, port1=gc2.ports["o1"], port2=mmi.ports["in2"], radius=10, cross_section=xs_sc)
    r_out1 = gf.routing.route_single(component=c, port1=mmi.ports["out1"], port2=gc3.ports["o1"], radius=10, cross_section=xs_sc)
    r_out2 = gf.routing.route_single(component=c, port1=mmi.ports["out2"], port2=gc4.ports["o1"], radius=10, cross_section=xs_sc)

    return c


# -----------------------------
# DOE generator
# -----------------------------
def generate_doe_gds(output_dir="mmi_doe_gds", n_grid=9):
    os.makedirs(output_dir, exist_ok=True)
    width_list = np.linspace(2.0, 4.0, int(np.sqrt(n_grid)))
    length_list = np.linspace(20.0, 40.0, int(np.sqrt(n_grid)))
    i = 0
    for w in width_list:
        for L in length_list:
            comp = mmi_2x2(width_mmi=w, length_mmi=L)
            fn = f"mmi_w{w:.2f}_L{L:.2f}.gds"
            path = os.path.join(output_dir, fn)
            comp.write_gds(path)
            print("Wrote", path)
            i += 1
    print("Total designs:", i)

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    mmi = mmi_2x2(width_mmi=3.0, length_mmi=30.0)
    tc = test_circuit_mmi(mmi)
    tc.write_gds("mmi_test_device_fixed.gds")
    print("Wrote mmi_test_device_fixed.gds")

    generate_doe_gds(n_grid=9)