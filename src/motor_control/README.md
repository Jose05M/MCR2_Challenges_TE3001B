# motor_control

## 1. Introduction

&ensp;&ensp;This package is the deliverable for the **Week 2** mini-challenge of
TE3001B - Fundamentación de Robótica (MCR2 / Tecnológico de Monterrey): *"Crear un
controlador PID para un motor simulado"* ("Create a PID controller for a simulated
motor"). It implements a closed-loop control system in ROS 2: a set-point generator, a
discrete PID controller, and a first-order DC motor simulation, all connected through
topics. The challenge is split into three phases:

1. **PID controller** with gains (`kp`, `ki`, `kd`, `Ts`) that can be retuned at
   runtime without restarting any node.
2. **Multiple reference signals** (`sine`, `square`, `triangle`, `step`), switchable
   at runtime via the `signal_type` parameter.
3. **Three fully independent control loops** running in parallel, isolated from each
   other through ROS 2 namespaces.

```
 ┌───────────┐  set_point   ┌────────────┐  motor_input_u   ┌──────────┐
 │ set_point │────────────► │ controller │ ───────────────► │ dc_motor │
 └───────────┘              └─────┬──────┘                  └────┬─────┘
                                   ▲                              │
                                   └────────── motor_speed_y ─────┘
```

## 2. Nodes

- ### 2.1 set_point
    &ensp;&ensp;Publishes a reference waveform on `set_point` at 100 Hz (0.01 s timer).
    Amplitude is fixed at `2.0` and angular frequency at `1.0 rad/s`. The waveform
    shape is controlled by the runtime-reconfigurable parameter `signal_type`:
    `sine`, `square`, `triangle`, or `step` (step rises to the amplitude at `t = 2 s`).
    See [set_point.py](motor_control/set_point.py).

    | Parameter     | Default | Description                                         |
    |---------------|---------|------------------------------------------------------|
    | `signal_type` | `sine`  | Waveform shape: `sine`, `square`, `triangle`, `step` |

    | Topic        | Type                | I/O | Description                  |
    |--------------|---------------------|-----|--------------------------------|
    | `set_point`  | `std_msgs/Float32`  | pub | Reference signal for the loop  |

- ### 2.2 controller
    &ensp;&ensp;Discrete PID controller. Subscribes to `set_point` and `motor_speed_y`,
    computes the error `e = sp - y`, and on a `Ts`-period timer applies:

    ```
    integral += e * Ts
    derivative = (e - e_prev) / Ts
    u = kp*e + ki*integral + kd*derivative
    ```

    &ensp;&ensp;`kp`, `ki`, `kd`, and `Ts` are runtime-reconfigurable parameters; the
    parameter callback rejects negative values. See
    [controller.py](motor_control/controller.py).

    | Parameter | Default | Description                  |
    |-----------|---------|--------------------------------|
    | `kp`      | `1.0`   | Proportional gain               |
    | `ki`      | `0.0`   | Integral gain                   |
    | `kd`      | `0.0`   | Derivative gain                 |
    | `Ts`      | `0.01`  | Control loop sample time (s)    |

    | Topic            | Type                | I/O | Description                  |
    |------------------|---------------------|-----|--------------------------------|
    | `set_point`      | `std_msgs/Float32`  | sub | Reference from `set_point`      |
    | `motor_speed_y`  | `std_msgs/Float32`  | sub | Plant output feedback           |
    | `motor_input_u`  | `std_msgs/Float32`  | pub | Control effort sent to the plant|

- ### 2.3 dc_motor
    &ensp;&ensp;Simulates a first-order DC motor plant (gain `K`, time constant `T`)
    using the discrete update `y[k+1] = y[k] + (-1/T·y[k] + K/T·u[k])·Ts`. Gain and
    time constant are runtime-reconfigurable. See
    [dc_motor.py](motor_control/dc_motor.py).

    | Parameter            | Default | Description                          |
    |----------------------|---------|----------------------------------------|
    | `sample_time`        | `0.01`  | Simulation sample time (s)              |
    | `sys_gain_K`         | `1.75`  | Plant gain `K`                          |
    | `sys_tau_T`          | `0.5`   | Plant time constant `T` (s)             |
    | `initial_conditions` | `0.0`   | Initial value of the output              |

    | Topic            | Type                | I/O | Description                     |
    |------------------|---------------------|-----|------------------------------------|
    | `motor_input_u`  | `std_msgs/Float32`  | sub | Control effort from `controller`   |
    | `motor_speed_y`  | `std_msgs/Float32`  | pub | Simulated motor speed              |

## 3. Package Structure

```
motor_control/
├── config/
│   └── params.yaml            # per-group parameters for challenge_launch.py
├── launch/
│   ├── motor_launch.py        # single unnamespaced loop, hardcoded parameters
│   └── challenge_launch.py    # 3 independent namespaced loops using params.yaml
├── motor_control/
│   ├── set_point.py           # reference signal generator node
│   ├── controller.py          # discrete PID controller node
│   └── dc_motor.py            # simulated first-order DC motor node
├── report/                    # submitted report (PDF)
├── test/                      # style tests (flake8, pep257, copyright)
├── package.xml
└── setup.py
```

