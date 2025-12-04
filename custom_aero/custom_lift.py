"""
This is a simplified example of a component that computes a weight for the
wing and horizontal tail. The calculation is nonsensical, but it shows how
a basic external subsystem an use hierarchy inputs and set new values for
parts of the weight calculation.

The wing and tail weights will replace Aviary's internally-computed values.

This examples shows that you can use the Aviary hierarchy in your component
(as we do for the wing and engine weight), but you can also use your own
local names (as we do for 'Tail'), and promote them in your builder.
"""

import openmdao.api as om
import math as math

from aviary.variable_info.variables import Aircraft


class CustomMass(om.ExplicitComponent):
    """
    A simple component that computes a wing mass as a function of the engine mass.
    These values are not representative of any existing aircraft, and the component
    is meant to demonstrate the concept of an externally calculated subsystem mass.
    """

    def setup(self):
        self.add_input(Aircraft.Wing.ASPECT_RATIO, 19.55, units='unitless')
        self.add_input(Aircraft.Design.ZERO_LIFT_DRAG_COEFF_FACTOR, 0.96, units='unitless')
        #self.add_input(Aircraft.Wing.DIHEDRAL, 2.0, units='angles')

        self.add_output(Aircraft.Wing.HIGH_LIFT_MASS_COEFFICIENT, 1.0, units='unitless')
        #self.add_output(Aircraft.Design.ZERO_LIFT_DRAG_COEFF_FACTOR, 1.0, units='unitless')

        #self.declare_partials(Aircraft.Wing.HIGH_LIFT_MASS_COEFFICIENT, Aircraft.Wing.ASPECT_RATIO, val=1.0)
        #self.declare_partials(Aircraft.Wing.HIGH_LIFT_MASS_COEFFICIENT, Aircraft.Wing.ASPECT_RATIO, val=1.0)
        #self.declare_partials(Aircraft.Wing.HIGH_LIFT_MASS_COEFFICIENT, Aircraft.Wing.SPAN, val=1.0)

    def compute(self, inputs, outputs):
        outputs[Aircraft.Wing.HIGH_LIFT_MASS_COEFFICIENT] = math.sqrt(inputs[Aircraft.Design.ZERO_LIFT_DRAG_COEFF_FACTOR]*(math.pi)*inputs[Aircraft.Wing.ASPECT_RATIO])
