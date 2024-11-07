import os
import numpy as np
from numpy import testing as npt
from astropy.table import Table
from astropy.cosmology import FlatLambdaCDM
from astropy.io import fits
from slsim.lens import Lens
from slsim.image_simulation import (
    simulate_image,
    sharp_image,
    sharp_rgb_image,
    rgb_image_from_image_list,
    point_source_coordinate_properties,
    image_data_class,
    centered_coordinate_system,
    point_source_image_with_variability,
    point_source_image_without_variability,
    point_source_image_at_time,
    deflector_images_with_different_zeropoint,
    image_plus_poisson_noise,
    image_plus_poisson_noise_for_list_of_image,
    lens_image,
    lens_image_series,
)
import pytest


from astropy.table import Table



class TestImageSimulation(object):
    def setup_method(self):
        # path = os.path.dirname(slsim.__file__)

        path = os.path.dirname(__file__)
        module_path, _ = os.path.split(path)
        print(path, module_path)
        blue_one = Table.read(
            os.path.join(path, "TestData/blue_one_modified.fits"), format="fits"
        )
        red_one = Table.read(
            os.path.join(path, "TestData/red_one_modified.fits"), format="fits"
        )
        cosmo = FlatLambdaCDM(H0=70, Om0=0.3)

        # Load the specific FITS file
        fits_file_path = r'C:\Users\rahul\OneDrive\Documents\GitHub\Simulating_and_Predicting_Nancy_G_Roman_Telescope_Data\COSMOS_field_morphology_matching\COSMOS_23.5_training_sample\real_galaxy_images_23.5_n21.fits'
        gal_hdu = 164
        real_galaxy_image = fits.getdata(fits_file_path, ext=gal_hdu)

        # Define the parameters
        z = 0.5
        z_data = 6
        pixel_width_data = 0.1
        phi_G = 0
        mag_g = 20
        mag_i=20
        mag_r=20


        # Create the interp_source table
        source_interp = Table([
            [z],
            [real_galaxy_image], 
            [z_data], 
            [pixel_width_data], 
            [phi_G], 
            [mag_g],
            [mag_i],
            [mag_r]
        ], names=("z", "image", "z_data", "pixel_width_data", "phi_G", "mag_g", "mag_i", "mag_r"))


        self.source_dict = blue_one
        self.deflector_dict = red_one
        self.source_interp = source_interp
        while True:
            gg_lens = Lens(
                source_dict=self.source_dict,
                deflector_dict=self.deflector_dict,
                cosmo=cosmo,
            )
            if gg_lens.validity_test():
                self.gg_lens = gg_lens
                break
        self.gg_lens_interp = Lens(
                source_dict=source_interp,
                deflector_dict=self.deflector_dict,
                lens_equation_solver="lenstronomy_analytical",
                kwargs_variability={"MJD", "ps_mag_i"},  # This line will not be used in
                # the testing but at least code go through this warning message.
                cosmo=cosmo,
                light_profile="interpolated"
            )


    def test_simulate_image(self):
        image = simulate_image(
            lens_class=self.gg_lens,
            band="g",
            num_pix=100,
            add_noise=True,
            observatory="LSST",
        )
        image_interp = simulate_image(
            lens_class=self.gg_lens_interp,
            band="g",
            num_pix=100,
            add_noise=True,
            observatory="LSST",
        )
        assert len(image) == 100
        assert len(image_interp) == 100

    def test_sharp_image(self):
        image = sharp_image(
            lens_class=self.gg_lens,
            band="g",
            mag_zero_point=30,
            delta_pix=0.05,
            num_pix=100,
            with_deflector=True,
        )
        image_interp = sharp_image(
            lens_class=self.gg_lens_interp,
            band="g",
            mag_zero_point=30,
            delta_pix=0.05,
            num_pix=100,
            with_deflector=True,
        )
        assert len(image) == 100
        assert len(image_interp) == 100

    def test_sharp_rgb_image(self):
        image = sharp_rgb_image(
            lens_class=self.gg_lens,
            rgb_band_list=["r", "g", "i"],
            mag_zero_point=30,
            delta_pix=0.05,
            num_pix=100,
        )
        image_interp = sharp_rgb_image(
            lens_class=self.gg_lens_interp,
            rgb_band_list=["r", "g", "i"],
            mag_zero_point=30,
            delta_pix=0.05,
            num_pix=100,
        )
        assert len(image) == 100
        assert len(image_interp) == 100

    def test_rgb_image_from_image_list(self):
        image_g = sharp_image(
            lens_class=self.gg_lens,
            band="g",
            mag_zero_point=30,
            delta_pix=0.05,
            num_pix=100,
            with_deflector=True,
        )
        image_r = sharp_image(
            lens_class=self.gg_lens,
            band="r",
            mag_zero_point=30,
            delta_pix=0.05,
            num_pix=100,
            with_deflector=True,
        )
        image_b = sharp_image(
            lens_class=self.gg_lens,
            band="i",
            mag_zero_point=30,
            delta_pix=0.05,
            num_pix=100,
            with_deflector=True,
        )
        image_list = [image_r, image_g, image_b]
        image = rgb_image_from_image_list(image_list, 0.5)

        image_g_interp= sharp_image(
            lens_class=self.gg_lens_interp,
            band="g",
            mag_zero_point=30,
            delta_pix=0.05,
            num_pix=100,
            with_deflector=True,
        )

        image_r_interp= sharp_image(
            lens_class=self.gg_lens,
            band="r",
            mag_zero_point=30,
            delta_pix=0.05,
            num_pix=100,
            with_deflector=True,
        )

        image_b_interp= sharp_image(
            lens_class=self.gg_lens,
            band="i",
            mag_zero_point=30,
            delta_pix=0.05,
            num_pix=100,
            with_deflector=True,
        )

        image_list_interp = [image_r_interp, image_g_interp, image_b_interp]
        image_interp = rgb_image_from_image_list(image_list, 0.5)
        assert len(image) == 100
        assert len(image_interp) == 100

    def test_point_source_image_with_lens_class_with_no_point_source(self):
        transf_matrix = np.array([[0.2, 0], [0, 0.2]])
        path = os.path.dirname(__file__)

        psf_image_1 = [
            np.load(os.path.join(path, "TestData/psf_kernels_for_image_1.npy"))
        ]
        psf_kernel_single = psf_image_1[-1]

        result1 = point_source_image_at_time(
            lens_class=self.gg_lens,
            band="i",
            mag_zero_point=27,
            delta_pix=0.2,
            num_pix=101,
            psf_kernel=psf_kernel_single,
            transform_pix2angle=transf_matrix,
            time=10,
        )

        result_1_interp = point_source_image_at_time(
            lens_class=self.gg_lens_interp,
            band="i",
            mag_zero_point=27,
            delta_pix=0.2,
            num_pix=101,
            psf_kernel=psf_kernel_single,
            transform_pix2angle=transf_matrix,
            time=10,
        )

        result2 = point_source_image_without_variability(
            lens_class=self.gg_lens,
            band="i",
            mag_zero_point=27,
            delta_pix=0.2,
            num_pix=101,
            psf_kernel=psf_kernel_single,
            transform_pix2angle=transf_matrix,
        )

        result_2_interp = point_source_image_at_time(
            lens_class=self.gg_lens_interp,
            band="i",
            mag_zero_point=27,
            delta_pix=0.2,
            num_pix=101,
            psf_kernel=psf_kernel_single,
            transform_pix2angle=transf_matrix,
            time=10,
        )
        assert np.all(result1[0] == 0)
        assert np.all(result2[0] == 0)
        assert np.all(result_1_interp[0] == 0)
        assert np.all(result_2_interp[0] == 0)


