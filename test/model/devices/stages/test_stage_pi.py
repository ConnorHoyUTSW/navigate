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

@pytest.mark.hardware
def test_PIStage_init():
    from aslm.model.devices.stages.stage_pi import PIStage, build_PIStage_connection
    from aslm.model.dummy import DummyModel
    from multiprocessing.managers import ListProxy

    model = DummyModel()
    # Checking if there are multiple stages
    stages = model.configuration['configuration']['hardware']['stage']
    pistage = []
    if type(stages) == ListProxy:
        for s in stages:
            if s['type'] == 'PI':
                pistage.append(s)
    else:
        if stages['type'] == 'PI':
            pistage.append(s)
            
    if len(pistage) == 0:
            raise TypeError(f"Wrong stage hardware specified PI stage not found")
        
    

        
    microscope_name = model.configuration['experiment']['MicroscopeState']['microscope_name']

    
    serial_controller = build_PIStage_connection(pistage[0]['controllername'], pistage[0]['serial_number'], pistage[0]['stages'], pistage[0]['refmode'])
    
    stage = PIStage(microscope_name, serial_controller, model.configuration)

@pytest.mark.hardware
def test_PIStage_attributes():
    from aslm.model.devices.stages.stage_pi import PIStage, build_PIStage_connection
    from aslm.model.dummy import DummyModel
    from multiprocessing.managers import ListProxy
    import functools

    model = DummyModel()
    # Checking if there are multiple stages
    stages = model.configuration['configuration']['hardware']['stage']
    pistage = []
    if type(stages) == ListProxy:
        for s in stages:
            if s['type'] == 'PI':
                pistage.append(s)
    else:
        if stages['type'] == 'PI':
            pistage.append(s)
            
    if len(pistage) == 0:
            raise TypeError(f"Wrong stage hardware specified PI stage not found")

    microscope_name = model.configuration['experiment']['MicroscopeState']['microscope_name']

    
    serial_controller = build_PIStage_connection(pistage[0]['controllername'], pistage[0]['serial_number'], pistage[0]['stages'], pistage[0]['refmode'])
    
    stage = PIStage(microscope_name, serial_controller, model.configuration)
    
    attrs = ['axes', 'pi_axes', 'pitools', 'pidevice']

    for attr in attrs:
        assert hasattr(stage, attr)
        
    # Robust check for proper axes encoding in PI
    for i , axes in enumerate(stage.pi_axes):
        assert axes == (i + 1)
        
    