#"""Copyright (c) 2021-2022  The University of Texas Southwestern Medical Center.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted for academic and research use only (subject to the limitations in the disclaimer below)
# provided that the following conditions are met:

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
# """

import pytest
from aslm.model.devices.stages.stage_pi import PIStage, build_PIStage_connection
from multiprocessing.managers import ListProxy

@pytest.fixture(scope='class')
def pistage(dummy_model):
    dummy_model = dummy_model
    stages = dummy_model.configuration['configuration']['hardware']['stage']
    pistage = []
    # Checking if multiple stages
    if type(stages) == ListProxy:
        for s in stages:
            if s['type'] == 'PI':
                pistage.append(s)
    else:
        if stages['type'] == 'PI':
            pistage.append(s)
            
    if len(pistage) == 0:
            raise TypeError(f"Wrong stage hardware specified PI stage not found")
        
    microscope_name = dummy_model.configuration['experiment']['MicroscopeState']['microscope_name']

    serial_controller = build_PIStage_connection(pistage[0]['controllername'], pistage[0]['serial_number'], pistage[0]['stages'], pistage[0]['refmode'])
    
    stage = PIStage(microscope_name, serial_controller, dummy_model.configuration)
    
    return stage

class TestPIStage:
    
    @pytest.fixture(autouse=True)
    def _setup_stage(self, pistage):
        self.pistage = pistage

    @pytest.mark.hardware
    def test_PIStage_init(self):
        
        # Initializing stage using fixture essentially testing that fixture works
        pistage = self.pistage
        # assert pistage != None TODO should we test it exists or will it catch already
        
    @pytest.mark.hardware
    def test_PIStage_attributes(self):
        
        # Listing off attributes to check existence
        attrs = ['axes', 'pi_axes', 'pitools', 'pidevice']

        for attr in attrs:
            assert hasattr(self.pistage, attr)
            
        # Robust check for proper axes encoding in PI
        for i , axes in enumerate(self.pistage.pi_axes):
            assert axes == (i + 1)
        
    @pytest.mark.hardware
    def test_PIStage_report_position(self):
        
        # Setup data
        test_dict = self.pistage.position_dict
        
        # Report data
        report_dict = self.pistage.report_position()
        
        assert report_dict == test_dict


    @pytest.mark.hardware
    def test_PIStage_move(self):
        '''
        Combines move absolute and move axis absolute in one test
        '''

        # Get current position of stage and grab step sizes from experiment file
        steps = self.pistage.dummy_model.configuration['experiment']['StageParameters']
        step_size = { key:value for key, value in steps.items() if "step" in key }
        step_size['x_step'] = step_size['xy_step']
        step_size['y_step'] = step_size['xy_step']

        positions = self.pistage.report_position()
        origin = { key.split("_")[0] + "_abs" : value for key, value in positions.items() }
        move_dict = { key.split("_")[0] + "_abs" : value + step_size[key+"_step"] for key, value in positions.items() }

        # Call move absolute from PIStage, which in turn will call move_axis_absolute
        self.pistage.move_absolute(move_dict, True)
        new_pos = self.pistage.report_position()
        new_pos = { key.split("_")[0] + "_abs" : value for key, value in new_pos.items() }
        assert new_pos == move_dict

        # Move back to starting position
        self.pistage.move_absolute(origin, True)
        final = self.pistage.report_position()
        final = { key.split("_")[0] + "_abs" : value for key, value in final.items() }
        assert origin == final


    @pytest.mark.hardware
    def test_PIStage_stop(self):
        '''
        Then for the stop stage command, you could try something like the following:
            Get current stage position
            Move stage 1 mm in each dimension
            Immediately halt operation (wait until complete operation may have to be false)
            Confirm that the stage did not move to the target, and that it is not moving still.
        '''

        # Setup step sizes, 2 steps for everything but theta is 1 mm
        steps = self.pistage.dummy_model.configuration['experiment']['StageParameters']
        step_size = { key: (value * 2) for key, value in steps.items() if "step" in key }
        step_size['x_step'] = step_size['xy_step']
        step_size['y_step'] = step_size['xy_step']
        step_size['theta_step'] = 10 # 10 Degrees step size

        # Get current position of stage
        positions = self.pistage.report_position()
        origin = { key.split("_")[0] + "_abs" : value for key, value in positions.items() }

        # Move stage 1 mm in each direction
        move_dict = { key.split("_")[0] + "_abs" : value + step_size[ key + "_step" ] for key, value in positions.items() }
        self.pistage.move_absolute(move_dict, False)

        # Immediately halt operation
        self.pistage.stop()

        # Check stage did not move to target
        stop_pos = self.pistage.report_position()
        stop_pos = { key.split("_")[0] + "_abs" : value for key, value in stop_pos.items() }
        assert stop_pos != move_dict

        # Move back to starting position
        self.pistage.move_absolute(origin, True)
        final = self.pistage.report_position()
        final = { key.split("_")[0] + "_abs" : value for key, value in final.items() }
        assert origin == final



    @pytest.mark.hardware
    def test_PIStage_load(self):
        '''
        Combines load and unload sample
        '''

        # Origin
        positions = self.pistage.report_position()
        origin = { key.split("_")[0] + "_abs" : value for key, value in positions.items() }

        # Load sample
        self.pistage.load_sample()
        post_load_pos = self.pistage.report_position()
        post_load_pos = { key.split("_")[0] + "_abs" : value for key, value in post_load_pos.items() }
        assert post_load_pos['y_abs'] == self.pistage.y_load_position / 1000

        # Unload sample
        self.pistage.unload_sample()
        post_unload_pos = self.pistage.report_position()
        post_unload_pos = { key.split("_")[0] + "_abs" : value for key, value in post_unload_pos.items() }
        assert post_unload_pos['y_abs'] == self.pistage.y_unload_position / 1000

        # Move back to start
        self.pistage.move_absolute(origin, True)
        final = self.pistage.report_position()
        final = { key.split("_")[0] + "_abs" : value for key, value in final.items() }
        assert origin == final
 
        
    @pytest.mark.hardware
    def test_PIStage_del(self):
        
        # Initializing stage then deleting
        pistage = self.pistage
        del pistage
    