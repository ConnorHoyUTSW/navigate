

def test_down_sample_by_sum_2x():
    array = np.arange(24).reshape(4, 6)
    ds_array = down_sample_by_sum(array, binning_factor=2)
    assert np.shape(ds_array) == (2, 3)
    assert ds_array[0, 0] == 14
    assert ds_array[0, 1] == 22
    assert ds_array[0, 2] == 30


def test_down_sample_by_sum_3x():
    array = np.arange(24).reshape(4, 6)
    ds_array = down_sample_by_sum(array, binning_factor=3)
    assert np.shape(ds_array) == (1, 2)
    assert ds_array[0, 0] == 63
    assert ds_array[0, 1] == 90