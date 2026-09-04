# pwm_publisher

## 1. Introduction

&ensp;&ensp;This package is the deliverable for the **Week 3** mini-challenge of
TE3001B - Fundamentación de Robótica (MCR2 / Tecnológico de Monterrey): *"Crear un
controlador para regular velocidad de motor usando ROS"* ("Create a controller to
regulate motor speed using ROS"). Unlike the previous weeks, the plant here is a
**real DC motor**, driven by an ESP32 running micro-ROS instead of a simulation.

```
 ┌──────────┐  /cmd_pwm (Float32, [-1,1])   ┌─────────┐  PWM + Dir   ┌────────────┐   ┌─────────┐
 │ pwm_pub  │ ─────────────────────────────►│ /motor  │─────────────►│ L298N      │──►│ DC Motor│
 │ (ROS 2)  │                               │ (ESP32, │              │ Motor Drv  │   └─────────┘
 └──────────┘                               │ micro-ROS)             └────────────┘
```

&ensp;&ensp;This package only contains the **ROS 2 side** (`pwm_pub`), which runs on
the computer and publishes speed commands. The `/motor` node runs as C/C++ firmware
on the ESP32 — it is **not** part of this ROS 2 workspace, since it is flashed onto
the microcontroller rather than built with `colcon`. Its source,
[mcr2_mini_challenge3.ino](firmware/mcr2_mini_challenge3.ino), is kept here only as a
reference copy (the actual Arduino sketch lives outside this repo).

## 2. Nodes

- ### 2.1 pwm_pub
    &ensp;&ensp;Publishes a random PWM command in `[-1.0, 1.0]` on `/cmd_pwm` every
    5 seconds (the slow period makes each step easy to observe on the motor). See
    [pwm_pub.py](pwm_publisher/pwm_pub.py).

    | Topic       | Type                | I/O | Description                          |
    |-------------|---------------------|-----|-----------------------------------------|
    | `/cmd_pwm`  | `std_msgs/Float32`  | pub | Speed/direction command in `[-1, 1]`    |

## 3. External Node Reference — `/motor` (ESP32 firmware)

