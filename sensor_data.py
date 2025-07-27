import asyncio
import json
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from mpu6050 import mpu6050
import VL53L0X

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
    TOF_SENSOR.start_ranging(VL53L0X.Vl5l3l0xAccuracyMode.LONG_RANGE)
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


app = FastAPI()


async def sensor_data_streamer(websocket: WebSocket):
    while True:
        timestamp_utc = datetime.now(timezone.utc).isoformat()

        distance_mm = -1
        if TOF_SENSOR:
            try:
                distance_mm = TOF_SENSOR.get_distance()
            except Exception:
                distance_mm = -2

        accel_data = None
        gyro_data = None
        if MPU_SENSOR:
            try:
                accel_data = MPU_SENSOR.get_accel_data()
                gyro_data = MPU_SENSOR.get_gyro_data()
            except Exception:
                accel_data = {"x": -999, "y": -999, "z": -999}
                gyro_data = {"x": -999, "y": -999, "z": -999}

        data_packet = {
            "timestamp": timestamp_utc,
            "tof_distance_mm": distance_mm,
            "accelerometer": accel_data,
            "gyroscope": gyro_data
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