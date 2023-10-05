 # Copyright (c) 2021-2022  The University of Texas Southwestern Medical Center.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted for academic and research use only (subject to the
# limitations in the disclaimer below) provided that the following conditions are met:

#      * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.

#      * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.

#      * Neither the name of the copyright holders nor the names of its
#      contributors may be used to endorse or promote products derived from this
#      software without specific prior written permission.

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
#

# Standard Library Imports
import time
import logging

# Third Party Imports
import numpy as np
import re

# Local Imports
from aslm.model.features.image_writer import ImageWriter

p = __name__.split(".")[1]
logger = logging.getLogger(p)

# Local imports


class ConstantVelocityAcquisition:
    """Class for acquiring data using the ASI internal encoder."""

    def __init__(self, model, axis='z', saving_flag=False, saving_dir="cva"):
        # Microscope Parameters
        self.model = model
        self.microscope_state = None

        # Stage Parameters
        self.axis = axis
        self.default_speed = None
        self.asi_stage = None

        # Acquisition Parameters
        self.stack_cycling_mode = None
        self.channels = 1
        self.current_channel_in_list = None
        self.readout_time = None
        self.waveform_dict = None

        # Scan Parameters
        self.actual_mechanical_step_size_um = None
        self.desired_mechanical_step_size_um = None
        self.desired_mechanical_step_size_mm = None
        self.desired_speed = None
        self.current_sweep_time = None
        self.start_position_mm = None
        self.start_position_um = None
        self.stop_position_mm = None
        self.stop_position_um = None
        self.number_z_steps = None
        self.actual_number_z_steps = None

        # Total frames / channel
        self.received_frames = None

        # Total frames overall
        self.total_received_frames = None
        self.total_expected_frames = None
        self.current_z_position_um = None

        # Flags
        self.end_acquisition = None

        # Saving Parameters
        self.saving_flag = saving_flag
        self.image_writer = None
        if self.saving_flag:
            self.image_writer = ImageWriter(
                model=self.model,
                sub_dir=saving_dir)

        logger.debug("Constant Velocity Acquisition Mode Initialized.")

        self.config_table = {
            "signal": {
                "init": self.pre_signal_function,
                "main": self.main_signal_function,
                "end": self.end_signal_function,
                "cleanup": self.cleanup_signal_function,
            },
            "data": {
                "init": self.pre_data_function,
                "main": self.main_data_function,
                "end": self.end_data_function,
                "cleanup": self.cleanup_data_function,
            },
            "node": {
                "node_type": "multi-step",
                "device_related": True
            },
        }

    def pre_signal_function(self):
        """Prepare the constant velocity acquisition.

        Assumes stage motion is 45 degrees relative to the optical axis.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # Specify the scan axis
        self.asi_stage = self.model.active_microscope.stages[self.axis]

        # Configure Flags and Counters
        self.end_acquisition = False
        self.received_frames = 0
        self.total_received_frames = 0

        # Configure Stage
        self.desired_mechanical_step_size_um = float(
            self.model.configuration[
                "experiment"]["MicroscopeState"]["step_size"])
        self.desired_mechanical_step_size_mm = self.desired_mechanical_step_size_um / 1000.0

        self.start_position_um = float(
            self.model.configuration[
                "experiment"]["MicroscopeState"]["abs_z_start"])
        self.start_position_mm = self.start_position_um / 1000.0
        logger.debug(f"Scan Start Position (mm) {self.start_position_mm}")

        self.stop_position_um = float(
            self.model.configuration[
                "experiment"]["MicroscopeState"]["abs_z_end"])
        self.stop_position_mm = self.stop_position_um / 1000.0
        logger.debug(f"Scan Stop Position (mm) {self.stop_position_mm}")

        # Calculate Number of Z Steps.
        self.number_z_steps = np.floor(
                abs(
                    self.stop_position_mm - self.start_position_mm
                ) / self.desired_mechanical_step_size_mm
            )
        logger.debug(f"Number of Z Steps {self.number_z_steps}")

        # Get the maximum speed for the stage.
        self.asi_stage.set_speed(percent=1)
        max_speed = self.asi_stage.get_speed(axis=self.axis)
        logger.debug(f"Axis {self.axis} Maximum Speed (mm/s): {max_speed}")

        # Get the minimum speed for the stage.
        self.asi_stage.set_speed(percent=0.0001)
        minimum_speed = self.asi_stage.get_speed(axis=self.axis)
        logger.debug(f"Axis {self.axis} Minimum Speed (mm/s): {minimum_speed}")

        # Get Microscope State
        self.microscope_state = self.model.configuration[
            "experiment"]["MicroscopeState"]
        self.stack_cycling_mode = self.microscope_state["stack_cycling_mode"]
        # Should only be per_stack acquisition.
        # TODO: Inject stop acquisition flag and notify user.

        self.channels = self.microscope_state["selected_channels"]
        self.current_channel_in_list = 0
        self.model.active_microscope.current_channel = 0

        # Configure the constant velocity/confocal projection mode
        self.model.configuration[
            "experiment"]["MicroscopeState"]["waveform_template"] = "CVACONPRO"
        self.model.configuration[
            "waveform_templates"]["CVACONPRO"]["expand"] = int(self.number_z_steps)
        self.model.configuration[
            "waveform_templates"]["CVACONPRO"]["repeat"] = int(1)

        self.model.active_microscope.prepare_next_channel()
        print("prepare next channel worked")

        self.model.active_microscope.daq.set_external_trigger("/PXI6259/PFI1")
        print("set external trigger worked")
        # Calculate the readout time for the camera and microscope sweep time.

        self.readout_time = self.model.active_microscope.get_readout_time()
        print("got the readout")

        _, sweep_times = self.model.active_microscope.calculate_exposure_sweep_times(
            self.readout_time)
        print("got the sweeptime")

        self.current_sweep_time = sweep_times[
            f"channel_{self.model.active_microscope.current_channel}"]
        print("got the current sweep time")

        # Get the desired speed for the stage.
        self.desired_speed = self.desired_mechanical_step_size_mm / self.current_sweep_time
        logger.debug(f"Axis {self.axis} Desired Speed (mm/s): {self.desired_speed}")

        stage_velocity = self.asi_stage.get_speed(axis=self.axis)
        logger.debug(f"Axis {self.axis} Actual Speed (mm/s): {stage_velocity}")

        # Inaccurate velocity results in inaccurate step size.
        # Update the Microscope/Configuration to record the actual step size
        actual_mechanical_step_size_mm = stage_velocity * self.current_sweep_time
        self.actual_mechanical_step_size_um = actual_mechanical_step_size_mm * 1000
        self.actual_number_z_steps = np.floor(
            abs(
                self.start_position_um - self.stop_position_um
            ) / self.actual_mechanical_step_size_um
        )
        print("pre signal function complete")

    def main_signal_function(self):
        print("main signal function called")
        if self.model.stop_acquisition:
            return False

        # Move to start position. Move axis absolute is in units microns.
        print("moving stage to start position")
        self.asi_stage.set_speed(percent=0.7)
        self.asi_stage.move_axis_absolute(
            axis=self.axis,
            abs_pos=self.start_position_um,
            wait_until_done=True)
        logger.debug(f"Current Stage Position (mm) "
                     f"{self.asi_stage.get_axis_position(self.axis) / 1000.0}")
        self.current_z_position_um = self.start_position_um

        # Configure the constant velocity scan.
        self.asi_stage.set_speed(velocity_dict={"X": self.desired_speed})
        self.asi_stage.scanr(
            start_position_mm=self.start_position_mm,
            end_position_mm=self.stop_position_mm,
            enc_divide=self.desired_mechanical_step_size_mm,
            axis=self.axis
        )
        print("starting scan")
        self.asi_stage.start_scan(self.axis)
        return True

    def end_signal_function(self):
        print("end signal function called")

        if self.model.stop_acquisition:
            return True

        if self.received_frames >= self.number_z_steps:
            print("updating channel")
            self.update_channel()
            self.received_frames = 0
            print("preparing next channel")
            self.model.active_microscope.prepare_next_channel()

            print("Current Channel", self.current_channel_in_list)
            if self.current_channel_in_list == 0:
                print("current_channel_in_list == 0")
                return True
        return False

    def update_channel(self):
        print("Updating channel")
        self.current_channel_in_list = (
            self.current_channel_in_list + 1) % self.channels


    def cleanup_signal_function(self):
        """Clean up the constant velocity acquisition.

        Moves the stage back to the start position and resets the trigger
        source.

        """
        print("Clean up signal function called")
        # Reset the settings - This should only be done after the last channel.
        self.model.configuration[
            "experiment"]["MicroscopeState"]["waveform_template"] = "Default"
        self.model.active_microscope.current_channel = 0
        self.model.active_microscope.daq.external_trigger = None
        self.model.active_microscope.prepare_next_channel()
        self.model.active_microscope.daq.set_external_trigger()
        self.asi_stage.set_speed(percent=0.7)
        return True

    def pre_data_function(self):
        """Prepare the constant velocity acquisition.

        Sets the number of frames to receive and the total number of frames.

        Function is called at the beginning of the acquisition.
        """
        self.total_expected_frames = self.channels * self.number_z_steps

    def main_data_function(self, frame_ids):
        """Process the data from the constant velocity acquisition.

        Writes data to disk.

        Function is called after every image acquisition. Largely bookkeeping.

        Parameters
        ----------
        frame_ids : list
            List of frame ids received from the camera.
        """
        self.received_frames += len(frame_ids)
        self.total_received_frames += len(frame_ids)

        if self.saving_flag:
            self.image_writer.write_frames(frame_ids)

    def end_data_function(self):
        """Evaluate end condition for constant velocity acquisition.

        Function is called after every image acquisition.

        Returns
        -------
        bool
            True if the acquisition is complete, False otherwise.
        """
        if self.total_received_frames >= self.total_expected_frames:
            self.model.stop_acquisition = True

        if self.received_frames >= self.number_z_steps:
            # If we don't have the self.model.stop_acquisition flag set to True here,
            # we never leave this function. However, if we do set it to True, we never
            # get to the second channel.
            print("received frames >= number z steps")
            # self.model.stop_acquisition = True
            return True
        else:
            return False

    def cleanup_data_function(self):
        """Clean up the constant velocity acquisition.

        Designed to be called in the case of a failure.
        Do not rely on this function being called.

        Cleans up the image writer.
        """
        print("clean up data function called")
        if self.saving_flag:
            self.image_writer.cleanup()
