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

try:
    MPU_SENSOR = mpu6050(0x68)
    print("MPU6050 Initialized.")
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

pitch = 0.0
roll = 0.0
last_update = time.time()
alpha = 0.98

async def sensor_data_streamer(websocket: WebSocket):
    global pitch, roll, last_update
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

        roll_deg = 0.0
        pitch_deg = 0.0

        if MPU_SENSOR:
            try:
                accel_data = MPU_SENSOR.get_accel_data()
                gyro_data = MPU_SENSOR.get_gyro_data()

                accel_x = accel_data['x']
                accel_y = accel_data['y']
                accel_z = accel_data['z']

                gyro_x = gyro_data['x']
                gyro_y = gyro_data['y']

                accel_roll = math.degrees(math.atan2(accel_y, math.sqrt(accel_x**2 + accel_z**2)))
                accel_pitch = math.degrees(math.atan2(-accel_x, math.sqrt(accel_y**2 + accel_z**2)))

                roll = alpha * (roll + gyro_x * dt) + (1 - alpha) * accel_roll
                pitch = alpha * (pitch + gyro_y * dt) + (1 - alpha) * accel_pitch
                
                roll_deg = roll
                pitch_deg = pitch

            except Exception as e:
                roll_deg = -999
                pitch_deg = -999
        
        data_packet = {
            "timestamp": timestamp_utc,
            "tof_distance_mm": distance_mm,
            "roll": roll_deg,
            "pitch": pitch_deg,
            "yaw": 0 
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
        uvicorn.run(app, host="0.0.0.0", port=5002)
    finally:
        if TOF_SENSOR:
            print("Stopping TOF sensor.")
            TOF_SENSOR.stop_ranging()
            TOF_SENSOR.close()