@pytest.fixture
def pes_lens_instance():
    path = os.path.dirname(__file__)
    source_dict = Table.read(
        os.path.join(path, "TestData/source_dict_ps.fits"), format="fits"
    )
    deflector_dict = Table.read(
        os.path.join(path, "TestData/deflector_dict_ps.fits"), format="fits"
    )

    cosmo = FlatLambdaCDM(H0=70, Om0=0.3)
    while True:
        pes_lens = Lens(
            source_dict=source_dict,
            deflector_dict=deflector_dict,
            source_type="point_plus_extended",
            variability_model="sinusoidal",
            kwargs_variability={"amp", "freq"},
            cosmo=cosmo,
        )
        if pes_lens.validity_test():
            pes_lens = pes_lens
            break
    return pes_lens


def test_centered_coordinate_system():
    transform_matrix = np.array([[0.2, 0], [0, 0.2]])
    grid = centered_coordinate_system(101, transform_pix2angle=transform_matrix)

    npt.assert_almost_equal(grid["ra_at_xy_0"], -10, decimal=10)
    npt.assert_almost_equal(grid["dec_at_xy_0"], -10, decimal=10)
    assert np.shape(grid["transform_pix2angle"]) == np.shape(transform_matrix)


def test_image_data_class(pes_lens_instance):
    trans_matrix_1 = np.array([[0.2, 0], [0, 0.2]])
    lens_class = pes_lens_instance
    data_class = image_data_class(
        lens_class=lens_class,
        band="i",
        mag_zero_point=27,
        delta_pix=0.2,
        num_pix=101,
        transform_pix2angle=trans_matrix_1,
    )
    results = data_class._x_at_radec_0
    npt.assert_almost_equal(results, 50, decimal=10)


def test_point_source_image_properties(pes_lens_instance):
    transform_matrix = np.array([[0.2, 0], [0, 0.2]])
    lens_class = pes_lens_instance
    result = point_source_coordinate_properties(
        lens_class=lens_class,
        band="i",
        mag_zero_point=27,
        delta_pix=0.2,
        num_pix=101,
        transform_pix2angle=transform_matrix,
    )
    keys = result.keys()
    result_key = []
    for key in keys:
        result_key.append(key)

    expected_key = ["deflector_pix", "image_pix", "ra_image", "dec_image"]
    assert result_key[0] == expected_key[0]
    assert result_key[1] == expected_key[1]
    assert result_key[2] == expected_key[2]
    assert result_key[3] == expected_key[3]


