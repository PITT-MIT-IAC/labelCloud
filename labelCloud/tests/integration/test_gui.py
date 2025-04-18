import logging
import os

from labelCloud.control.config_manager import config
from PyQt5 import QtCore
from PyQt5.QtWidgets import QAbstractSlider


def test_gui(qtbot, startup_pyqt):
    view, controller = startup_pyqt

    assert len(controller.pcd_manager.pcds) > 0
    os.remove("labels/exemplary.json")
    qtbot.mouseClick(view.button_next_pcd, QtCore.Qt.LeftButton, delay=0)
    assert "exemplary.json" in os.listdir("labels")

    bbox = controller.bbox_controller.bboxes[0]
    bbox.center = (0, 0, 0)
    controller.bbox_controller.set_active_bbox(0)
    qtbot.mouseClick(view.button_right, QtCore.Qt.LeftButton, delay=0)
    qtbot.mouseClick(view.button_up, QtCore.Qt.LeftButton, delay=0)
    qtbot.mouseClick(view.button_backward, QtCore.Qt.LeftButton, delay=0)
    assert bbox.center == (0.03, 0.03, 0.03)

    view.close()


def test_bbox_control_with_buttons(qtbot, startup_pyqt, bbox):
    view, controller = startup_pyqt

    # Prepare test bounding box
    controller.bbox_controller.bboxes = [bbox]
    old_length, old_width, old_height = bbox.get_dimensions()
    controller.bbox_controller.set_active_bbox(0)

    # Translation
    translation_step = config.getfloat("LABEL", "std_translation")
    qtbot.mouseClick(view.button_right, QtCore.Qt.LeftButton, delay=0)
    qtbot.mouseClick(view.button_up, QtCore.Qt.LeftButton, delay=0)
    qtbot.mouseClick(view.button_backward, QtCore.Qt.LeftButton, delay=0)
    assert bbox.center == (translation_step, translation_step, translation_step)
    qtbot.mouseClick(view.button_left, QtCore.Qt.LeftButton, delay=0)
    qtbot.mouseClick(view.button_down, QtCore.Qt.LeftButton, delay=0)
    qtbot.mouseClick(view.button_forward, QtCore.Qt.LeftButton)
    logging.info("BBOX: %s" % [str(c) for c in bbox.get_center()])
    assert bbox.center == (0.00, 0.00, 0.00)

    # Scaling
    scaling_step = config.getfloat("LABEL", "std_scaling")
    qtbot.mouseClick(view.button_incr_dim, QtCore.Qt.LeftButton)
    assert bbox.length == old_length + scaling_step
    assert bbox.width == old_width / old_length * bbox.length
    assert bbox.height == old_height / old_length * bbox.length

    # Rotation
    # TODO: Make dial configureable?
    view.dial_zrotation.triggerAction(QAbstractSlider.SliderSingleStepAdd)
    assert bbox.z_rotation == 1
    view.dial_zrotation.triggerAction(QAbstractSlider.SliderPageStepAdd)
    assert bbox.z_rotation == 11

    view.close()


def test_bbox_control_with_keyboard(qtbot, startup_pyqt, qapp, bbox):
    view, controller = startup_pyqt

    # Prepare test bounding box
    controller.bbox_controller.bboxes = [bbox]
    controller.bbox_controller.set_active_bbox(0)

    # Translation
    translation_step = config.getfloat("LABEL", "std_translation")
    for letter in "dqw":
        qtbot.keyClick(view, letter)
    assert bbox.center == (translation_step, translation_step, translation_step)
    translation_step = config.getfloat("LABEL", "std_translation")
    for letter in "aes":
        qtbot.keyClick(view, letter)
    assert bbox.center == (0, 0, 0)

    for key in [QtCore.Qt.Key_Right, QtCore.Qt.Key_Up, QtCore.Qt.Key_PageUp]:
        qtbot.keyClick(view, key)
    assert bbox.center == (translation_step, translation_step, translation_step)
    for key in [QtCore.Qt.Key_Left, QtCore.Qt.Key_Down, QtCore.Qt.Key_PageDown]:
        qtbot.keyClick(view, key)
    assert bbox.center == (0, 0, 0)

    # Rotation
    rotation_step = config.getfloat("LABEL", "std_rotation")
    config.set("USER_INTERFACE", "z_rotation_only", "False")
    qtbot.keyClick(view, "y")
    assert bbox.z_rotation == rotation_step
    qtbot.keyClick(view, "x")
    assert bbox.z_rotation == 0
    qtbot.keyClick(view, QtCore.Qt.Key_Comma)
    assert bbox.z_rotation == rotation_step
    qtbot.keyClick(view, QtCore.Qt.Key_Period)
    assert bbox.z_rotation == 0
    qtbot.keyClick(view, "c")
    assert bbox.y_rotation == rotation_step
    qtbot.keyClick(view, "v")
    assert bbox.y_rotation == 0
    qtbot.keyClick(view, "b")
    assert bbox.x_rotation == rotation_step
    qtbot.keyClick(view, "n")
    assert bbox.x_rotation == 0

    # Shortcuts
    qtbot.keyClick(view, QtCore.Qt.Key_Delete)
    assert len(controller.bbox_controller.bboxes) == 0
    assert controller.bbox_controller.get_active_bbox() is None

    view.close()
