# MCR2_Challenges_TE3001B

<p align="center">
  <img alt="ROS 2 logo" src="https://avatars.githubusercontent.com/u/3979232?v=4" width="56">
  &nbsp;&nbsp;
  <img alt="micro-ROS logo" src="https://avatars.githubusercontent.com/u/49058602?v=4" width="56">
  &nbsp;&nbsp;
  <img alt="Manchester Robotics logo" src="https://avatars.githubusercontent.com/u/107204750?v=4" width="56">
</p>

<p align="center">
  <img alt="CI" src="https://github.com/Jose05M/MCR2_Challenges_TE3001B/actions/workflows/ci.yml/badge.svg">
  <img alt="ROS 2" src="https://img.shields.io/badge/ROS_2-Humble-22314E?logo=ros&logoColor=white">
  <img alt="micro-ROS" src="https://img.shields.io/badge/micro--ROS-ESP32-4E8EE9">
  <img alt="License" src="https://img.shields.io/badge/license-Apache_2.0-green">
</p>

## 1. Introduction

&ensp;&ensp;This is the ROS 2 workspace for the weekly mini-challenges of **TE3001B -
Fundamentals of Robotics** (MCR2 / Tecnológico de Monterrey), a 5-week course that
introduces ROS 2 fundamentals — from topics and messages to closed-loop control and
real hardware with micro-ROS. Each week's deliverable is its own `ament_python`
package under [src/](src/), documented in its own README.

```mermaid
flowchart LR
    W1["📡 Week 1<br/>signal_processing<br/>Topics &amp; nodes"]
    W2["⚙️ Week 2<br/>motor_control<br/>Simulated PID"]
    W3["🔌 Week 3<br/>pwm_publisher<br/>Real motor via micro-ROS"]
    W4["🏆 Final Challenge<br/>control_motor_challenge<br/>Closed-loop PID + encoder"]
    W1 --> W2 --> W3 --> W4
```

## 2. Packages

| Package | Deliverable | Summary |
|---|---|---|
| 📡 [signal_processing](src/signal_processing/) | Week 1 | Two nodes over topics: one generates a sine wave, the other phase-shifts, offsets, and normalizes it |
| ⚙️ [motor_control](src/motor_control/) | Week 2 | PID controller for a **simulated** DC motor, in 3 phases: live-tunable gains, switchable reference signals, and 3 independent namespaced control loops |
| 🔌 [pwm_publisher](src/pwm_publisher/) | Week 3 | ROS 2 side of a **real** DC motor driven by an ESP32 running micro-ROS: publishes random PWM commands to `/cmd_pwm` |
| 🏆 [control_motor_challenge](src/control_motor_challenge/) | Final Challenge | Closed-loop speed control of a **real** DC motor with encoder feedback: system identification (open loop) + incremental PID running on the ESP32 (closed loop) |

&ensp;&ensp;Each package's README documents its nodes, topics, parameters, how to
build and run it, and links to its submitted report.

## 3. Workspace Structure

```
ros2_challenge1/
├── src/
│   ├── signal_processing/          # Week 1
│   ├── motor_control/              # Week 2
│   ├── pwm_publisher/              # Week 3
│   └── control_motor_challenge/    # Final Challenge (system ID + closed-loop PID)
├── build/ install/ log/            # colcon artifacts (gitignored)
└── .gitignore
```

## 4. Requirements

- ROS 2 (Humble or compatible) with `colcon`.
- `micro_ros_agent`, for the packages that talk to a real ESP32
  ([pwm_publisher](src/pwm_publisher/), [control_motor_challenge](src/control_motor_challenge/)).
- An Arduino/ESP32 toolchain with the
  [micro-ros-arduino](https://github.com/micro-ROS/micro_ros_arduino) library, only
  needed to flash the ESP32 firmware referenced (as external code) by those two
  packages — see their own READMEs for details.

## 5. How To Build

```bash
# whole workspace
colcon build
source install/setup.bash

# a single package
colcon build --packages-select <package_name>
```

## 6. Related Repository

&ensp;&ensp;The Final Challenge has a companion repository with a more complete
write-up, the full system identification data/scripts, and both ESP32 firmware
variants: [Jose05M/challenge_control_PID_using_ROS2](https://github.com/Jose05M/challenge_control_PID_using_ROS2).

## 7. License

&ensp;&ensp;This workspace is licensed under the [Apache License 2.0](LICENSE).

## 8. Team

- Josue Ureña Valencia — A01738940
- César Arellano Arellano — A00839373
- Jose Eduardo Sánchez Martínez — A01738476
- Rafael André Gamiz Salazar — A00838280

&ensp;&ensp;Developed for **TE3001B - Fundamentals of Robotics**, in partnership
with **Manchester Robotics (MCR2)** as industry partner, at **Tecnológico de
Monterrey**.