def test_point_source_image_with_and_without_variability(pes_lens_instance):
    lens_class = pes_lens_instance
    transf_matrix = np.array([[0.2, 0], [0, 0.2]])
    path = os.path.dirname(__file__)

    psf_image_1 = [np.load(os.path.join(path, "TestData/psf_kernels_for_image_1.npy"))]
    psf_kernel_single = psf_image_1[-1]

    # Call the function to get the result
    result1 = point_source_image_at_time(
        lens_class=lens_class,
        band="i",
        mag_zero_point=27,
        delta_pix=0.2,
        num_pix=101,
        psf_kernel=psf_kernel_single,
        transform_pix2angle=transf_matrix,
        time=10,
    )
    result2 = point_source_image_without_variability(
        lens_class=lens_class,
        band="i",
        mag_zero_point=27,
        delta_pix=0.2,
        num_pix=101,
        psf_kernel=psf_kernel_single,
        transform_pix2angle=transf_matrix,
    )

    transform_matrix = np.array(
        [
            np.array([[0.2, 0], [0, 0.2]]),
            np.array([[0.2, 0], [0, 0.2]]),
            np.array([[0.2, 0], [0, 0.2]]),
        ]
    )
    mag_zero_points = np.array([27, 27, 27])
    t_obs = np.array([10, 20, 30])
    psf_kernels = psf_image_1[:-1]
    psf_kernels.extend([psf_image_1[-1]] * 3)
    result3 = point_source_image_with_variability(
        lens_class=lens_class,
        band="i",
        mag_zero_point=mag_zero_points,
        delta_pix=0.2,
        num_pix=101,
        psf_kernels=psf_kernels,
        transform_pix2angle=transform_matrix,
        t_obs=t_obs,
    )

    assert result1.shape[0] == 101
    assert result2.shape[0] == 101
    assert len(result3) == len(t_obs)


def test_deflector_images_with_different_zeropoint(pes_lens_instance):
    lens_class = pes_lens_instance
    mag_zero_points = np.array([27, 30])
    result_images = deflector_images_with_different_zeropoint(
        lens_class=lens_class,
        band="i",
        mag_zero_point=mag_zero_points,
        delta_pix=0.2,
        num_pix=64,
    )
    noise_image = image_plus_poisson_noise(result_images[0], exposure_time=30)
    diff_image = noise_image - result_images[0]
    exposure_time = [30] * len(result_images)
    result_list = image_plus_poisson_noise_for_list_of_image(
        result_images, exposure_time
    )
    path = os.path.dirname(__file__)

    psf_image_1 = [np.load(os.path.join(path, "TestData/psf_kernels_for_image_1.npy"))]
    psf_kernel_single = psf_image_1[-1]
    transf_matrix = np.array([[0.2, 0], [0, 0.2]])
    lens_image_result_1 = lens_image(
        lens_class=pes_lens_instance,
        band="i",
        mag_zero_point=27,
        num_pix=64,
        psf_kernel=psf_kernel_single,
        transform_pix2angle=np.array([[0.2, 0], [0, 0.2]]),
        exposure_time=30,
        t_obs=10,
    )
    lens_image_result_2 = lens_image(
        lens_class=lens_class,
        band="i",
        mag_zero_point=27,
        num_pix=64,
        psf_kernel=psf_kernel_single,
        transform_pix2angle=transf_matrix,
        exposure_time=None,
        t_obs=None,
    )

    lens_image_result_3 = lens_image_series(
        lens_class=lens_class,
        band="i",
        mag_zero_point=np.array([27, 30]),
        num_pix=64,
        psf_kernel=np.array([psf_kernel_single, psf_kernel_single]),
        transform_pix2angle=np.array([transf_matrix, transf_matrix]),
        exposure_time=np.array([30, 30]),
        t_obs=np.array([20, 30]),
    )
    lens_image_result_4 = lens_image(
        lens_class=lens_class,
        band="i",
        mag_zero_point=27,
        num_pix=64,
        psf_kernel=psf_kernel_single,
        transform_pix2angle=transf_matrix,
        exposure_time=None,
        t_obs=None,
        std_gaussian_noise=0.2,
    )
    residual = lens_image_result_4 - lens_image_result_2
    assert len(result_images) == len(mag_zero_points)
    assert len(result_list) == len(result_images)
    assert np.any(diff_image != 0)
    assert lens_image_result_1.shape[0] == 64
    assert lens_image_result_2.shape[0] == 64
    assert len(lens_image_result_3) == 2
    assert np.any(residual != 0)


if __name__ == "__main__":
    pytest.main()
