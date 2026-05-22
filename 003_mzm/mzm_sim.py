import meep as mp
import matplotlib.pyplot as plt
import numpy as np

resolution = 20

Si = mp.Medium(index=3.48)
SiO2 = mp.Medium(index=1.44)

sx = 30
sy = 15
w = 0.5 # waveguide width
L = 10 # arm length
gap = 2.0 # distance bw two arms

def make_mzm(delta_n=0.0):
    """
    delta_n: Applying voltage makes refractive index changes"""

    # modulated material
    Si_mod = mp.Medium(index=3.48 + delta_n)

    geometry = [
        # input waveguide
        mp.Block(
            size=mp.Vector3(sx/2 - L/2, w, mp.inf),
            center=mp.Vector3(-(L/2 + sx/4), 0, 0),
            material=Si
        ),
        # upper arm
        mp.Block(
            size=mp.Vector3(L, w, mp.inf),
            center=mp.Vector3(0, gap/2, 0),
            material=Si
        ),
        # lower arm (modulated)
        mp.Block(
           size=mp.Vector3(L, w, mp.inf),
           center=mp.Vector3(0, -gap/2, 0),
           material=Si_mod
        ),
        # output waveguide
         mp.Block(
            size=mp.Vector3(sx/2 - L/2, w, mp.inf),
            center=mp.Vector3(L/2 + sx/4, 0, 0),
            material=Si
        ),
    ]
    return geometry

# Compare two states
# 1. no modulation (delta_n = 0)
# 2. with modulation (delta_n = 0.01)

results = {}

for delta_n, label in [(0.0, 'no_mod'), (0.01, 'with_md')]:
    sim = mp.Simulation(
        cell_size=mp.Vector3(sx, sy),
        boundary_layers=[mp.PML(1.0)],
        geometry=make_mzm(delta_n),
        sources=[
            mp.Source(
                mp.GaussianSource(frequency=1/1.55, fwidth=0.2),
                component=mp.Ez,
                center=mp.Vector3(-sx/2 + 1, 0),
                size=mp.Vector3(0, w*2)
            )
        ],
        resolution=resolution,
        default_material=SiO2
    )

    mon = sim.add_flux(
        1/1.55, 0.2, 50,
        mp.FluxRegion(
            center=mp.Vector3(sx/2 - 2, 0),
            size=mp.Vector3(0, w*2)
        )
    )

    sim.run(until=400)

    freqs = mp.get_flux_freqs(mon)
    flux = mp.get_fluxes(mon)
    wavelengths = [1/f for f in freqs]
    results[label] = (wavelengths, flux)

    ez_data = sim.get_array(
        center=mp.Vector3(),
        size=mp.Vector3(sx, sy),
        component=mp.Ez
    )

    plt.figure(figsize=(12, 4))
    plt.imshow(ez_data.T, interpolation='bilinear',
               cmap='seismic', origin='lower')
    plt.colorbar(label='Ez field')
    plt.title(f'MZM - {label}')
    plt.tight_layout()
    plt.savefig(f'mzm_{label}.png', dpi=150)
    plt.close()

    # Comparison
    plt.figure(figsize=(10, 5))
    for label, (w1, f1) in results.items():
        plt.plot(w1, f1, label=label, linewidth=1.5)
    plt.xlabel('Wavelength (μm)')
    plt.ylabel('Transmission (a.u.)')
    plt.title('MZM - Transmission Comparison')
    plt.legend()
    plt.tight_layout()
    plt.savefig('mzm_comparison.png', dpi=150)
    plt.show()
    print("completed!")