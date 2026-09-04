# control_motor_challenge

## 1. Introduction

&ensp;&ensp;This package is the deliverable for the **Final Challenge** of TE3001B -
Fundamentación de Robótica (MCR2 / Tecnológico de Monterrey): *"Reporte final del
reto"* — a closed-loop speed controller for a **real DC motor with encoder**,
regulated from ROS 2 through an ESP32 running micro-ROS. The project has two stages:

1. **System identification** (*"Adquirir datos de los encoders usando el ESP32"*):
   drive the motor open-loop, log its response, and fit a first-order transfer
   function `G(s) = K / (τs + 1)` to it.
2. **Closed-loop control**: use that model to guide the PID gains, then run a full
   closed-loop controller **on the ESP32 itself**, with ROS 2 generating the
   reference signal and logging/plotting the result.

```
   PC (ROS 2)                              ESP32 (micro-ROS, node "motor_control")
 ┌────────────────┐   /set_point          ┌──────────────────────────────┐
 │ set_point_node  │ ────────────────────► │  PID incremental              │  PWM+Dir  ┌───────┐   ┌───────────┐
 │ (this package)  │                       │  (Kp=1.6, Ki=0.6, Kd=0.02)    │──────────►│ L298N │──►│ DC Motor  │
 └────────────────┘                       │                                │           └───────┘   │ + Encoder │
 ┌────────────────┐   /motor_output       │                                │◄──── pulses ──────────┘└───────────┘
 │ save_data       │◄───────────────────── │                                │
 │ (this package)  │                       └───────────────┬────────────────┘
 └────────────────┘   /motor_velocity                       │
 ┌────────────────┐◄──────────────────────────────────────────┘
 │ rqt_plot        │
 └────────────────┘
```

&ensp;&ensp;This package only contains the **ROS 2 side** (`set_point`, `save_data`).
The ESP32 firmware (`motor_control` micro-ROS node) is C/C++, flashed directly onto
the microcontroller, kept here only as a reference copy in [firmware/](firmware/).

