import openmdao.api as om

from aviary.constants import GRAV_ENGLISH_LBM
from aviary.variable_info.functions import add_aviary_input, add_aviary_output
from aviary.variable_info.variables import Aircraft, Mission

class StrutMass(om.ExplicitComponent):
    """
    Calculates the mass of the strut.
    """

    def setup(self):
        add_aviary_input(self, Mission.Design.GROSS_MASS, units='lbm')
        add_aviary_input(self, Aircraft.Strut.AREA, units='ft**2')
        add_aviary_input(self, Aircraft.Strut.LENGTH, units='ft')


        add_aviary_output(self, Aircraft.Strut.MASS, units='lbm')

    def setup_partials(self):
        self.declare_partials('*', '*')

    def compute(self, inputs, outputs):
        # togw = inputs[Mission.Design.GROSS_MASS] * GRAV_ENGLISH_LBM
        area = inputs[Aircraft.Strut.AREA]
        length = inputs[Aircraft.Strut.LENGTH]
        rho = 170       # density [lm/ft^3]

        strut_weight = 2 * area * length * rho
        outputs[Aircraft.Strut.MASS] = (
            strut_weight / GRAV_ENGLISH_LBM
        )

    def compute_partials(self, inputs, J):
        area = inputs[Aircraft.Strut.AREA]
        length = inputs[Aircraft.Strut.LENGTH]
        rho = 170       # density [lbm/ft^3]
        # taper_ratio = inputs[Aircraft.Canard.TAPER_RATIO]
        # scaler = inputs[Aircraft.Canard.MASS_SCALER]
        # gross_weight = inputs[Mission.Design.GROSS_MASS] * GRAV_ENGLISH_LBM

        # gross_weight_exp = gross_weight**0.2

        J[Aircraft.Strut.MASS, Aircraft.Strut.AREA] = (
                (2 * rho * length) / GRAV_ENGLISH_LBM
        )

        J[Aircraft.Strut.MASS, Aircraft.Strut.LENGTH] = (
                (2 * rho * area) / GRAV_ENGLISH_LBM
        )
