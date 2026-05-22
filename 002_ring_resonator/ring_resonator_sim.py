import meep as mp
import matplotlib.pyplot as plt
import numpy as np

resolution = 20

# Materials
Si = mp.Medium(index=3.48)
SiO2 = mp.Medium(index=1.44)

# Size setting
sx = 20
sy = 20
w = 0.5 # waveguide width
r = 3.0 # ring radius
gap = 0.2 # gap bw waveguide and ring

geometry = [
    # waveguide
    mp.Block(
        size=mp.Vector3(mp.inf, w, mp.inf),
        center=mp.Vector3(0, -(r + w/2 + gap), 0),
        material=Si
    ),
    # ring (big-small circle)
    mp.Cylinder(
        radius=r + w/2,
        height=mp.inf,
        center=mp.Vector3(0, 0, 0),
        material=Si
    ),
    mp.Cylinder(
        radius=r - w/2,
        height=mp.inf,
        center=mp.Vector3(0, 0, 0),
        material=SiO2
    ),
]


sources = [
    mp.Source(
        mp.GaussianSource(frequency=1/1.55, fwidth=0.3),
        component=mp.Ez,
        center=mp.Vector3(-sx/2 + 1, -(r + w/2 + gap)),
        size=mp.Vector3(0, w*2)
    )

]

pml_layers = [mp.PML(1.0)]

# Measurement
# Input
mon_pt_in = mp.Vector3(-sx/2 + 2, -(r + w/2 + gap))
# Output
mon_pt_out = mp.Vector3(sx/2 - 2, -(r + w/2 + gap))

sim = mp.Simulation(
    cell_size=mp.Vector3(sx, sy),
    boundary_layers=pml_layers,
    geometry=geometry,
    sources=sources,
    resolution=resolution,
    default_material=SiO2
)

# Monitor
mon_in = sim.add_flux(
    1/1.55, 0.3, 100,
    mp.FluxRegion(center=mon_pt_in, size=mp.Vector3(0, w*2))
)
mon_out = sim.add_flux(
    1/1.55, 0.3, 100,
    mp.FluxRegion(center=mon_pt_out, size=mp.Vector3(0, w*2))
)

sim.run(until=500)

# Spectrum data
freqs = mp.get_flux_freqs(mon_in)
flux_in = mp.get_fluxes(mon_in)
flux_out = mp.get_fluxes(mon_out)

wavelengths = [1/f for f in freqs]
transmission = [abs(o/i) for o, i in zip(flux_out, flux_in)]

plt.figure(figsize=(10, 5))
plt.plot(wavelengths, transmission, 'b-', linewidth=1.5)
plt.xlabel('Wavelength (μm)')
plt.ylabel('Transmission')
plt.title('Ring Resonator - Transmission Spectrum')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('transmission.png', dpi=150)
plt.show()
print("Completed!")
