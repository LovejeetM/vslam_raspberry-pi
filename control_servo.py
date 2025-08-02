# This lets you control servo movement over the internet for testing.
### It creates a realtime socket connection with the tunnel and streams movements data in realtime
### The latency is gives is 20 ms - 50 ms ~ using cloudflared tunnel
### The web page linked to it is present in side the templates folder

# This code is more faster and efficient than the flask code i previously had. 

import pigpio
import time
import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

SERVO_H_PIN = 8
SERVO_V_PIN = 7
PI_HOST = 'localhost'
# make sure to run pigpio on port 5001 or change it if its occupied. 
pi_port = 5001

pi = pigpio.pi(PI_HOST, pi_port)

PULSE_H_CENTER = 1440
PULSE_H_MIN = 500
PULSE_H_MAX = 2240
PULSE_V_CENTER = 1580
PULSE_V_MIN = 500
PULSE_V_MAX = 2160

SPEED_FACTOR = 450

pulse_h_current = PULSE_H_CENTER
pulse_v_current = PULSE_V_CENTER
h_velocity = 0.0
v_velocity = 0.0

html_content = ""
with open("templates/index.html", "r") as f:
    html_content = f.read()

def stop_servos_and_cleanup():
    print("Centering servos and cleaning up.")
    if pi.connected:
        pi.set_servo_pulsewidth(SERVO_H_PIN, PULSE_H_CENTER)
        pi.set_servo_pulsewidth(SERVO_V_PIN, PULSE_V_CENTER)
        time.sleep(1)
        pi.set_servo_pulsewidth(SERVO_H_PIN, 0)
        pi.set_servo_pulsewidth(SERVO_V_PIN, 0)
        pi.stop()

def set_initial_position():
    global pulse_h_current, pulse_v_current
    pulse_h_current = PULSE_H_CENTER
    pulse_v_current = PULSE_V_CENTER
    pi.set_servo_pulsewidth(SERVO_H_PIN, PULSE_H_CENTER)
    pi.set_servo_pulsewidth(SERVO_V_PIN, PULSE_V_CENTER)

async def servo_updater_task():
    global pulse_h_current, pulse_v_current
    while True:
        delta_h = h_velocity * SPEED_FACTOR * 0.02
        delta_v = v_velocity * SPEED_FACTOR * 0.02

        pulse_h_current -= delta_h
        pulse_v_current -= delta_v
        
        pulse_h_current = max(PULSE_H_MIN, min(PULSE_H_MAX, pulse_h_current))
        pulse_v_current = max(PULSE_V_MIN, min(PULSE_V_MAX, pulse_v_current))
            
        pi.set_servo_pulsewidth(SERVO_H_PIN, int(pulse_h_current))
        pi.set_servo_pulsewidth(SERVO_V_PIN, int(pulse_v_current))
            
        await asyncio.sleep(0.02)

@app.on_event("startup")
async def startup_event():
    if not pi.connected:
        print("Could not connect to pigpio daemon. Make sure its running on correct port.")
        exit()
    asyncio.create_task(servo_updater_task())

@app.get("/")
async def get():
    return HTMLResponse(html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global h_velocity, v_velocity
    await websocket.accept()
    print("Client connected.")
    set_initial_position()
    try:
        while True:
            data = await websocket.receive_json()
            h_velocity = data.get('x', 0.0)
            v_velocity = data.get('y', 0.0)
    except WebSocketDisconnect:
        h_velocity = 0.0
        v_velocity = 0.0
        print("Client disconnected.")

if __name__ == '__main__':
    try:
        uvicorn.run(app, host='0.0.0.0', port=5000)
    except (KeyboardInterrupt, SystemExit):
        print("Program interrupted...")
    finally:
        stop_servos_and_cleanup()
