"""
Alignify! v1.0.0
Manual stack alignment tool

Author: Kristoffer Jonsson
Created: 2026-04-14

Features:
- Frame-by-frame translational alignment
- Centered rotational alignment
- Fine/coarse continuous rotation controls
- Save aligned output stack

Built in Python using napari
"""

import base64
import numpy as np
from skimage import io
from scipy.ndimage import affine_transform
import napari
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

from qtpy.QtWidgets import (
    QSlider,
    QVBoxLayout,
    QWidget,
    QApplication,
    QLabel
)
from qtpy.QtCore import QObject, Qt, QTimer, QEvent
from qtpy.QtGui import QPixmap, QIcon
from napari.utils.transforms import Affine


# ----------------------------
# Embedded Logo
# ----------------------------
LOGO_B64 = """
iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAACXBIWXMAAAsTAAALEwEAmpwYAAAE8WlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgMTAuMC1jMDAwIDI1LkcuZDIwZTQ2NiwgMjAyNS8xMi8wOC0yMDo1MDoyMSAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iIHhtbG5zOnBob3Rvc2hvcD0iaHR0cDovL25zLmFkb2JlLmNvbS9waG90b3Nob3AvMS4wLyIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0RXZ0PSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VFdmVudCMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIDI3LjUgKFdpbmRvd3MpIiB4bXA6Q3JlYXRlRGF0ZT0iMjAyNi0wNC0xNFQxNDo0MDoyNSswMjowMCIgeG1wOk1vZGlmeURhdGU9IjIwMjYtMDQtMTZUMTI6MDU6MjkrMDI6MDAiIHhtcDpNZXRhZGF0YURhdGU9IjIwMjYtMDQtMTZUMTI6MDU6MjkrMDI6MDAiIGRjOmZvcm1hdD0iaW1hZ2UvcG5nIiBwaG90b3Nob3A6Q29sb3JNb2RlPSIzIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjMxYWYyNmQzLTYyMzUtMTQ0NS05YTI4LWI0OGYxODRlOWJiMCIgeG1wTU06RG9jdW1lbnRJ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"""


def pixmap_from_b64(b64_string):
    raw = base64.b64decode(b64_string)
    pix = QPixmap()
    if not pix.loadFromData(raw):
        raise RuntimeError("Failed to decode logo image.")
    return pix


# ----------------------------
# File selection
# ----------------------------
Tk().withdraw()

stack_path = askopenfilename(
    title="Select TIFF stack",
    filetypes=[("TIFF files", "*.tif;*.tiff")]
)
if not stack_path:
    raise RuntimeError("No file selected.")

output_path = asksaveasfilename(
    title="Save aligned stack as",
    defaultextension=".tif",
    filetypes=[("TIFF files", "*.tif;*.tiff")]
)
if not output_path:
    raise RuntimeError("No output file selected.")


# ----------------------------
# Load stack
# ----------------------------
stack = io.imread(stack_path)
n_frames, height, width = stack.shape

translations = [(0.0, 0.0) for _ in range(n_frames)]
rotations = [0.0 for _ in range(n_frames)]

current_frame = 1


# ----------------------------
# Viewer Setup
# ----------------------------
viewer = napari.Viewer()

app = QApplication.instance()
if app is not None:
    app.setApplicationName("Alignify!")

viewer.window._qt_window.setWindowTitle("Alignify!")

# Set taskbar/window icon
app_icon_pix = pixmap_from_b64(LOGO_B64)
app_icon = QIcon(app_icon_pix)
viewer.window._qt_window.setWindowIcon(app_icon)
if app is not None:
    app.setWindowIcon(app_icon)

top_layer = None
bottom_layer = None


# ----------------------------
# Reference Grid
# ----------------------------
def add_reference_grid():
    pts = []
    for y in range(0, height, 50):
        for x in range(0, width, 50):
            pts.append([y, x])

    return viewer.add_points(
        np.array(pts),
        name="Reference Grid",
        size=3,
        face_color="yellow",
        opacity=0.35
    )


grid_layer = add_reference_grid()


# ----------------------------
# Affine transform
# ----------------------------
def build_affine_matrix(translation, rotation_deg):
    ty, tx = translation

    cy = height / 2.0
    cx = width / 2.0

    theta = np.deg2rad(rotation_deg)
    c = np.cos(theta)
    s = np.sin(theta)

    T1 = np.array([
        [1, 0, -cx],
        [0, 1, -cy],
        [0, 0, 1]
    ])

    R = np.array([
        [c, -s, 0],
        [s,  c, 0],
        [0,  0, 1]
    ])

    T2 = np.array([
        [1, 0, cx + tx],
        [0, 1, cy + ty],
        [0, 0, 1]
    ])

    return T2 @ R @ T1


def apply_transform(layer, t, r):
    layer.affine = Affine(affine_matrix=build_affine_matrix(t, r))


# ----------------------------
# Capture translation after drag
# ----------------------------
def capture_translation():
    global translations

    if top_layer is None:
        return

    M = top_layer.affine.affine_matrix
    tx, ty = M[0, 2], M[1, 2]

    cx, cy = width / 2.0, height / 2.0

    theta = np.deg2rad(rotations[current_frame])
    c, s = np.cos(theta), np.sin(theta)

    center_shift_x = cx - (c * cx - s * cy)
    center_shift_y = cy - (s * cx + c * cy)

    translations[current_frame] = (
        ty - center_shift_y,
        tx - center_shift_x
    )


