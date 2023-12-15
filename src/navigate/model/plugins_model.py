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

import os
from pathlib import Path
import inspect

from navigate.tools.common_functions import load_module_from_file
from navigate.tools.file_functions import load_yaml_file, save_yaml_file
from navigate.tools.decorators import FeatureList, AcquisitionMode
from navigate.model.features import feature_related_functions
from navigate.config.config import get_navigate_path


class PluginsModel:
    def __init__(self):
        self.plugins_path = os.path.join(
            Path(__file__).resolve().parent.parent, "plugins"
        )

    def load_plugins(self):
        devices_dict = {}
        plugin_acquisition_modes = {}
        plugins = os.listdir(self.plugins_path)
        feature_lists_path = get_navigate_path() + "/feature_lists"
        feature_list_files = [
            temp
            for temp in os.listdir(feature_lists_path)
            if (temp.endswith(".yml") or temp.endswith(".yaml"))
            and os.path.isfile(os.path.join(feature_lists_path, temp))
        ]
        for f in plugins:
            if not os.path.isdir(os.path.join(self.plugins_path, f)):
                continue

            # read "plugin_config.yml"
            plugin_config = load_yaml_file(
                os.path.join(self.plugins_path, f, "plugin_config.yml")
            )
            if plugin_config is None:
                continue
            plugin_name = plugin_config.get("name", f)

            # feature
            features_dir = os.path.join(self.plugins_path, f, "model", "features")
            if os.path.exists(features_dir):
                features = os.listdir(features_dir)
                for feature in features:
                    feature_file = os.path.join(features_dir, feature)
                    if os.path.isfile(feature_file):
                        temp = load_module_from_file(feature, feature_file)
                        for c in dir(temp):
                            if inspect.isclass(getattr(temp, c)):
                                setattr(feature_related_functions, c, getattr(temp, c))
            # feature list
            plugin_feature_list = os.path.join(self.plugins_path, f, "feature_list.py")
            if os.path.exists(plugin_feature_list):
                module = load_module_from_file("feature_list_temp", plugin_feature_list)
                features = [
                    f
                    for f in dir(module)
                    if isinstance(getattr(module, f), FeatureList)
                ]
                for feature_name in features:
                    feature = getattr(module, feature_name)
                    feature_list_name = feature.feature_list_name
                    feature_list_file_name = "_".join(feature_list_name.split())
                    if (
                        f"{feature_list_file_name}.yml" in feature_list_files
                        or f"{feature_list_file_name}.yaml" in feature_list_files
                    ):
                        continue
                    feature_list_content = {
                        "module_name": feature_name,
                        "feature_list_name": feature_list_name,
                        "filename": plugin_feature_list,
                    }
                    save_yaml_file(
                        feature_lists_path,
                        feature_list_content,
                        f"{feature_list_file_name}.yml",
                    )

            # acquisition mode
            acquisition_modes = plugin_config.get("acquisition_modes", [])
            for acquisition_mode_config in acquisition_modes:
                acquisition_file = os.path.join(
                    self.plugins_path, f, acquisition_mode_config["file_name"]
                )
                if os.path.exists(acquisition_file):
                    module = load_module_from_file(
                        acquisition_mode_config["file_name"][:-3], acquisition_file
                    )
                    acquisition_mode = [
                        m
                        for m in dir(module)
                        if isinstance(getattr(module, m), AcquisitionMode)
                    ]
                    if acquisition_mode:
                        plugin_acquisition_modes[
                            acquisition_mode_config["name"]
                        ] = getattr(module, acquisition_mode[0])(
                            acquisition_mode_config["name"]
                        )

            # device
            device_dir = os.path.join(self.plugins_path, f, "model", "devices")
            if os.path.exists(device_dir):
                devices = os.listdir(device_dir)
                for device in devices:
                    device_path = os.path.join(device_dir, device)
                    if not os.path.isdir(device_path):
                        continue
                    module = load_module_from_file(
                        "device_module",
                        os.path.join(device_path, "device_startup_functions.py"),
                    )
                    if module:
                        devices_dict[device] = {}
                        devices_dict[device]["ref_list"] = module.DEVICE_REF_LIST
                        devices_dict[device]["load_device"] = module.load_device
                        devices_dict[device]["start_device"] = module.start_device
        return devices_dict, plugin_acquisition_modes