&ensp;&ensp;This section documents, for context only, the C/C++ micro-ROS node that
runs on the ESP32 and receives what `pwm_pub` sends. It is built with the
[micro-ros-arduino](https://github.com/micro-ROS/micro_ros_arduino) library and
flashed directly to the microcontroller — it is **not** a ROS 2 package, is not
compiled by `colcon`, and has no `package.xml`/`setup.py`. Its only touchpoint with
this repository is the topic contract it shares with `pwm_pub`: it creates a node
named `motor` and a subscriber on `cmd_pwm` (`std_msgs/Float32`).

- ### 3.1 Connection lifecycle
    &ensp;&ensp;The firmware implements a 4-state machine (`enum states`) in `loop()`
    so it survives the micro-ROS agent appearing, disappearing, and reappearing
    without ever needing a manual reset of the board:

    | State                | Meaning                                                              |
    |-----------------------|----------------------------------------------------------------------|
    | `WAITING_AGENT`       | No agent yet; pings every 500 ms via `rmw_uros_ping_agent`            |
    | `AGENT_AVAILABLE`     | Agent found; calls `create_entities()` to build the node/subscriber   |
    | `AGENT_CONNECTED`     | Entities live; pings every 200 ms and spins the executor to process incoming `/cmd_pwm` messages |
    | `AGENT_DISCONNECTED`  | Ping failed; calls `destroy_entities()` and falls back to `WAITING_AGENT` |

    &ensp;&ensp;Transport is **Serial** (`set_microros_transports()` in `setup()`),
    so the micro-ROS agent on the computer must be started with the `serial` backend
    (see [§6.2](#62-start-the-micro-ros-agent-connects-to-the-esp32-over-serial)).

- ### 3.2 Pin and PWM configuration
    &ensp;&ensp;Speed is output as a hardware PWM signal on one pin, direction as
    digital levels on two others, all set up in `setup()` via `ledcSetup` /
    `ledcAttachPin`:

    | Macro       | Value      | Purpose                                    |
    |-------------|------------|----------------------------------------------|
    | `PWM_PIN`   | `GPIO27`   | PWM output to the L298N `ENA` (speed)         |
    | `IN1`       | `GPIO25`   | L298N direction pin 1                         |
    | `IN2`       | `GPIO26`   | L298N direction pin 2                         |
    | `PWM_FRQ`   | `980 Hz`   | PWM carrier frequency                         |
    | `PWM_RES`   | `8 bits`   | PWM resolution → duty cycle range `0-255`     |
    | `PWM_CHNL`  | `0`        | ESP32 LEDC channel used for the PWM signal    |

- ### 3.3 Subscriber callback — `/cmd_pwm` → PWM + direction
    &ensp;&ensp;`subscription_callback()` fires on every message received on
    `cmd_pwm`. The incoming value is clamped to `[-1, 1]`, converted to a duty cycle,
    and used to set direction:

    ```
    cmd   = constrain(msg.data, -1, 1)
    duty  = (2^PWM_RES - 1) * |cmd|      # → 0-255
    ```

    | `cmd`     | `IN1` | `IN2` | Result                              |
    |-----------|-------|-------|----------------------------------------|
    | `> 0`     | HIGH  | LOW   | Forward, duty proportional to `\|cmd\|` |
    | `< 0`     | LOW   | HIGH  | Reverse, duty proportional to `\|cmd\|` |
    | `== 0`    | HIGH  | HIGH  | Brake (duty forced to `0`)              |

    &ensp;&ensp;The resulting duty cycle is written with `ledcWrite(PWM_CHNL, duty)`,
    driving the L298N which in turn drives the 12V DC motor.

&ensp;&ensp;Full source in [firmware/mcr2_mini_challenge3.ino](firmware/mcr2_mini_challenge3.ino);
wiring diagram (L298N to ESP32) is in the [report](report/).

## 4. Package Structure

```
pwm_publisher/
├── pwm_publisher/
│   └── pwm_pub.py          # PWM command publisher node
├── firmware/
│   └── mcr2_mini_challenge3.ino   # ESP32 /motor node (reference copy, not built by colcon)
├── report/                 # submitted report (PDF)
├── test/                   # style tests (flake8, pep257, copyright)
├── package.xml
└── setup.py
```

## 5. Requirements

- ROS 2 (Humble or compatible), with `rclpy` and `std_msgs`.
- `micro_ros_agent` running on the computer, bridging the ESP32 to ROS 2.
- An ESP32 flashed with the `/motor` micro-ROS firmware, wired to an L298N driver
  and a 12V DC motor (see [report](report/) for the wiring diagram).

## 6. How To Use

- ### 6.1 Build the package
    ```bash
    # from the workspace root
    colcon build --packages-select pwm_publisher
    source install/setup.bash
    ```

- ### 6.2 Start the micro-ROS agent (connects to the ESP32 over serial)
    ```bash
    ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0
    ```
    &ensp;&ensp;Wait until the ESP32 reaches `AGENT_CONNECTED` and `/motor` shows up
    in `ros2 node list`.

- ### 6.3 Manual test (single commands from the terminal)
    ```bash
    ros2 topic pub /cmd_pwm std_msgs/msg/Float32 "data: 0.9"   # forward
    ros2 topic pub /cmd_pwm std_msgs/msg/Float32 "data: 0.0"   # stop
    ros2 topic pub /cmd_pwm std_msgs/msg/Float32 "data: -1.0"  # reverse
    ```

- ### 6.4 Run the pwm_pub node (continuous random commands)
    ```bash
    ros2 run pwm_publisher pwm_pub
    ```
    &ensp;&ensp;Publishes a new random value in `[-1, 1]` on `/cmd_pwm` every 5 s.

- ### 6.5 Verify the connection
    ```bash
    ros2 node list      # /pwm_pub, /motor
    rqt_graph            # shows /pwm_pub --/cmd_pwm--> /motor
    ```

## 7. Report

**📄 Report** &nbsp; [Minireto_Semana3.pdf](report/Minireto_Semana3.pdf)
**📅 Submission date** &nbsp; 04/mar/2026
**🎥 Demo video** &nbsp; [video_reto_semana3_MCR2](https://youtu.be/j9zVz_eDtaE)

| Member                         | ID         |
|---------------------------------|------------|
| Josue Ureña Valencia            | A01738940  |
| César Arellano Arellano         | A00839373  |
| Jose Eduardo Sánchez Martínez   | A01738476  |
| Rafael André Gamiz Salazar      | A00838280  |
