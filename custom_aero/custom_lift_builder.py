"""
Builder for a simple component that computes a new wing and horizontal tail
mass.

The CustomMass component is placed inside of a group so that we can promote
the variable "Tail" using the alias Aircraft.HorizontalTail.MASS
"""

import openmdao.api as om

from aviary.examples.external_subsystems.custom_aero.custom_aero import CustomAero
from aviary.subsystems.subsystem_builder_base import SubsystemBuilderBase
from aviary.variable_info.variables import Aircraft


class LiftDragBuilder(SubsystemBuilderBase):
    """
    Prototype of a subsystem that overrides an aviary internally computed var.

    It also provides a method to build OpenMDAO systems for the pre-mission and mission computations of the subsystem.

    Attributes
    ----------
    name : str ('wing_mass')
        object label

    Methods
    -------
    __init__(self, name='wing_mass'):
        Initializes the WingMassBuilder object with a given name.
    build_pre_mission(self, aviary_inputs) -> openmdao.core.System:
        Builds an OpenMDAO system for the pre-mission computations of the subsystem.
    """

    def __init__(self, name='lift_drag'):
        super().__init__(name)

    def build_pre_mission(self, aviary_inputs):
        """
        Build an OpenMDAO system for the pre-mission computations of the subsystem.

        Returns
        -------
        pre_mission_sys : openmdao.core.System
            An OpenMDAO system containing all computations that need to happen in
            the pre-mission part of the Aviary problem. This
            includes sizing, design, and other non-mission parameters.
        """
        wing_group = om.Group()
        wing_group.add_subsystem(
            'aerostructures',
            CustomMass(),
            promotes_inputs=['aircraft:*'],
            promotes_outputs=[Aircraft.Wing.HIGH_LIFT_MASS_COEFFICIENT],
        )
        return wing_group
