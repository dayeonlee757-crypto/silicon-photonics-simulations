import meep as mp
import matplotlib.pyplot as plt
import numpy as np

resolution = 20

# materials
Si = mp.Medium(index=3.48)
SiO2 = mp.Medium(index=1.44)

# size setting
sx = 30
sy = 30
w = 0.5 # waveguide width
r = 5.0 # ring radius
gap = 0.1 # gap bw waveguide and ring

# Geometry
waveguide = mp.Block(
        size=mp.Vector3(mp.inf, w, mp.inf),
        center=mp.Vector3(0, -(r + w/2 + gap), 0),
        material=Si
)

ring = [
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
        mp.GaussianSource(frequency=1/1.55, fwidth=0.15),
        component=mp.Ez,
        center=mp.Vector3(-sx/2 + 1, -(r + w/2 + gap)),
        size=mp.Vector3(0, w*2)
    )
]

pml_layers = [mp.PML(1.0)]

# step 1: baseline (waveguide only)
print("Step 1: Baseline simulation...")
sim_empty = mp.Simulation(
    cell_size=mp.Vector3(sx, sy),
    boundary_layers=pml_layers,
    geometry=[waveguide],
    sources=sources,
    resolution=resolution,
    default_material=SiO2
)

mon_baseline = sim_empty.add_flux(
    1/1.55, 0.15, 200,
    mp.FluxRegion(
        center=mp.Vector3(sx/2 -2, -(r + w/2 + gap)),
        size=mp.Vector3(0, w*2)
    )
)

sim_empty.run(until=1500)
baseline = mp.get_fluxes(mon_baseline)

# step 2: ring resonator
print("step 2: ring resonator simulation...")
sim = mp.Simulation(
    cell_size=mp.Vector3(sx, sy),
    boundary_layers=pml_layers,
    geometry=[waveguide] + ring,
    sources=sources,
    resolution=resolution,
    default_material=SiO2
)

mon_out = sim.add_flux(
    1/1.55, 0.15, 200,
    mp.FluxRegion(
        center=mp.Vector3(sx/2 -2, -(r + w/2 + gap)),
        size=mp.Vector3(0, w*2)
    )
)

sim.run(until=1500)

# Ez field
ez_data = sim.get_array(
    center=mp.Vector3(),
    size=mp.Vector3(sx, sy),
    component=mp.Ez
)

# Results
freqs = mp.get_flux_freqs(mon_out)
flux_out = mp.get_fluxes(mon_out)
wavelengths = [1/f for f in freqs]
transmission = [o/b for o, b in zip(flux_out, baseline)]

# Ez field graph
plt.figure(figsize=(8, 8))
plt.imshow(ez_data.T, interpolation='bilinear',
           cmap='seismic', origin='lower',
           extent=[-sx/2, sx/2, -sy/2, sy/2])
plt.colorbar(label='Ez field')
plt.title('Ring Resonator - Ez field')
plt.xlabel('x (μm)')
plt.ylabel('y (μm)')
plt.tight_layout()
plt.savefig('ring_ez.png', dpi=150)
plt.show()
print("Completed!")