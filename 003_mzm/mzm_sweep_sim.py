import meep as mp
import matplotlib.pyplot as plt
import numpy as np

resolution = 20

Si = mp.Medium(index=3.48)
SiO2 = mp.Medium(index=1.44)

sx = 30
sy = 15
w = 0.5
L = 10.0
gap = 2.0

def run_mzm(delta_n):
    Si_mod = mp.Medium(index=3.48 + delta_n)

    geometry = [
        mp.Block(
            size=mp.Vector3(sx/2 - L/2, w, mp.inf),
            center=mp.Vector3(-(L/2 + sx/4), 0, 0),
            material=Si
        ),
        mp.Block(
            size=mp.Vector3(L, w, mp.inf),
            center=mp.Vector3(0, gap/2, 0),
            material=Si
        ),
        mp.Block(
            size=mp.Vector3(L, w, mp.inf),
            center=mp.Vector3(0, -gap/2, 0),
            material=Si_mod
        ),
        mp.Block(
            size=mp.Vector3(sx/2 - L/2, w, mp.inf),
            center=mp.Vector3(L/2 + sx/4, 0, 0),
            material=Si
        ),
    ]

    sim = mp.Simulation(
    cell_size=mp.Vector3(sx, sy),
    boundary_layers=[mp.PML(1.0)],
    geometry=geometry,
    sources=[
        mp.Source(
            mp.GaussianSource(frequency=1/1.55, fwidth=0.01),
            component=mp.Ez,
            center=mp.Vector3(-sx/2 + 1, 0),
            size=mp.Vector3(0, w*2)
        )
    ],
    resolution=resolution,
    default_material=SiO2
    )

    mon = sim.add_flux(
        1/1.55, 0.01, 1,
        mp.FluxRegion(
            center=mp.Vector3(sx/2 - 2, 0),
            size=mp.Vector3(0, w*2)
        )
    )

    sim.run(until=400)

    flux = mp.get_fluxes(mon)
    return flux[0]

# Sweeping
delta_n_values = np.linspace(0, 0.1, 20)
transmissions = []

print("Start sweeping..")
for i, dn in enumerate(delta_n_values):
    print(f"Processing: {i+1}/20 (delta_n = {dn:.4f})")
    t = run_mzm(dn)
    transmissions.append(t)

# Normalization
transmissions = np.array(transmissions)
transmissions_norm = transmissions / transmissions[0]

# Extinction point
min_idx = np.argmin(transmissions_norm)
extinction_delta_n = delta_n_values[min_idx]
print(f"\nExtinction point: delta_n = {extinction_delta_n:.4f} ")

# Plotting
plt.figure(figsize=(10, 5))
plt.plot(delta_n_values, transmissions_norm, 'b-o', linewidth=1.5)
plt.axvline(x=extinction_delta_n, color='r',
            linestyle='--', label=f'Extinction point (Δn={extinction_delta_n:.4f})')
plt.xlabel('Δn (index change)')
plt.ylabel('Normalized Transmission')
plt.title('MZM - Transmission vs Index Change')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('mzm_sweep.png', dpi=150)
plt.show()
print("Completed!!")