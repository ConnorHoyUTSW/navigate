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

# Third Party Imports
import numpy as np

# Local Imports


class ImagePreProcessing:
    def preprocess(self,
                   image_array,
                   binning_factor=3):
        r"""Downsample and normallize the data.

        Parameters
        ----------
        image_array : np.ndarray
            Input image.
        binning_factor : int
            Downsampling factor.

        Returns
        -------
        ds_array : np.ndarray
            Downsampled and normalized image.
        """

        ds_array = self.downsample(image_array, binning_factor=binning_factor)
        return self.normalize_norm_l1(ds_array)

    @staticmethod
    def downsample(self,
                   input_array,
                   binning_factor=3):
        r"""Down-sample image by taking sum of pixel neighborhood.

        Implemented using a 2D convolution.
        Parameters
        ----------
        input_array : numpy.ndarray
            Original Image
        binning_factor : int
            Factor to down-sample the data by.

        Returns
        -------
        down_sampled_image : numpy.ndarray
            Final image.

        """
        kernel = np.ones((binning_factor,
                          binning_factor))
        convolved = convolve2d(input_array,
                               kernel,
                               mode='valid')
        return convolved[::binning_factor, ::binning_factor]

    @staticmethod
    def normalize_norm_l1(self, image_array):
        r"""Normalize image by L1 norm.

        Parameters
        ----------
        image_array : np.ndarray
            Input image.

        Returns
        -------
        norm_image : np.ndarray
            Normalized image.
        """
        l1_norm = np.linalg.norm(image_array, ord=1)
        norm_image = np.divide(image_array, l1_norm)
        return norm_image
