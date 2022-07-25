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
from scipy import stats

# Local Imports


class StatisticalImageFocus:
    r"""
    Image quality metrics that are based upon standard statistical approaches.

    """
    @staticmethod
    def mean(self, image_array):
        return np.mean(image_array)

    @staticmethod
    def max(self, image_array):
        return np.max(image_array)

    @staticmethod
    def variance(self, image_array):
        return np.var(image_array)

    def normalized_variance(self, image_array):
        image_variance = self.variance(image_array)
        image_mean = self.mean(image_array)
        return np.divide(image_variance, np.multiply(image_mean, image_mean))

    @staticmethod
    def kurtosis(self, image_array):
        return stats.kurtosis(image, axis=None, fisher=False, bias=False)

    def difference_image_kurtosis(self, image_array):
        dif_image = image_array[1:, 1:] - image_array[:-1, :-1]
        return self.kurtosis(dif_image)

    def histogram_entropy(self, image_array):
        pass

    def l_p_sparsity(self, image_array):
        pass



if __name__ == "__main__":
    from skimage import filters
    from tifffile import imread

    image_path = r"/Users/S155475/Desktop/test_image.tif"
    image = imread(image_path)
    image = np.array(image, dtype=np.double)

    image = preprocess_data(image, binning_factor=3)
    for i in range(5):
        smooth = filters.gaussian(image, i)
        metric = vollath_f4_method(smooth)
        print("Gaussian Filter:", i, "Image Contrast:", metric)
