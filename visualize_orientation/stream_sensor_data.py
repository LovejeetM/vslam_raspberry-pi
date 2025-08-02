import asyncio
import json
import time
import math
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from mpu6050 import mpu6050
import VL53L0X

app = FastAPI()

TOF_SENSOR = None
MPU_SENSOR = None
TOF_TIMING = 20000
STREAM_INTERVAL_SECONDS = 0.05

gyro_offset = {'x': 0, 'y': 0, 'z': 0}
initial_orientation = {'roll': 0, 'pitch': 0}

pitch = 0.0
roll = 0.0
yaw = 0.0
last_update = time.time()
alpha = 0.98

def calibrate_sensors():
    global MPU_SENSOR, gyro_offset, initial_orientation
    if not MPU_SENSOR:
        print("MPU6050 not available. Skipping calibration.")
        return

    print("Calibrating MPU6050... Please keep the sensor perfectly still.")
    
    gyro_x_sum = 0
    gyro_y_sum = 0
    gyro_z_sum = 0
    
    roll_sum = 0
    pitch_sum = 0
    
    num_samples = 200
    
    for _ in range(num_samples):
        try:
            gyro_data = MPU_SENSOR.get_gyro_data()
            accel_data = MPU_SENSOR.get_accel_data()
            
            gyro_x_sum += gyro_data['x']
            gyro_y_sum += gyro_data['y']
            gyro_z_sum += gyro_data['z']
            
            accel_x = accel_data['x']
            accel_y = accel_data['y']
            accel_z = accel_data['z']
            
            roll_sum += math.degrees(math.atan2(accel_y, math.sqrt(accel_x**2 + accel_z**2)))
            pitch_sum += math.degrees(math.atan2(-accel_x, math.sqrt(accel_y**2 + accel_z**2)))

        except Exception as e:
            print(f"Error during calibration sample: {e}")
            return
        time.sleep(0.01)
        
    gyro_offset['x'] = gyro_x_sum / num_samples
    gyro_offset['y'] = gyro_y_sum / num_samples
    gyro_offset['z'] = gyro_z_sum / num_samples

    initial_orientation['roll'] = roll_sum / num_samples
    initial_orientation['pitch'] = pitch_sum / num_samples
    
    print("Calibration Complete.")
    print(f"Gyro Offsets (x, y, z): {gyro_offset['x']:.2f}, {gyro_offset['y']:.2f}, {gyro_offset['z']:.2f}")
    print(f"Initial Orientation (Roll, Pitch): {initial_orientation['roll']:.2f}, {initial_orientation['pitch']:.2f}")


try:
    MPU_SENSOR = mpu6050(0x68)
    print("MPU6050 Initialized.")
    calibrate_sensors()
except Exception as e:
    print(f"Failed to initialize MPU6050: {e}")
    MPU_SENSOR = None

try:
    TOF_SENSOR = VL53L0X.VL53L0X(i2c_bus=1, i2c_address=0x29)
    TOF_SENSOR.open()
    TOF_SENSOR.start_ranging(VL53L0X.Vl53l0xAccuracyMode.LONG_RANGE)
    timing = TOF_SENSOR.get_timing()
    if timing < 20000:
        TOF_TIMING = 20000
    else:
        TOF_TIMING = timing
    print(f"VL53L0X Initialized.")
except Exception as e:
    print(f"Failed to initialize VL53L0X: {e}")
    if TOF_SENSOR:
        TOF_SENSOR.stop_ranging()
        TOF_SENSOR.close()
    TOF_SENSOR = None

roll = initial_orientation['roll']
pitch = initial_orientation['pitch']

async def sensor_data_streamer(websocket: WebSocket):
    global pitch, roll, yaw, last_update
    while True:
        timestamp_utc = datetime.now(timezone.utc).isoformat()
        current_time = time.time()
        dt = current_time - last_update
        last_update = current_time

        distance_mm = -1
        if TOF_SENSOR:
            try:
                distance_mm = TOF_SENSOR.get_distance()
            except Exception:
                distance_mm = -2

        if MPU_SENSOR:
            try:
                accel_data = MPU_SENSOR.get_accel_data()
                gyro_data = MPU_SENSOR.get_gyro_data()

                gyro_x = gyro_data['x'] - gyro_offset['x']
                gyro_y = gyro_data['y'] - gyro_offset['y']
                gyro_z = gyro_data['z'] - gyro_offset['z']
                
                accel_x = accel_data['x']
                accel_y = accel_data['y']
                accel_z = accel_data['z']

                accel_roll = math.degrees(math.atan2(accel_y, math.sqrt(accel_x**2 + accel_z**2)))
                accel_pitch = math.degrees(math.atan2(-accel_x, math.sqrt(accel_y**2 + accel_z**2)))

                pitch = alpha * (pitch + gyro_x * dt) + (1 - alpha) * accel_pitch
                roll = alpha * (roll + gyro_y * dt) + (1 - alpha) * accel_roll
                yaw += gyro_z * dt

            except Exception:
                pass
        
        data_packet = {
            "timestamp": timestamp_utc,
            "tof_distance_mm": distance_mm,
            "roll": roll - initial_orientation['roll'],
            "pitch": pitch - initial_orientation['pitch'],
            "yaw": yaw 
        }

        await websocket.send_text(json.dumps(data_packet))
        await asyncio.sleep(STREAM_INTERVAL_SECONDS)


@app.websocket("/sensordata")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected.")
    try:
        await sensor_data_streamer(websocket)
    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"error: {e}")
    finally:
        if TOF_SENSOR:
            TOF_SENSOR.stop_ranging()
        print("connection closed.")


@app.get("/")
def read_root():
    return {"status": "Sensor streaming server is running. Connect to /sensordata"}


if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=5000)
    finally:
        if TOF_SENSOR:
            print("Stopping TOF sensor.")
            TOF_SENSOR.stop_ranging()
            TOF_SENSOR.close()