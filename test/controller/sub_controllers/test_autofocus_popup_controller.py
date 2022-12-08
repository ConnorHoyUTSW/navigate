# Copyright (c) 2021-2022  The University of Texas Southwestern Medical Center.
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
#

from aslm.controller.sub_controllers import AutofocusPopupController
from aslm.view.menus.autofocus_setting_popup import autofocus_popup
import pytest

class TestAutofocusPopupController():

    @pytest.fixture(autouse=True)
    def setup_class(self, dummy_controller):
        c = dummy_controller
        v = dummy_controller.view
        afpop = autofocus_popup(v)

        self.af_controller = AutofocusPopupController(afpop, c)


    def test_init(self):

        assert isinstance(self.af_controller, AutofocusPopupController)
        assert self.af_controller.view.popup.winfo_exists() == 1


    def test_attr(self):

        # Listing off attributes to check existence
        attrs = [ 'autofocus_fig', 'autofocus_coarse', 'autofocus_fine', 'widgets', 'setting_dict' ]

        for attr in attrs:
            assert hasattr(self.af_controller, attr)


    def test_populate_experiment_values(self):
         
         # Because this function runs inside of init, we can check that things are correct
         for k in self.af_controller.widgets:
            assert self.af_controller.widgets[k].get() == str(self.af_controller.setting_dict[k]) # Some values are ints but Tkinter only uses strings

    
    def test_update_experiment_values(self):
        
        # Changing values
        self.af_controller.widgets['coarse_range'].set(200)
        self.af_controller.widgets['coarse_step_size'].set(30)
        self.af_controller.view.stage_vars[0].set(False)
        self.af_controller.widgets['fine_range'].set(25)
        self.af_controller.widgets['fine_step_size'].set(2)
        self.af_controller.view.stage_vars[1].set(False)

        # Updating file
        self.af_controller.update_experiment_values()

        # Checking values match
        for k in self.af_controller.widgets:
            assert self.af_controller.widgets[k].get() == str(self.af_controller.setting_dict[k])
        assert self.af_controller.view.stage_vars[0].get() == self.af_controller.setting_dict['coarse_selected']
        assert self.af_controller.view.stage_vars[1].get() == self.af_controller.setting_dict['fine_selected']

    
    def test_start_autofocus(self):

        # Calling function
        self.af_controller.start_autofocus()

        # Checking message sent
        res = self.af_controller.parent_controller.pop()
        assert res == 'autofocus'


    def test_display_plot(self):
        pass