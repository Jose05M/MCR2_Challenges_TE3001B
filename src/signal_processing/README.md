# signal_processing

## 1. Introduction

&ensp;&ensp;This package is the deliverable for the **Week 1** mini-challenge of
TE3001B - Fundamentación de Robótica (MCR2 / Tecnológico de Monterrey): *"Generar nodo
que envíe una señal a otro nodo que procese la señal"* ("Create a node that sends a
signal to another node that processes the signal"). It contains two ROS 2 nodes that
communicate over topics — one generates a sinusoidal signal and the other receives it,
applies a phase shift, an offset, and a scaling, then publishes the result.

```
                 /signal (Float32)
   ┌────────────┐ ───────────────►  ┌──────────────┐
   │ signal_gen │                   │ signal_proc  │ ──► /proc_signal (Float32)
   └────────────┘ ───────────────►  └──────────────┘
                 /time (Float32)
```

## 2. Nodes

- ### 2.1 signal_gen
    &ensp;&ensp;Generates a real-time sinusoidal signal and publishes it together with
    a timestamp, at 10 Hz (0.1 s timer period). `t` is the time elapsed since the node
    started (`time.time() - start_time`), and `signal(t) = sin(t)`. See
    [signal_gen.py](signal_processing/signal_gen.py).

    | Topic     | Type                | I/O | Description                        |
    |-----------|---------------------|-----|-------------------------------------|
    | `/signal` | `std_msgs/Float32`  | pub | Instantaneous value of `sin(t)`     |
    | `/time`   | `std_msgs/Float32`  | pub | Elapsed time `t` (seconds)          |

- ### 2.2 signal_proc
    &ensp;&ensp;Subscribes to `/signal` and `/time`, caches the latest sample of each
    (`signal_callback` / `time_callback`), and on its own 10 Hz timer applies:

    1. __Phase shift__ — uses the trigonometric identity
       `sin(t + φ) = sin(t)·cos(φ) + cos(t)·sin(φ)` with `φ = π/2` (hardcoded), taking
       `sin(t)` from `/signal` and computing `cos(t) = cos(self.time)` from `/time`.
       With `φ = π/2` this turns the sine into a cosine: `sin(t + π/2) = cos(t)`.
    2. __Offset__ — adds `1.0`, moving the range from `[-1, 1]` to `[0, 2]`.
    3. __Scaling__ — multiplies by `0.5`, normalizing the result to `[0, 1]`.

    &ensp;&ensp;See [signal_proc.py](signal_processing/signal_proc.py).

    | Topic          | Type                | I/O | Description                                    |
    |----------------|---------------------|-----|--------------------------------------------------|
    | `/signal`      | `std_msgs/Float32`  | sub | Raw signal from `signal_gen`                      |
    | `/time`        | `std_msgs/Float32`  | sub | Timestamp from `signal_gen`                       |
    | `/proc_signal` | `std_msgs/Float32`  | pub | Phase-shifted, offset, normalized signal [0,1]    |

## 3. Package Structure

```
signal_processing/
├── launch/
│   └── challenge1_launch.py   # brings up signal_gen + signal_proc + rqt_plot
├── signal_processing/
│   ├── signal_gen.py          # signal generator node
│   └── signal_proc.py         # signal processing node
├── report/                    # submitted report (PDF)
├── test/                      # style tests (flake8, pep257, copyright)
├── package.xml
└── setup.py
```

## 4. Requirements

- ROS 2 (Humble or compatible), with `rclpy` and `std_msgs`.
- `rqt_plot` (optional — only used by the launch file to plot live data).

## 5. How To Use

- ### 5.1 Build the package
    ```bash
    # from the workspace root
    colcon build --packages-select signal_processing
    source install/setup.bash
    ```

- ### 5.2 Launch both nodes + rqt_plot
    ```bash
    ros2 launch signal_processing challenge1_launch.py
    ```
    &ensp;&ensp;Starts `signal_gen`, `signal_proc`, and `rqt_plot` (plotting `/signal`
    and `/proc_signal` live). See [challenge1_launch.py](launch/challenge1_launch.py).

- ### 5.3 Run the nodes individually
    ```bash
    # terminal 1
    ros2 run signal_processing signal_gen
    # terminal 2
    ros2 run signal_processing signal_proc
    ```

- ### 5.4 Verify topics manually
    ```bash
    ros2 topic echo /signal
    ros2 topic echo /proc_signal
    ros2 topic hz /proc_signal      # should report ~10 Hz
    ```

## 6. Report

**📄 Report** &nbsp; [Minireto_semana1.pdf](report/Minireto_semana1.pdf)
**📅 Submission date** &nbsp; 18/feb/2026
**👨‍🏫 Instructor** &nbsp; Luis Ricardo Salgado Garza

**🎥 Demo video** &nbsp; [video_reto_semana1_MCR2](https://youtu.be/o1mtZCxGZms)

| Member                         | ID         |
|---------------------------------|------------|
| Josue Ureña Valencia            | A01738940  |
| César Arellano Arellano         | A00839373  |
| Jose Eduardo Sánchez Martínez   | A01738476  |
| Rafael André Gamiz Salazar      | A00838280  |
