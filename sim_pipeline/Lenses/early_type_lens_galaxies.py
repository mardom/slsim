import numpy as np
import numpy.random as random
from sim_pipeline.selection import galaxy_cut


class EarlyTypeLensGalaxies(object):
    """
    class describing early-type galaxies
    """
    def __init__(self, galaxy_list, kwargs_cut, kwargs_mass2light, cosmo):
        """

        :param galaxy_list: list of dictionary with galaxy parameters of early-type galaxies
         (currently supporting skypy pipelines)
        :param kwargs_cut: cuts in parameters
        :type kwargs_cut: dict
        :param kwargs_mass2light: mass-to-light relation
        :param cosmo: astropy.cosmology instance
        """
        self._galaxy_select = galaxy_cut(galaxy_list, **kwargs_cut)
        self._num_select = len(self._galaxy_select)

    def draw_deflector(self):
        """

        :return: dictionary of complete parameterization of deflector
        """

        index = random.randint(0, self._num_select - 1)
        deflector = self._galaxy_select[index]
        if 'vel_disp' not in deflector:
            stellar_mass = deflector['stellar_mass']
            vel_disp = vel_disp_from_m_star(stellar_mass)
            deflector['vel_disp'] = vel_disp
        if 'e1_light' not in deflector or 'e2_light' not in deflector:
            e1_light, e2_light, e1_mass, e2_mass = early_type_projected_eccentricity(**deflector)
            deflector['e1_light'] = e1_light
            deflector['e2_light'] = e2_light
            deflector['e1_mass'] = e1_mass
            deflector['e2_mass'] = e2_mass
        if 'n_sersic' not in deflector:
            deflector['n_sersic'] = 4  # TODO make a better estimate with scatter
        return deflector


def early_type_projected_eccentricity(ellipticity, **kwargs):
    """
    projected eccentricity of early-type galaxies as a function of other deflector parameters

    :param ellipticity: eccentricity amplitude
    :type ellipticity: float [0,1)
    :param kwargs: deflector properties
    :type kwargs: dict
    :return: e1_light, e2_light,e1_mass, e2_mass eccentricity components
    """
    e_light = ellipticity
    phi_light = np.random.uniform(0, np.pi)
    e1_light = e_light * np.cos(phi_light)
    e2_light = e_light * np.sin(phi_light)
    e_mass = 0.5 * ellipticity + np.random.normal(loc=0, scale=0.1)
    phi_mass = phi_light + np.random.normal(loc=0, scale=0.1)
    e1_mass = e_mass * np.cos(phi_mass)
    e2_mass = e_mass * np.sin(phi_mass)
    return e1_light, e2_light, e1_mass, e2_mass


def vel_disp_from_m_star(m_star):
    """
    function for calculate the velocity dispersion from the staller mass using empirical relation for
    early type galaxies

    The power-law formula is given by:

    .. math::

         V_{\mathrm{disp}} = 10^{2.32} \left( \frac{M_{\mathrm{star}}}{10^{11} M_\odot} \right)^{0.24}

    2.32,0.24 is the parameters from [1] table 2
    [1]:Auger, M. W., et al. "The Sloan Lens ACS Survey. X. Stellar, dynamical, and total mass correlations of massive
    early-type galaxies." The Astrophysical Journal 724.1 (2010): 511.

    :param m_star: stellar mass in the unit of solar mass
    :return: the velocity dispersion ("km/s")

    """
    v_disp = (np.power(10, 2.32) * np.power(m_star/1e11, 0.24))
    return v_disp
