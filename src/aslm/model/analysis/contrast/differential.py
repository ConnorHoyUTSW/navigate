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
import cv2
from scipy.signal import convolve2d

# Local Imports


class DifferentialImageFocus:
    r"""Edge-detection-based image quality metrics."""
    @staticmethod
    def brenners_method(self,
                        image_array):
        r"""Brenner's Focus Method.

        Brenner JF, Dew BS, Horton JB, King T, Neurath PW, Selles WD.
        An automated microscope for cytologic research a preliminary evaluation.
        Journal of Histochemistry & Cytochemistry. 1976;24(1):100-111. doi:10.1177/24.1.1254907

        Parameters
        ----------
        image_array : 2D image array.

        Returns
        -------
        Brenner contrast metric.

        """
        shift_array = image_array[:, :-1] - image_array[:, 1:]
        shift_array = np.sum(shift_array * shift_array)
        return shift_array / image_array.size
    
    @staticmethod
    def absolute_laplacian_method(image_array):
        r"""Measure the absolute summed Laplace of an image.
    
        Convolution-based.
    
        Parameters
        ----------
        image_array : np.ndarray
            Input image.
    
        Returns
        -------
        absolute_laplace : float
    
        """
        d2x = np.abs(convolve2d(image_array, np.mat('-1, 2, -1'), mode='same'))
        d2y = np.abs(convolve2d(image_array, np.mat('-1; 2; -1'), mode='same'))
        # kernel = np.array(np.mat('0, 1, 0;'
        #                          '1, -4, 1;'
        #                          '0, 1 ,0'))
        # convolved = np.sum(np.abs(convolve2d(image_array,
        #                                      kernel,
        #                                      mode='same')))
        return np.sum(convolved)
    
    
    def squared_laplacian_like_method(image_array):
        kernel = np.array(np.mat('0, 1, 0; '
                                 '1, -4, 1; '
                                 '0, 1 ,0'))

        pass
    
    
    def total_variation_method(image_array):
        x_gradient = np.square(image_array[1:, :] - image_array[:-1, :])
        y_gradient = np.square(image_array[:, 1:] - image_array[:, :-1])
        x_gradient = np.sum(x_gradient ** 2)
        y_gradient = np.sum(y_gradient ** 2)
        return np.sqrt(x_gradient + y_gradient) / image_array.size
    
    
    def block_total_variation_method(image_array):
        pass
    
    
    def tenengrad_method(image_array, ksize=3):
        r"""Tenengrad Focus Method
    
        TTE Yeo, SH Ong,  Jayasooriah, R Sinniah,
        Autofocusing for tissue microscopy,
        Image and Vision Computing, Volume 11, Issue 10, 1993, Pages 629-639,
    
    
        """
        x_gradient = cv2.Sobel(image_array,
                               ddepth=cv2.CV_64F,
                               dx=1,
                               dy=0,
                               ksize=ksize)
        y_gradient = cv2.Sobel(image_array,
                               ddepth=cv2.CV_64F,
                               dx=0,
                               dy=1,
                               ksize=ksize)
        focus_metric = x_gradient*x_gradient + y_gradient*y_gradient
        focus_metric_mean = cv2.mean(focus_metric)[0]
        if np.isnan(focus_metric_mean):
            return np.nanmean(focus_metric)
        return focus_metric_mean



