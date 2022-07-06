"""Copyright (c) 2021-2022  The University of Texas Southwestern Medical Center.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted for academic and research use only (subject to the limitations in the disclaimer below)
provided that the following conditions are met:

     * Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     * Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.

     * Neither the name of the copyright holders nor the names of its
     contributors may be used to endorse or promote products derived from this
     software without specific prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY
THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

# Standard Library Imports
import unittest
from pathlib import Path

# Third Party Imports

# Local Imports
from aslm.model.devices.zoom.zoom_base import ZoomBase
from aslm.model.aslm_model_config import Session as session


class TestZoomBase(unittest.TestCase):
    r"""Unit Test for Zoom Base Class"""

    def test_zoom_base_attributes(self):
        base_directory = Path(__file__).resolve().parent.parent.parent.parent.parent
        configuration_directory = Path.joinpath(base_directory, 'src', 'aslm', 'config')
        configuration_path = Path.joinpath(configuration_directory, 'configuration.yml')

        configuration = session(configuration_path, False)
        zoom_class = ZoomBase(configuration, False)

        assert hasattr(zoom_class, 'configuration')
        assert hasattr(zoom_class, 'zoomdict')
        assert hasattr(zoom_class, 'zoomvalue')
        assert hasattr(zoom_class, 'verbose')

if __name__ == '__main__':
    unittest.main()