import openmdao.api as om
import numpy as np

from aviary.variable_info.functions import add_aviary_input, add_aviary_output
from aviary.variable_info.variables import Aircraft

class WingPrelim(om.ExplicitComponent):
    def setup(self):
        self.add_input(Aircraft.Wing.ASPECT_RATIO, units=None)
        self.add_input(Aircraft.Wing.AREA, units="ft**2")

        self.add_output(Aircraft.Wing.SPAN, units="ft")

        self.declare_partials(of=Aircraft.Wing.SPAN,
                              wrt=[Aircraft.Wing.ASPECT_RATIO, Aircraft.Wing.AREA])

    def compute(self, inputs, outputs):
        AR = inputs[Aircraft.Wing.ASPECT_RATIO]
        S = inputs[Aircraft.Wing.AREA]
        outputs[Aircraft.Wing.SPAN] = np.sqrt(AR * S)

    def compute_partials(self, inputs, J):
        AR = inputs[Aircraft.Wing.ASPECT_RATIO]
        S = inputs[Aircraft.Wing.AREA]
        root = np.sqrt(AR * S)
        J[Aircraft.Wing.SPAN, Aircraft.Wing.ASPECT_RATIO] = 0.5 * S / root
        J[Aircraft.Wing.SPAN, Aircraft.Wing.AREA] = 0.5 * AR / root


class SBWStrutGeometry(om.ExplicitComponent):
    def setup(self):
        # Required wing geometry inputs
        self.add_input(Aircraft.Wing.SPAN, units="ft")
        self.add_input(Aircraft.Strut.ATTACHMENT_LOCATION_DIMENSIONLESS)
        self.add_input(Aircraft.Fuselage.AVG_DIAMETER, units="ft")

        # Strut shape variables
        self.add_input(Aircraft.Strut.THICKNESS_TO_CHORD)
        self.add_input(Aircraft.Strut.CHORD, units="ft")

        # Outputs — official strut variables
        self.add_output(Aircraft.Strut.ATTACHMENT_LOCATION, units="ft")
        self.add_output(Aircraft.Strut.LENGTH, units="ft")
        self.add_output(Aircraft.Strut.AREA, units="ft**2")

        self.declare_partials("*", "*", method="fd")

    def compute(self, inputs, outputs):
        span   = inputs[Aircraft.Wing.SPAN]
        eta = inputs[Aircraft.Strut.ATTACHMENT_LOCATION_DIMENSIONLESS]
        c_s = inputs[Aircraft.Strut.CHORD]
        t_c = inputs[Aircraft.Strut.THICKNESS_TO_CHORD]
        cabin_width = inputs[Aircraft.Fuselage.AVG_DIAMETER]

        # dimensional attach location
        y_attach = 0.5 * span * eta

        # placeholder vertical offset:
        # z_root = 1.0  # fuselage clearance / TBD
        # z_attach = 0.0

        # compute strut length
        length = np.sqrt(((y_attach - (cabin_width / 2)) ** 2) + ((cabin_width / 2)**2))

        # length = ((y_attach - (cabin_width / 2)) ** 2 + (z_root - z_attach) ** 2) ** 0.5

        # cross-sectional area
        area = 0.6 * c_s * (t_c * c_s)

        outputs[Aircraft.Strut.ATTACHMENT_LOCATION] = y_attach
        outputs[Aircraft.Strut.LENGTH] = length
        outputs[Aircraft.Strut.AREA] = area

class SBWWingGeometry(om.Group):
    def setup(self):
        # Add subsystems
        self.add_subsystem("span", WingPrelim(), promotes=["*"])
        self.add_subsystem("strut", SBWStrutGeometry(), promotes=["*"])

