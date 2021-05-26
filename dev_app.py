import os
import numpy as np
import streamlit as st
from typing import Tuple, List
import preprocess as P
import SessionState
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


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


def slice_in_3D(ax, i, shape):
    # From https://stackoverflow.com/questions/44881885/python-draw-3d-cube
    Z = np.array([[0, 0, 0],
                  [1, 0, 0],
                  [1, 1, 0],
                  [0, 1, 0],
                  [0, 0, 1],
                  [1, 0, 1],
                  [1, 1, 1],
                  [0, 1, 1]])

    Z = Z * shape
    r = [-1, 1]
    X, Y = np.meshgrid(r, r)

    # Plot vertices
    ax.scatter3D(Z[:, 0], Z[:, 1], Z[:, 2])

    # List sides' polygons of figure
    verts = [[Z[0], Z[1], Z[2], Z[3]],
             [Z[4], Z[5], Z[6], Z[7]],
             [Z[0], Z[1], Z[5], Z[4]],
             [Z[2], Z[3], Z[7], Z[6]],
             [Z[1], Z[2], Z[6], Z[5]],
             [Z[4], Z[7], Z[3], Z[0]],
             [Z[2], Z[3], Z[7], Z[6]]]

    # Plot sides
    ax.add_collection3d(
        Poly3DCollection(
            verts,
            facecolors=(1, 1, 1, 0.25),
            linewidths=1,
            edgecolors="black"
        )
    )

    verts = np.array([[[0, 0, 0],
                       [0, 0, 1],
                       [0, 1, 1],
                       [0, 1, 0]]])
    verts = verts * shape
    verts += [i, 0, 0]

    ax.add_collection3d(
        Poly3DCollection(
            verts,
            facecolors="pink",
            linewidths=1,
            edgecolors="black"
        )
    )

    ax.set_xlabel("plane")
    ax.set_xlim(0, 100)
    ax.set_ylabel("row")
    ax.set_zlabel("col")

    # Autoscale plot axes
    scaling = np.array([getattr(ax, f'get_{dim}lim')() for dim in "xyz"])
    ax.auto_scale_xyz(* [[np.min(scaling), np.max(scaling)]] * 3)


state = SessionState.get(image_path="")

path = select_image()
if path: 
	state.image_path = path

try:

	image = P.load_and_preprocess(state.image_path)
	n_plane, n_col, n_row = image.shape
	
	plane_index = st.slider("Plane",  min_value=None, max_value=n_plane - 1, value=n_plane // 2, help='xy')
	col_index   = st.slider("Column", min_value=None, max_value=n_col - 1,   value=n_col // 2,   help='yz')
	row_index   = st.slider("Row",   min_value=None, max_value=n_row - 1,    value=n_row // 2,   help='xz')

	fig = plt.figure()
	xy = plt.subplot2grid((3, 3), (0, 0), rowspan=2, colspan=2)
	yz = plt.subplot2grid((3, 3), (0, 2), rowspan=2, colspan=1)
	xz = plt.subplot2grid((3, 3), (2, 0), rowspan=1, colspan=2)
	cube = plt.subplot2grid((3, 3), (2, 2), rowspan=1, colspan=1, projection="3d")

	xy.imshow(image[plane_index], cmap='gray')
	yz.imshow(image[:, col_index, :].transpose(1, 0), cmap='gray')
	xz.imshow(image[:, :, row_index], cmap='gray')
	slice_in_3D(cube, plane_index, image.shape)

	plt.tight_layout()

	# st.image(image[slice_index])
	st.pyplot(fig)

except ValueError:

	st.title("Select a path to a tiff image")