> **Reference implementation:** the team's own GitHub repository,
> [Jose05M/challenge_control_PID_using_ROS2](https://github.com/Jose05M/challenge_control_PID_using_ROS2),
> has this same project with a more polished structure, its own README, and the
> saved experiment data (`csv_data/`) — use it as the canonical version for any
> future improvements to this challenge.

## 2. Nodes (this package)

- ### 2.1 set_point
    &ensp;&ensp;Publishes a reference waveform on `set_point` at 100 Hz (0.01 s
    timer), amplitude `1.0`, angular frequency `1.0 rad/s` (amplitude is `1.0` here,
    not `2.0` as in [motor_control](../motor_control/)'s simulated version, since the
    real ESP32 clamps `set_point` to `[-1, 1]`). Waveform shape is
    runtime-reconfigurable via `signal_type`: `sine`, `square`, `triangle`, `step`.
    See [set_point.py](control_motor_challenge/set_point.py) — identical structure
    to `motor_control`'s `set_point` node.

    | Parameter     | Default | Description                                          |
    |---------------|---------|--------------------------------------------------------|
    | `signal_type` | `sine`  | Waveform shape: `sine`, `square`, `triangle`, `step`    |

    | Topic        | Type                | I/O | Description                    |
    |--------------|---------------------|-----|-----------------------------------|
    | `/set_point` | `std_msgs/Float32`  | pub | Reference signal in `[-1, 1]`      |

- ### 2.2 save_data
    &ensp;&ensp;Subscribes to `/motor_output` and appends every sample to
    `motor_data.csv` (created in the directory the node is run from), with columns
    `time, setpoint, control, velocity`. See
    [save_data.py](control_motor_challenge/save_data.py).

    | Topic           | Type                        | I/O | Description                                      |
    |-----------------|-----------------------------|-----|-----------------------------------------------------|
    | `/motor_output` | `std_msgs/Float32MultiArray`| sub | `[time, setpoint, control_signal, velocity]`         |

## 3. External Node Reference — ESP32 firmware (`motor_control`)

&ensp;&ensp;Both firmware variants share the same hardware pinout and micro-ROS
connection lifecycle as [pwm_publisher's `/motor`](../pwm_publisher/#3-external-node-reference--motor-esp32-firmware)
node (4-state machine, Serial transport), but add a real quadrature encoder for
closed-loop feedback:

| Macro / Const     | Value      | Purpose                                     |
|--------------------|------------|-----------------------------------------------|
| `PHASEA_GPIO`       | `GPIO14`   | Encoder channel A (interrupt, `FALLING`)      |
| `PHASEB_GPIO`       | `GPIO13`   | Encoder channel B (direction sense)           |
| `IN1` / `IN2`       | `GPIO25` / `GPIO26` | L298N direction pins                 |
| `PWM_PIN`           | `GPIO27`   | PWM output to the L298N `ENA` (speed)         |
| `PWM_FRQ` / `PWM_RES` | `980 Hz` / `8 bit` | PWM carrier / duty range `0-255`     |
| `RPM_MAX`           | `134.0`    | Motor's rated max speed (gearmotor JGA25-370) |
| `PULSES_PER_REV`    | `495`      | Encoder resolution                            |
| `Ts`                | `0.1 s` (ident.) / `0.05 s` (final) | Control/sampling period      |

&ensp;&ensp;Velocity is computed from the pulse count accumulated each `Ts`, then
exponentially filtered:
```
rpm_raw  = (pulseCount * 60) / (PULSES_PER_REV * Ts)
rpm_filt = α·rpm_raw + (1-α)·rpm_filt        # α = 0.20
velocity = rpm_filt / RPM_MAX                # normalized to [-1, 1]
```

- ### 3.1 Stage 1 — [firmware/identificacion_motor.ino](firmware/identificacion_motor.ino)
    &ensp;&ensp;**Open-loop.** Applies `/set_point` directly as PWM magnitude (no
    controller) and publishes `/motor_output` as `[time, setpoint, velocity]`
    (3 fields) — just enough to record the motor's step response for identification.

- ### 3.2 Stage 2 — [firmware/mcr2_challenge_final.ino](firmware/mcr2_challenge_final.ino)
    &ensp;&ensp;**Closed-loop.** Runs a discrete incremental PID on-board:
    ```
    e[k] = reference - velocity
    u[k] = u[k-1] + Kp(e[k]-e[k-1]) + Ki·Ts·e[k] + (Kd/Ts)(e[k]-2e[k-1]+e[k-2])
    u[k] = constrain(u[k], 0, 1)          # then PWM = u[k] * 255
    ```
    &ensp;&ensp;with gains `Kp = 1.6, Ki = 0.6, Kd = 0.02`, tuned manually starting
    from the identified model. Publishes `/motor_output` as
    `[time, setpoint, control_signal, velocity]` (4 fields, matching `save_data`)
    **and** `/motor_velocity` (`std_msgs/Float32`) separately for `rqt_plot`.

- ### 3.3 System identification result
    &ensp;&ensp;Stage 1's logged step response was fit to `G(s) = 1.005 / (1.105s + 1)`
    (ARX(1,1) method) to guide the initial PID gain guess. The full identification
    method, logged data, and plots are kept in the
    [reference repository](https://github.com/Jose05M/challenge_control_PID_using_ROS2)
    (`csv_data/`), not duplicated here.

## 4. Package Structure

```
control_motor_challenge/
├── control_motor_challenge/
│   ├── set_point.py             # reference signal generator node
│   └── save_data.py             # /motor_output → motor_data.csv logger
├── firmware/
│   ├── identificacion_motor.ino # Stage 1: open-loop, for system identification
│   └── mcr2_challenge_final.ino # Stage 2: closed-loop incremental PID (final)
├── report/                      # submitted final report (PDF)
├── test/                        # style tests (flake8, pep257, copyright)
├── package.xml
└── setup.py
```

## 5. Requirements

- ROS 2 (Humble or compatible), with `rclpy`, `std_msgs`.
- `micro_ros_agent` running on the computer, bridging the ESP32 to ROS 2.
- Hardware: ESP32, DC gearmotor with quadrature encoder (JGA25-370, 140 RPM/12V),
  L298N H-bridge driver, external 12V supply — wiring diagram in the
  [report](report/).

## 6. How To Use

- ### 6.1 Build the package
    ```bash
    # from the workspace root
    colcon build --packages-select control_motor_challenge
    source install/setup.bash
    ```

- ### 6.2 Stage 1 — Identify the real motor
    &ensp;&ensp;Flash [firmware/identificacion_motor.ino](firmware/identificacion_motor.ino)
    to the ESP32, then:
    ```bash
    ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0
    ros2 run control_motor_challenge set_point --ros-args -p signal_type:=step
    ros2 run control_motor_challenge save_data     # writes motor_data.csv
    ```
    &ensp;&ensp;Fitting the model from `motor_data.csv` is covered in the
    [reference repository](https://github.com/Jose05M/challenge_control_PID_using_ROS2).

- ### 6.3 Stage 2 — Run the closed-loop PID challenge
    &ensp;&ensp;Flash [firmware/mcr2_challenge_final.ino](firmware/mcr2_challenge_final.ino)
    instead, then:
    ```bash
    ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0
    ros2 run control_motor_challenge set_point --ros-args -p signal_type:=sine
    ros2 run control_motor_challenge save_data
    ros2 run rqt_plot rqt_plot /set_point/data /motor_velocity/data
    ```
    &ensp;&ensp;Switch reference signals live, as in [motor_control §5.3](../motor_control/#53-phase-2--switch-the-reference-signal-at-runtime):
    ```bash
    ros2 param set /set_point_node signal_type square
    ros2 param set /set_point_node signal_type step
    ```

## 7. Report

**📄 Report** &nbsp; [reporte_final.pdf](report/reporte_final.pdf)
**📅 Submission date** &nbsp; 13/mar/2026
**🎥 Demo video** &nbsp; [video_reto_final_MCR2](https://youtu.be/kC0vWSkkP8s)
**🔗 Source repository** &nbsp; [github.com/Jose05M/challenge_control_PID_using_ROS2](https://github.com/Jose05M/challenge_control_PID_using_ROS2)

&ensp;&ensp;Four experiments were run with the final closed-loop controller (plots in
the [reference repository](https://github.com/Jose05M/challenge_control_PID_using_ROS2)):

| Signal              | Observation                                                                 |
|---------------------|-------------------------------------------------------------------------------|
| Sine                | Tracks closely, error stays within ±0.2; a brief spike near t=25s at a direction change |
| Square              | Most demanding case — error peaks to ±2.0 only during the ±1↔-1 direction reversals, then returns to ~0 |
| Step                | Fast, accurate settling from -1.0 to +1.0 within a few seconds                 |
| Step + perturbations| Manual resistance applied to the shaft (t=5-20s) causes oscillation, but the controller recovers the setpoint |

&ensp;&ensp;Per the report's conclusions: the system is stable in every scenario;
the main identified improvements are adding an **anti-windup** mechanism to the
integral term, and filtering/using a time-between-pulses method for velocity
estimation at low RPM.

| Member                         | ID         |
|---------------------------------|------------|
| Josue Ureña Valencia            | A01738940  |
| César Arellano Arellano         | A00839373  |
| Jose Eduardo Sánchez Martínez   | A01738476  |
| Rafael André Gamiz Salazar      | A00838280  |
