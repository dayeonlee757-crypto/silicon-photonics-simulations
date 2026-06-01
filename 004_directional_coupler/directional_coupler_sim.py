import meep as mp
import matplotlib.pyplot as plt
import numpy as np

resolution = 20
Si = mp.Medium(index=3.48)
SiO2 = mp.Medium(index=1.44)

sx = 24
sy = 10
w = 0.5
gap = 0.2 # distance between two waveguides
L_coup = 6.0 # coupling length
L_in = 4.0 # input waveguide length


# waveguide y center
y_top = (gap + w) / 2
y_bot = -(gap + w) / 2

geometry = [
    # upper input waveguide
    mp.Block(
        size=mp.Vector3(L_in, w, mp.inf),
        center=mp.Vector3(-sx/2 + L_in/2, y_top, 0),
        material=Si
    ),
    # upper coupling
    mp.Block(
        size=mp.Vector3(L_coup, w, mp.inf),
        center=mp.Vector3(0, y_top, 0),
        material=Si
    ),
    # upper output waveguide
    mp.Block(
        size=mp.Vector3(L_in, w, mp.inf),
        center=mp.Vector3(sx/2 - L_in/2, y_top, 0),
        material=Si
    ),
    #  bottom input waveguide
    mp.Block(
        size=mp.Vector3(L_in, w, mp.inf),
        center=mp.Vector3(-sx/2 + L_in/2, y_bot, 0),
        material=Si
    ),
    #  bottom coupling 
    mp.Block(
        size=mp.Vector3(L_coup, w, mp.inf),
        center=mp.Vector3(0, y_bot, 0),
        material=Si
    ),
    # bottom output waveguide
    mp.Block(
        size=mp.Vector3(L_in, w, mp.inf),
        center=mp.Vector3(sx/2 - L_in/2, y_bot, 0),
        material=Si
    ),

]

# only light source to upper waveguide
sources=[
    mp.Source(
        mp.GaussianSource(frequency=1/1.55, fwidth=0.1),
        component=mp.Ez,
        center=mp.Vector3(-sx/2 + 1, y_top),
        size=mp.Vector3(0, w*2)
    )
]

pml_layer = [mp.PML(1.0)]

sim = mp.Simulation(
    cell_size=mp.Vector3(sx, sy),
    boundary_layers=pml_layer,
    geometry=geometry,
    sources=sources,
    resolution=resolution,
    default_material=SiO2
)

# Output monitor
mon_top = sim.add_flux(
    1/1.55, 0.1, 50,
    mp.FluxRegion(
        center=mp.Vector3(sx/2 -2, y_top),
        size=mp.Vector3(0, w*2)
    )
)

mon_bot = sim.add_flux(
    1/1.55, 0.1, 50,
    mp.FluxRegion(
        center=mp.Vector3(sx/2 -2, y_bot),
        size=mp.Vector3(0, w*2)
    )
)

sim.run(until=400)

flux_top = mp.get_fluxes(mon_top)
flux_bot = mp.get_fluxes(mon_bot)
freqs = mp.get_flux_freqs(mon_top)
wavelength = [1/f for f in freqs]

print(f"flux_top raw: {flux_top[:3]}")
print(f"flux_bot raw: {flux_bot[:3]}")

total = [t + b for t, b in zip(flux_top, flux_bot)]
ratio_top = [t/total_ if total_ != 0 else 0
             for t, total_ in zip(flux_top, total)]
ratio_bot = [b/total_ if total_ != 0 else 0
             for b, total_ in zip(flux_bot, total)]

ez_data = sim.get_array(
    center=mp.Vector3(),
    size=mp.Vector3(sx, sy),
    component=mp.Ez
)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

ax1.imshow(ez_data.T, interpolation='bilinear',
           cmap='seismic', origin='lower',
           extent=[-sx/2, sx/2, -sy/2, sy/2])
ax1.set_title('Directional coupler - Ez field')
ax1.set_xlabel('x (μm)')
ax1.set_ylabel('y (μm)')

ax2.plot(wavelength, ratio_top, 'b-', label='Top (through)', linewidth=1.5)
ax2.plot(wavelength, ratio_bot, 'r-', label='Bottom (coupled)', linewidth=1.5)
ax2.axhline(y=0.5, color='g', linestyle='--', label='50:50')
ax2.set_xlabel('Wavelength (μm)')
ax2.set_ylabel('Power ratio')
ax2.set_title('Directional coupler - coupling ratio')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('directional_coupler.png', dpi=150)
plt.show()
print("Completed!")