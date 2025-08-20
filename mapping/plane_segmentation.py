import open3d as o3d
import numpy as np
import random
import time


class LiveVisualizer:
    def __init__(self, window_title="live map"):
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


def segment_and_color_planes(pcd, distance_threshold=0.02, min_points=100):
    segmented_pcd = o3d.geometry.PointCloud()
    points_to_segment = np.asarray(pcd.points)
    colors_to_segment = np.asarray(pcd.colors)
    
    while len(points_to_segment) > min_points:
        temp_pcd = o3d.geometry.PointCloud()
        temp_pcd.points = o3d.utility.Vector3dVector(points_to_segment)
        temp_pcd.colors = o3d.utility.Vector3dVector(colors_to_segment)
        plane_model, inliers = temp_pcd.segment_plane(distance_threshold=distance_threshold, ransac_n=3, num_iterations=1000)
        if len(inliers) < min_points:
            break
        plane_color = [random.random(), random.random(), random.random()]
        plane_points = points_to_segment[inliers]
        plane_pcd = o3d.geometry.PointCloud()
        plane_pcd.points = o3d.utility.Vector3dVector(plane_points)
        plane_pcd.paint_uniform_color(plane_color)
        segmented_pcd += plane_pcd
        points_to_segment = np.delete(points_to_segment, inliers, axis=0)
        colors_to_segment = np.delete(colors_to_segment, inliers, axis=0)
    
    remaining_pcd = o3d.geometry.PointCloud()
    remaining_pcd.points = o3d.utility.Vector3dVector(points_to_segment)
    remaining_pcd.colors = o3d.utility.Vector3dVector(colors_to_segment)
    segmented_pcd += remaining_pcd
    
    return segmented_pcd



visualizer = LiveVisualizer("map with plane Segmentation")


full_map_pcd = o3d.geometry.PointCloud()


frame_count = 0
SEGMENT_EVERY_N_FRAMES = 20 


pcd_to_display = o3d.geometry.PointCloud()

try:
    while True:
        
        new_points = np.random.rand(500, 3)
        full_map_pcd.points.extend(o3d.utility.Vector3dVector(new_points))
        

        if frame_count % SEGMENT_EVERY_N_FRAMES == 0:
            # print(f"Frame {frame_count}")
            
            downsampled_pcd = full_map_pcd.voxel_down_sample(voxel_size=0.05)
            pcd_to_display = segment_and_color_planes(downsampled_pcd)
        
        
        if not pcd_to_display.has_points():
             is_running = visualizer.update(full_map_pcd)
        else:
             is_running = visualizer.update(pcd_to_display)
        
        if not is_running:
            break
        
        frame_count += 1
        time.sleep(0.05)

finally:
    visualizer.close()
    