# This lets you control servo movement over the internet for testing.
### It creates a realtime socket connection with the tunnel and streams movements data in realtime
### The lstency is gives is 20 ms - 50 ms ~ using cloudflared tunnel
### The web page linked to it is present in side the templates folder


import pigpio
import time
import atexit
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

SERVO_H_PIN = 8
SERVO_V_PIN = 7
PI_HOST = 'localhost'
pi_port = 5001

pi = pigpio.pi(PI_HOST, pi_port)

PULSE_H_CENTER = 1440
PULSE_H_MIN = 500
PULSE_H_MAX = 2040
PULSE_V_CENTER = 1580
PULSE_V_MIN = 420
PULSE_V_MAX = 1960


SPEED_FACTOR = 400  #150

pulse_h_current = PULSE_H_CENTER
pulse_v_current = PULSE_V_CENTER
h_velocity = 0.0
v_velocity = 0.0
update_lock = threading.Lock()

def stop_servos_and_cleanup():
    print("Centering servos and cleaning up.")
    pi.set_servo_pulsewidth(SERVO_H_PIN, PULSE_H_CENTER)
    pi.set_servo_pulsewidth(SERVO_V_PIN, PULSE_V_CENTER)
    time.sleep(1)
    pi.set_servo_pulsewidth(SERVO_H_PIN, 0)
    pi.set_servo_pulsewidth(SERVO_V_PIN, 0)
    pi.stop()

def set_initial_position():
    with update_lock:
        global pulse_h_current, pulse_v_current
        pulse_h_current = PULSE_H_CENTER
        pulse_v_current = PULSE_V_CENTER
    pi.set_servo_pulsewidth(SERVO_H_PIN, PULSE_H_CENTER)
    pi.set_servo_pulsewidth(SERVO_V_PIN, PULSE_V_CENTER)


def servo_updater_thread():
    global pulse_h_current, pulse_v_current
    while True:
        with update_lock:
            delta_h = h_velocity * SPEED_FACTOR * 0.02
            delta_v = v_velocity * SPEED_FACTOR * 0.02

            pulse_h_current += delta_h
            pulse_v_current += delta_v

            pulse_h_current = max(PULSE_H_MIN, min(PULSE_H_MAX, pulse_h_current))
            pulse_v_current = max(PULSE_V_MIN, min(PULSE_V_MAX, pulse_v_current))

            pi.set_servo_pulsewidth(SERVO_H_PIN, int(pulse_h_current))
            pi.set_servo_pulsewidth(SERVO_V_PIN, int(pulse_v_current))

        time.sleep(0.02)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    set_initial_position()

@socketio.on('joystick_move')
def handle_joystick_move(data):
    global h_velocity, v_velocity
    with update_lock:
        h_velocity = -data.get('x', 0.0)
        v_velocity = -data.get('y', 0.0)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    if not pi.connected:
        print("Could not connect to pigpio daemon. Make sure its running on port 5001.")
        exit()

        
    atexit.register(stop_servos_and_cleanup)

    updater_thread = threading.Thread(target=servo_updater_thread, daemon=True)
    updater_thread.start()

    print("Starting Flask server...")
    socketio.run(app, host='0.0.0.0', port=5000)