## 4. Requirements

- ROS 2 (Humble or compatible), with `rclpy`, `std_msgs`, and `numpy`.
- `rqt_plot` (optional — for plotting `set_point` vs. `motor_speed_y` live).

## 5. How To Use

- ### 5.1 Build the package
    ```bash
    # from the workspace root
    colcon build --packages-select motor_control
    source install/setup.bash
    ```

- ### 5.2 Phase 1 — PID controller with live-tunable gains
    ```bash
    ros2 launch motor_control motor_launch.py
    ```
    &ensp;&ensp;Starts one closed loop — nodes `/sp_gen`, `/control`, `/motor_sys` —
    with a sine reference and the controller starting **untuned**
    (`kp=2.0, ki=0.0, kd=0.0`). See [motor_launch.py](launch/motor_launch.py).

    &ensp;&ensp;Inspect the running system and watch it track the reference poorly:
    ```bash
    ros2 node list          # /sp_gen, /control, /motor_sys
    ros2 param list         # parameters declared by each active node
    ros2 run rqt_plot rqt_plot /set_point/data /motor_speed_y/data /motor_input_u/data
    ```
    &ensp;&ensp;Retune the controller at runtime, without restarting any node. The
    report shows `kp=0.1, ki=7.0, kd=0.0` making `motor_speed_y` track `set_point`
    closely on the same `rqt_plot`:
    ```bash
    ros2 param set /control kp 0.1
    ros2 param set /control ki 7.0
    ```

- ### 5.3 Phase 2 — switch the reference signal at runtime
    &ensp;&ensp;With Phase 1 already running well — `motor_launch.py` up, `rqt_plot`
    open, and the gains tuned to `kp=0.1, ki=7.0, kd=0.0` as above — change the
    waveform generated by `/sp_gen` without restarting it and watch `rqt_plot` update
    live for each shape:
    ```bash
    ros2 param set /sp_gen signal_type square
    ros2 param set /sp_gen signal_type triangle
    ros2 param set /sp_gen signal_type step
    ros2 param set /sp_gen signal_type sine
    ```

- ### 5.4 Phase 3 — 3 fully independent control loops
    &ensp;&ensp;Stop the Phase 1/2 session (`Ctrl+C` on `motor_launch.py`) and launch
    the multi-group setup instead:
    ```bash
    ros2 launch motor_control challenge_launch.py
    ```
    &ensp;&ensp;Starts three closed loops isolated under the namespaces `/group1`,
    `/group2`, and `/group3` (node names `..._1`, `..._2`, `..._3`), each with its own
    plant and reference signal, configured in
    [config/params.yaml](config/params.yaml):

    | Group  | Reference  | Plant `K` | Plant `T` | `kp` | `ki` |
    |--------|------------|-----------|-----------|------|------|
    | group1 | sine       | 4.0       | 0.9       | 0.1  | 7.0  |
    | group2 | square     | 1.75      | 0.5       | 0.1  | 7.0  |
    | group3 | triangle   | 2.16      | 0.05      | 0.1  | 7.0  |

    &ensp;&ensp;Verify the groups are isolated with `rqt_graph` — it should show 3
    fully separate subgraphs, one per group, with no shared topics:
    ```bash
    ros2 topic list         # topics prefixed per group, e.g. /group1/set_point
    rqt_graph
    ```
    &ensp;&ensp;Compare the three groups on a single plot to confirm each one runs
    its own reference signal independently:
    ```bash
    ros2 run rqt_plot rqt_plot /group1/set_point/data /group2/set_point/data /group3/set_point/data
    ```
    &ensp;&ensp;Finally, each group can be retuned independently through its own
    namespaced node names — both the reference signal and the PID gains. The general
    pattern is:
    ```bash
    ros2 param set /<namespace>/<node_name> <parameter_name> <value>
    ```
    &ensp;&ensp;For example:
    ```bash
    ros2 param set /group1/sp_gen_1 signal_type step
    ros2 param set /group1/control_1 kp 0.2
    ros2 param set /group2/control_2 ki 5.0
    ros2 param set /group3/control_3 kd 0.01
    ```

## 6. Report

**📄 Report** &nbsp; [Mini-reto_ semana2.pdf](report/Mini-reto_%20semana2.pdf)
**📅 Submission date** &nbsp; 26/feb/2026
**🎥 Demo video** &nbsp; [video_reto_semana2_MCR2](https://youtu.be/qfFP-Em9IwY)

| Member                         | ID         |
|---------------------------------|------------|
| Josue Ureña Valencia            | A01738940  |
| César Arellano Arellano         | A00839373  |
| Jose Eduardo Sánchez Martínez   | A01738476  |
| Rafael André Gamiz Salazar      | A00838280  |