# ----------------------------
# Update display
# ----------------------------
def update(frame):
    global current_frame, top_layer, bottom_layer

    capture_translation()
    current_frame = frame

    zoom = viewer.camera.zoom
    center = viewer.camera.center

    for l in list(viewer.layers):
        if l.name != "Reference Grid":
            viewer.layers.remove(l)

    if frame == 0:
        top_layer = viewer.add_image(
            stack[0],
            name="Frame 0",
            opacity=1.0
        )
        apply_transform(top_layer, translations[0], rotations[0])

    else:
        bottom_layer = viewer.add_image(
            stack[frame - 1],
            name=f"Frame {frame-1}",
            opacity=1.0,
            colormap="green"
        )
        apply_transform(
            bottom_layer,
            translations[frame - 1],
            rotations[frame - 1]
        )
        bottom_layer.editable = False

        top_layer = viewer.add_image(
            stack[frame],
            name=f"Frame {frame}",
            opacity=0.5,
            colormap="magenta"
        )
        apply_transform(
            top_layer,
            translations[frame],
            rotations[frame]
        )
        top_layer.editable = True

    viewer.camera.zoom = zoom
    viewer.camera.center = center
    viewer.layers.selection.active = top_layer


# ----------------------------
# Slider dock
# ----------------------------
slider_widget = QWidget()
slider_layout = QVBoxLayout()
slider_widget.setLayout(slider_layout)

slider = QSlider(Qt.Horizontal)
slider.setMinimum(0)
slider.setMaximum(n_frames - 1)
slider.setValue(current_frame)

slider_layout.addWidget(slider)
slider.valueChanged.connect(update)

viewer.window.add_dock_widget(
    slider_widget,
    area='bottom',
    name='Frame Slider'
)


# ----------------------------
# Controls panel dock
# ----------------------------
controls_widget = QWidget()
controls_layout = QVBoxLayout()
controls_widget.setLayout(controls_layout)

# Logo
logo_label = QLabel()
logo_pix = pixmap_from_b64(LOGO_B64).scaledToHeight(
    48,
    Qt.SmoothTransformation
)
logo_label.setPixmap(logo_pix)
logo_label.setAlignment(Qt.AlignCenter)

# Software name
title_label = QLabel("<h2>Alignify!</h2>")
title_label.setAlignment(Qt.AlignCenter)

# Spacer
spacer = QLabel("<br><br>")

# Controls text
controls_text = QLabel("""
<b>Controls</b><br><br>

1 = Move both layers<br>
2 = Move top layer only<br><br>

Q = Fine rotate CW<br>
E = Fine rotate CCW<br><br>

Shift+Q = Coarse rotate CW<br>
Shift+E = Coarse rotate CCW<br><br>

N = Next frame<br>
P = Previous frame<br><br>

G = Toggle grid<br>
S = Save aligned stack
""")

controls_text.setTextFormat(Qt.RichText)

controls_layout.addWidget(logo_label)
controls_layout.addWidget(title_label)
controls_layout.addWidget(spacer)
controls_layout.addWidget(controls_text)

viewer.window.add_dock_widget(
    controls_widget,
    area='right',
    name=''
)


# ----------------------------
# Navigation
# ----------------------------
@viewer.bind_key('n')
def next_frame(v):
    slider.setValue(min(current_frame + 1, n_frames - 1))


@viewer.bind_key('p')
def prev_frame(v):
    slider.setValue(max(current_frame - 1, 0))


@viewer.bind_key('g')
def toggle_grid(v):
    grid_layer.visible = not grid_layer.visible


# ----------------------------
# Rotation state
# ----------------------------
rot_left = False
rot_right = False
shift_held = False

fine_step = 0.1
coarse_step = 0.4


# ----------------------------
# Timer rotation engine
# ----------------------------
timer = QTimer()


def tick():
    if top_layer is None:
        return

    if rot_left or rot_right:
        capture_translation()

        step = coarse_step if shift_held else fine_step

        if rot_left:
            rotations[current_frame] -= step
        if rot_right:
            rotations[current_frame] += step

        apply_transform(
            top_layer,
            translations[current_frame],
            rotations[current_frame]
        )


timer.timeout.connect(tick)
timer.start(20)


# ----------------------------
# Key event filter
# ----------------------------
class KeyFilter(QObject):
    def eventFilter(self, obj, event):
        global rot_left, rot_right, shift_held

        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Q:
                rot_left = True
            elif event.key() == Qt.Key_E:
                rot_right = True
            elif event.key() == Qt.Key_Shift:
                shift_held = True

        elif event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_Q:
                rot_left = False
            elif event.key() == Qt.Key_E:
                rot_right = False
            elif event.key() == Qt.Key_Shift:
                shift_held = False

        return False


key_filter = KeyFilter()
app.installEventFilter(key_filter)


# ----------------------------
# Save aligned stack
# ----------------------------
def save():
    capture_translation()

    out = np.zeros_like(stack)

    for i in range(n_frames):
        M = build_affine_matrix(translations[i], rotations[i])
        inv = np.linalg.inv(M)

        out[i] = affine_transform(
            stack[i],
            matrix=inv[:2, :2],
            offset=inv[:2, 2],
            order=1
        )

    io.imsave(output_path, out)
    print("Saved aligned stack.")


@viewer.bind_key('s')
def save_key(v):
    save()


# ----------------------------
# Start
# ----------------------------
update(current_frame)
napari.run()
