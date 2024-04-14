class LOSConfig:
    """Configuration class for setting parameters related to line-of-sight (LOS) effects
    and Gaussian mixture models in a simulation or analysis context.

    Attributes:
        mixgauss_gamma (bool): A flag to enable or disable gamma correction in the Gaussian
            mixture model. Default is False.
        mixgauss_means (list of float or None): The means of the Gaussian mixture components.
            If None, no means are specified. Default is None.
        mixgauss_stds (list of float or None): The standard deviations of the Gaussian mixture
            components. If None, no standard deviations are specified. Default is None.
        mixgauss_weights (list of float or None): The weights of the Gaussian mixture components.
            If None, no weights are specified. Default is None.
        los_bool (bool): A boolean flag to include or exclude line-of-sight distortions in the
            analysis. Default is True.
        nonlinear_los_bool (bool): A boolean flag to include or exclude non-linear corrections
            to line-of-sight distortions. Default is False.
        nonlinear_correction_path (str or None): The file path to the non-linear correction
            distributions stored in an H5 file. If None, no path is provided. Default is None.
        no_correction_path (str or None): The file path to the distributions without non-linear
            corrections, stored in an H5 file. If None, no path is provided. Default is None.

    Example:
        To create an instance of LOSConfig with default settings:
            config = LOSConfig()
            )
    """

    def __init__(
        self,
        los_bool=True,
        mixgauss_gamma=False,
        mixgauss_means=None,
        mixgauss_stds=None,
        mixgauss_weights=None,
        nonlinear_los_bool=False,
        nonlinear_correction_path=None,
        no_correction_path=None,
    ):
        """
        :param los_bool: Boolean to include line-of-sight distortions, default is True.
        :type los_bool: bool
        :param mixgauss_gamma: Flag to enable gamma correction for Gaussian mixtures, default is False.
        :type mixgauss_gamma: bool
        :param mixgauss_means: Means of the Gaussian mixture components, default is None.
        :type mixgauss_means: list of float or None
        :param mixgauss_stds: Standard deviations of the Gaussian mixture components, default is None.
        :type mixgauss_stds: list of float or None
        :param mixgauss_weights: Weights of the Gaussian mixture components, default is None.
        :type mixgauss_weights: list of float or None
        :param nonlinear_los_bool: Boolean to include non-linear corrections to LOS distortions, default is False.
        :type nonlinear_los_bool: bool
        :param nonlinear_correction_path: Path to the non-linear correction distributions stored in an H5 file, default is None.
        :type nonlinear_correction_path: str or None
        :param no_correction_path: Path to the no non-linear correction distributions stored in an H5 file, default is None.
        :type no_correction_path: str or None
        """

        self.mixgauss_gamma = mixgauss_gamma
        self.mixgauss_means = mixgauss_means
        self.mixgauss_stds = mixgauss_stds
        self.mixgauss_weights = mixgauss_weights
        self.los_bool = los_bool
        self.nonlinear_los_bool = nonlinear_los_bool
        self.nonlinear_correction_path = nonlinear_correction_path
        self.no_correction_path = no_correction_path
