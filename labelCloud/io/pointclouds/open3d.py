from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple

import numpy as np
import open3d as o3d

from . import BasePointCloudHandler

if TYPE_CHECKING:
    from ...model import PointCloud


class Open3DHandler(BasePointCloudHandler):
    EXTENSIONS = {".pcd", ".ply", ".pts", ".xyz", ".xyzn", ".xyzrgb"}

    def __init__(self) -> None:
        super().__init__()

    def to_point_cloud(
        self, pointcloud: o3d.geometry.PointCloud
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        return (
            np.asarray(pointcloud.points).astype("float32"),
            np.asarray(pointcloud.colors).astype("float32"),
        )

    def to_open3d_point_cloud(
        self, pointcloud: "PointCloud"
    ) -> o3d.geometry.PointCloud:
        o3d_pointcloud = o3d.geometry.PointCloud(
            o3d.utility.Vector3dVector(pointcloud.points)
        )
        o3d_pointcloud.colors = o3d.utility.Vector3dVector(pointcloud.colors)
        return o3d_pointcloud

    #def read_point_cloud(self, path: Path) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    #    super().read_point_cloud(path)
    #    return self.to_point_cloud(
    #        o3d.io.read_point_cloud(str(path), remove_nan_points=True)
    #    )

    def read_point_cloud(self, path: Path) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        super().read_point_cloud(path)
        points = np.loadtxt(path, skiprows=10).astype(np.float32)
        return (points[:,:3], None)

    def write_point_cloud(self, path: Path, pointcloud: "PointCloud") -> None:
        super().write_point_cloud(path, pointcloud)
        o3d.io.write_point_cloud(str(path), self.to_open3d_point_cloud(pointcloud))
