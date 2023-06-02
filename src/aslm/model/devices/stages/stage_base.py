# Copyright (c) 2021-2022  The University of Texas Southwestern Medical Center.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted for academic and research use only (subject to the
# limitations in the disclaimer below) provided that the following conditions are met:
#
#      * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#
#      * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#      * Neither the name of the copyright holders nor the names of its
#      contributors may be used to endorse or promote products derived from this
#      software without specific prior written permission.
#
# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY
# THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Standard Imports
import logging
from multiprocessing.managers import ListProxy

# Third Party Imports

# Local Imports

# Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)


class StageBase:
    """StageBase Parent Class

    Parameters
    ----------
    microscope_name : str
        Name of microscope in configuration
    device_connection : object
        Hardware device to connect to
    configuration : multiprocessing.managers.DictProxy
        Global configuration of the microscope

    Attributes
    -----------
    x_pos : float
        True x position
    y_pos : float
        True y position
    z_pos : float
        True z position
    f_pos : float
        True focus position
    theta_pos : float
        True rotation position
    x_max : float
        Max x position
    y_max : float
        Max y position
    z_max : float
        Max y position
    f_max : float
        Max focus position
    theta_max : float
        Max rotation position
    x_min : float
        Min x position
    y_min : float
        Min y position
    z_min : float
        Min y position
    f_min : float
        Min focus positoin
    theta_min : float
        Min rotation position

    Methods
    -------
    get_position_dict()
        Returns a dictionary with the hardware stage positions.
    get_abs_position()
        Makes sure that the move is within the min and max stage limits.
    verify_abs_position()
        Return a dictionary with moving positions within the min and max stage limits
    stop()
        Emergency halt of stage operation.

    """

    def __init__(self, microscope_name, device_connection, configuration, device_id=0):

        stage = configuration["configuration"]["microscopes"][microscope_name]["stage"]
        if type(stage["hardware"]) == ListProxy:
            self.axes = list(stage["hardware"][device_id]["axes"])
            device_axes = stage["hardware"][device_id].get("axes_mapping", [])
        else:
            self.axes = list(stage["hardware"]["axes"])
            device_axes = stage["hardware"].get("axes_mapping", [])

        if device_axes is None:
            device_axes = []

        if len(self.axes) > len(device_axes):
            log_string = f"{microscope_name}: stage axes mapping is not specified in "
            "the configuration file, will use the default one in the code!"
            logger.debug(log_string)
            print(log_string)

        self.axes_mapping = dict(zip(self.axes, device_axes))

        """Initial setting for all positions
        self.x_pos, self.y_pos etc are the true axis positions, no matter whether
        the stages are zeroed or not.
        """
        for ax in self.axes:
            setattr(self, f"{ax}_pos", 0)
            setattr(self, f"{ax}_min", stage[f"{ax}_min"])  # Units are in microns
            setattr(self, f"{ax}_max", stage[f"{ax}_max"])  # Units are in microns
        self.stage_limits = True

    def get_position_dict(self):
        """Return a dictionary with the saved stage positions."""
        position_dict = {}
        for ax in self.axes:
            ax_str = f"{ax}_pos"
            position_dict[ax_str] = getattr(self, ax_str)
        return position_dict

    def get_abs_position(self, axis, axis_abs):
        """Ensure the requested position is within axis bounds and return it.

        Parameters
        ----------
        axis : str
            An axis: x, y, z, f, theta
        axis_abs : float
            Absolute position value

        Returns
        -------
        float
            Position to move the stage to for this axis.
        """
        try:
            # Get all necessary attributes.
            # If we can't we'll move to the error case (e.g., -1e50).
            axis_min, axis_max = getattr(self, f"{axis}_min"), getattr(
                self, f"{axis}_max"
            )
        except (KeyError, AttributeError) as e:
            # Alert the user, but don't kill the thread
            msg = f"No key {e} in move_dictionary or axis missing from {self.axes}."
            logger.debug(msg)
            print(msg)
            return -1e50

        if not self.stage_limits:
            return axis_abs

        # Check that our position is within the axis bounds, fail if it's not.
        if (axis_min > axis_abs) or (axis_max < axis_abs):
            log_string = (
                f"Absolute movement stopped: {axis} limit would be reached!"
                f"{axis_abs} is not in the range {axis_min} to {axis_max}."
            )
            logger.info(log_string)
            print(log_string)
            # Return a ridiculous value to make it clear we've failed.
            # This is to avoid returning a duck type.
            return -1e50
        return axis_abs

    def verify_abs_position(self, move_dictionary, is_strict=False):
        """Ensure the requested moving positions are within axes bounds

        Parameters
        ----------
        move_dictionary : dict
            A dictionary of values required for movement.
            Includes 'x_abs', 'y_abs', etc. for one or more axes.
            Expect values in micrometers, except for theta, which is in degrees.

        Returns
        -------
        dict
            a verified moving dict {axis: abs_position}
        """
        abs_pos_dict = {}
        result_flag = True
        for axis in self.axes_mapping.keys():
            if f"{axis}_abs" not in move_dictionary:
                continue
            axis_abs = move_dictionary[f"{axis}_abs"]
            axis_min = getattr(self, f"{axis}_min")
            axis_max = getattr(self, f"{axis}_max")

            if self.stage_limits and ((axis_abs < axis_min) or (axis_abs > axis_max)):
                log_string = (
                    f"Absolute movement stopped: {axis} limit would be reached!"
                    f"{axis_abs} is not in the range {axis_min} to {axis_max}."
                )
                logger.info(log_string)
                print(log_string)
                result_flag = False
            else:
                abs_pos_dict[axis] = axis_abs

        if is_strict and not result_flag:
            return {}
        return abs_pos_dict

    def stop(self):
        """Stop all stage movement abruptly."""
        pass
