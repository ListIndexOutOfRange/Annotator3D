import tifffile
import numpy as np
import streamlit as st
from typing import Tuple
from scipy import ndimage
from skimage import exposure, img_as_float


def get_spacing(tiff_path: str) -> Tuple[float]:
    with tifffile.TiffFile(tiff_path) as tif:
        metadata = tif.pages[0].tags
        res_x, res_y = metadata['XResolution'].value[0], metadata['YResolution'].value[0]
    inch_to_mm = 25.4 
    spacing_yx = (1 / np.array((res_y, res_x))) * inch_to_mm
    spacing = (1, *spacing_yx)
    return spacing


def normalize_spacing(image: np.ndarray, spacing: Tuple[float], target_spacing: Tuple[float]=(1, 1, 1)) -> Tuple[np.ndarray]:
    spacing, new_spacing = np.array(spacing), np.array(target_spacing)
    resize_factor  = spacing / new_spacing
    new_real_shape = image.shape * resize_factor
    new_shape = np.round(new_real_shape)
    real_resize = new_shape / image.shape
    new_spacing = spacing / real_resize
    normalized_image = ndimage.interpolation.zoom(image, real_resize)
    return normalized_image, new_spacing


def rescale_intensity(image: np.ndarray, percentile: Tuple[float]=(0.5, 99.5)) -> np.ndarray:
    vmin, vmax = np.percentile(image, percentile)
    return exposure.rescale_intensity(image, in_range=(vmin, vmax))


@st.cache(show_spinner=False)
def load_and_preprocess(path: str) -> np.ndarray:
	with st.spinner('Loading and preprocessing 3D tiff file...'):
		image = tifffile.imread(path)
		image, new_spacing = normalize_spacing(image, get_spacing(path))
		image = rescale_intensity(image)
		image = img_as_float(image)
	return image