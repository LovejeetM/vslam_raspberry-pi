import open3d as o3d
import numpy as np
import time

class AdvancedLiveVisualizer:
    def __init__(self, window_title="live map"):
        self.is_showing_mesh = False
        self.geometry = o3d.geometry.PointCloud()
        self.is_first_frame = True
        
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(window_name=window_title)
        
        opt = self.vis.get_render_option()
        opt.background_color = np.asarray([0.1, 0.1, 0.1])
        opt.point_size = 2.0
        opt.mesh_show_back_face = True

    def update(self, tsdf_volume, frame_count, update_mesh_every_n_frames=30):
        if frame_count % update_mesh_every_n_frames == 0:
            print("Generating high-quality mesh:")
            new_geometry = tsdf_volume.extract_triangle_mesh()
            new_geometry.compute_vertex_normals()
            self.is_showing_mesh = True
        else:
            pcd = tsdf_volume.extract_point_cloud()
            new_geometry = pcd.voxel_down_sample(voxel_size=0.02)
            self.is_showing_mesh = False

        self.vis.remove_geometry(self.geometry, reset_bounding_box=False)
        self.geometry = new_geometry
        self.vis.add_geometry(self.geometry, reset_bounding_box=False)

        if self.is_first_frame:
            self.vis.reset_view_point(True)
            self.is_first_frame = False

        is_window_open = self.vis.poll_events()
        self.vis.update_renderer()
        return is_window_open

    def close(self):
        self.vis.destroy_window()


voxel_size = 0.015
tsdf_volume = o3d.pipelines.integration.ScalableTSDFVolume(
    voxel_length=voxel_size,
    sdf_trunc=0.04,
    color_type=o3d.pipelines.integration.TSDFVolumeColorType.RGB8
)


visualizer = AdvancedLiveVisualizer()
frame_count = 0

try:
    
    while True:
        
        simulated_pcd = o3d.geometry.PointCloud()
        simulated_pcd.points = o3d.utility.Vector3dVector(np.random.rand(1000, 3))
        tsdf_volume.integrate(
            o3d.geometry.RGBDImage(), 
            o3d.camera.PinholeCameraIntrinsic(o3d.camera.PinholeCameraIntrinsicParameters.PrimeSenseDefault), 
            np.eye(4)
        )
        
        is_running = visualizer.update(tsdf_volume, frame_count)
        if not is_running:
            break
        
        frame_count += 1
        # time.sleep(0.01) 

finally:
    # print("Saving to 'final_map.ply'.")
    final_mesh = tsdf_volume.extract_triangle_mesh()
    final_mesh.compute_vertex_normals()
    o3d.io.write_triangle_mesh("final_map.ply", final_mesh)
    visualizer.close()