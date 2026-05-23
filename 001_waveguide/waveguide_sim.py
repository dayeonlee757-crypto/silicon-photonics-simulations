import meep as mp
import matplotlib.pyplot as plt
import numpy as np

resolution = 20 # pixel per micron

# waveguide geometry
Si = mp.Medium(index=3.48)
SiO2 = mp.Medium(index=1.44)

# simulation size
sx = 16
sy = 8
w = 0.5 # width of waveguide (standard)

geometry = [
    mp.Block(
        size=mp.Vector3(mp.inf, w, mp.inf),
        center=mp.Vector3(0, 0, 0),
        material=Si
    )
]

# source (wavelength = 1500nm for communication)
sources = [
    mp.Source(
        mp.GaussianSource(frequency=1/1.55, fwidth=0.1),
        component=mp.Ez,
        center=mp.Vector3(-sx/2 + 1, 0),
        size=mp.Vector3(0, w*2)
    )
]

# PML
pml_layers = [mp.PML(1.0)]

sim = mp.Simulation(
    cell_size=mp.Vector3(sx, sy),
    boundary_layers=pml_layers,
    geometry=geometry,
    sources=sources,
    resolution=resolution,
    default_material=SiO2
)

sim.run(until=400)

# visualization
ez_data = sim.get_array(center=mp.Vector3(),
                        size=mp.Vector3(sx, sy),
                        component=mp.Ez)

plt.figure(figsize=(10, 4))
plt.imshow(ez_data.T, interpolation='bilinear',
           cmap='seismic', origin='lower')
plt.colorbar(label='Ez field')
plt.title('Silicon Waveguide - Ez-field')
plt.xlabel('x (\u00b5m)')
plt.ylabel('y (\u00b5m)')
plt.tight_layout()
plt.savefig('waveguide.png', dpi=150)
plt.show()
print('Completed!')
