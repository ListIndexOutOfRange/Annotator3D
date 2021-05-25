import os
import numpy as np
import streamlit as st
from typing import Tuple, List
import preprocess as P
import SessionState


ROOTDIR = "/media/almotasim/DATA/Datasets/SFE/FOV_90/"
IMAGE   = "FOV_90_MMStack_Pos0_zstep0.15_t000001_c2_decon.tif" 


@st.cache(show_spinner=False)
def get_images_paths(rootdir: str) -> List[str]:
	return list(filter(lambda x: x.endswith(('tiff', 'tif')), os.listdir(rootdir)))


def select_image():
	directory  = st.text_input("Working Directory")
	if directory:
		image_path = st.selectbox('Select Image', get_images_paths(directory))
	load = st.button('Load Selected Image')
	if load:
		return os.path.join(directory, image_path) 


state = SessionState.get(image_path="")

path = select_image()
if path: 
	state.image_path = path


try:
	st.write(state.image_path)
	image = P.load_and_preprocess(state.image_path)
	num_slices = image.shape[0]
	slice_index = st.slider("Slice", min_value=None, max_value=num_slices - 1, value=num_slices // 2, help='test')
	st.image(image[slice_index])
except ValueError:
	st.title("Select a path to a tiff image")
	st.write(state.image_path)




