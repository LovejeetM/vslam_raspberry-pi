import open3d as o3d
import numpy as np

class LiveVisualizer:
    def __init__(self, window_title="live vis"):
        self.pcd = o3d.geometry.PointCloud()
        self.is_first_frame = True
        
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(window_name=window_title)
        
        opt = self.vis.get_render_option()
        opt.background_color = np.asarray([0.1, 0.1, 0.1])
        opt.point_size = 1.5

    def update(self, new_pcd_data):
        self.pcd.points = new_pcd_data.points
        self.pcd.colors = new_pcd_data.colors

        if self.is_first_frame:
            self.vis.add_geometry(self.pcd)
            self.is_first_frame = False
        else:
            self.vis.update_geometry(self.pcd)

        is_window_open = self.vis.poll_events()
        self.vis.update_renderer()
        return is_window_open

    def close(self):
        self.vis.destroy_window()

