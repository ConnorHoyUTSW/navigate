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

def test_stage_base_attributes():
    from aslm.model.devices.stages.stage_base import StageBase
    from aslm.model.dummy import DummyModel
    
    model = DummyModel()
    microscope_name = model.configuration['experiment']['MicroscopeState']['microscope_name']
    stage_base = StageBase(microscope_name, None, model.configuration)
    stage_config = model.configuration['configuration']['microscopes'][microscope_name]['stage']
    
    attrs = [
             'x_pos', 'y_pos', 'z_pos', 
             'f_pos', 'theta_pos', 'position_dict', 
             'int_x_pos', 'int_y_pos', 'int_z_pos',
             'int_f_pos', 'int_theta_pos', 'int_position_dict',
             'int_x_pos_offset', 'int_y_pos_offset', 'int_z_pos_offset',
             'int_f_pos_offset', 'int_theta_pos_offset', 'x_max',
             'y_max', 'z_max', 'f_max', 'x_min', 'y_min', 'z_min',
             'f_min', 'theta_min', 'x_rot_position', 'y_rot_position',
             'z_rot_position', 'startfocus', 'axes'
            ]

    for attr in attrs:
        assert hasattr(stage_base, attr)
        
            
def test_stage_base_functions():
    from aslm.model.devices.stages.stage_base import StageBase
    from aslm.model.dummy import DummyModel
    
    model = DummyModel()
    microscope_name = model.configuration['experiment']['MicroscopeState']['microscope_name']
    stage_base = StageBase(microscope_name, None, model.configuration)
    stage_config = model.configuration['configuration']['microscopes'][microscope_name]['stage']
    
    funcs = ['create_position_dict', 'create_internal_position_dict', 'update_position_dictionaries', 'get_abs_position', 'stop']
    args = [None, None, None, ['x', {'x_abs': 0}], None]
    
    for f, a in zip(funcs, args):
        if a is not None:
            getattr(stage_base, f)(*a)
        else:
            getattr(stage_base, f)()