from sim_pipeline.Pipelines.skypy_pipeline import SkyPyPipeline
from sim_pipeline.gg_lens import GGLens, theta_e_when_source_infinity
import numpy as np

def draw_test_area(deflector):
    """
    draw a test area around the deflector
    :param deflector: deflector dictionary
    :return: test area in arcsec^2
    """
    theta_e_infinity = theta_e_when_source_infinity(deflector)
    test_area = np.pi * (theta_e_infinity*2) ** 2
    return test_area


class GGLensPop(object):
    """
    class to perform samples of galaxy-galaxy lensing
    """

    def __init__(self, lens_type='early-type', source_type='galaxies', kwargs_lens_cut=None, kwargs_source_cut=None,
                 kwargs_mass2light=None, skypy_config=None, f_sky=0.1, cosmo=None):
        """

        :param lens_type: type of the lens
        :type lens_type: string
        :param source_type: type of the source
        :type source_type: string
        :param kwargs_selection:
        :type kwargs_selection: dict
        :param skypy_config: path to SkyPy configuration yaml file
        :type skypy_config: string
        :param f_sky: sky area (in deg^2)
        :type f_sky: float
        """
        pipeline = SkyPyPipeline(skypy_config=skypy_config, f_sky=f_sky)
        if kwargs_lens_cut is None:
            kwargs_lens_cut = {}
        if kwargs_mass2light is None:
            kwargs_mass2light = {}
        if lens_type == 'early-type':
            from sim_pipeline.Lenses.early_type_lens_galaxies import EarlyTypeLensGalaxies
            self._lens_galaxies = EarlyTypeLensGalaxies(pipeline.red_galaxies, kwargs_cut=kwargs_lens_cut,
                                                        kwargs_mass2light=kwargs_mass2light, cosmo=cosmo)
        else:
            raise ValueError('lens_type %s is not supported' % lens_type)

        if kwargs_source_cut is None:
            kwargs_source_cut = {}
        if source_type == 'galaxies':
            from sim_pipeline.Sources.galaxies import Galaxies
            self._source_galaxies = Galaxies(pipeline.blue_galaxies, kwargs_cut=kwargs_source_cut, cosmo=cosmo)
        else:
            raise ValueError('source_type %s is not supported' % source_type)
        self.cosmo = cosmo
        self.f_sky = f_sky

    def select_lens_at_random(self):
        """
        draw a random lens within the cuts of the lens and source, with possible additional cut in the lensing
        configuration.

        #TODO: make sure mass function is preserved, as well as option to draw all lenses within the cuts within the area

        :return: GGLens() instance with parameters of the deflector and lens and source light
        """
        source = self._source_galaxies.draw_galaxy()
        lens = self._lens_galaxies.draw_deflector()
        gg_lens = GGLens(deflector_dict=lens, source_dict=source, cosmo=self.cosmo)
        return gg_lens

    def get_num_lenses(self):
        return self._lens_galaxies.deflector_number()

    def get_num_sources(self):
        return self._source_galaxies.galaxies_number()

    def get_num_sources_tested(self, testarea):
        """
         To show the mean of source galaxies needed to tested within the test area.
         (later draw a normal distribution around the mean for the number of source galaxies tested);
         num_sources_tested_mean/ testarea = num_sources/ f_sky;
         testarea is in units off arcsec^2, f_sky is in units of deg^2. 1 deg^2 = 12960000 arcsec^2
         num_source_range is in Poisson distribution with mean of num_sources_tested_mean.

        """
        num_sources = self._source_galaxies.galaxies_number()
        num_sources_tested_mean = (testarea * num_sources) / (12960000 * self.f_sky)
        num_sources_range = np.random.poisson(lam=num_sources_tested_mean)
        return num_sources_range

    def draw_population(self):
        """
        return full population list of all lenses within the area
        # TODO: need to implement a version of it. (improve the algorithm)
            Draw a population of galaxy-galaxy lenses within the area.

        :return: List of GGLens instances with parameters of the deflectors and lens and source light.
        :rtype: list
        """

        # Initialize an empty list to store the GGLens instances
        gg_lens_population = []
        # Estimate the number of lensing systems
        num_lenses = self._lens_galaxies.deflector_number()
        num_sources = self._source_galaxies.galaxies_number()
#        print(num_sources_tested_mean)
#        print("num_lenses is " + str(num_lenses))
#        print("num_sources is " + str(num_sources))
#        print(np.int(num_lenses * num_sources_tested_mean))

        # Draw a population of galaxy-galaxy lenses within the area.
        for _ in range(num_lenses):
            lens = self._lens_galaxies.draw_deflector()
            test_area = draw_test_area(deflector=lens)
            num_sources_range = self.get_num_sources_tested(testarea=test_area)
            if num_sources_range > 0:
                for _ in range(num_sources_range):
                    source = self._source_galaxies.draw_galaxy()
                    gg_lens = GGLens(deflector_dict=lens, source_dict=source, cosmo=self.cosmo, test_area=test_area)
                    # Check the validity of the lens system
                    if gg_lens.validity_test():
                        gg_lens_population.append(gg_lens)
        return len(gg_lens_population)
