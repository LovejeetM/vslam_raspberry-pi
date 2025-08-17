import numpy as np


def calculate_scaled_depth_map(relative_depth_map, lidar_distance_m, aoi_size=5):
    if lidar_distance_m <= 0.01:
        return None
    h, w = relative_depth_map.shape
    center_y, center_x = h // 2, w // 2
    half_aoi = aoi_size // 2
    aoi = relative_depth_map[center_y-half_aoi:center_y+half_aoi+1, center_x-half_aoi:center_x+half_aoi+1]
    relative_depth_at_center = np.median(aoi)
    if relative_depth_at_center < 1e-6:
        return None
    scale_factor = lidar_distance_m / relative_depth_at_center
    absolute_depth_map = relative_depth_map.astype(np.float32) * scale_factor
    return absolute_depth_map