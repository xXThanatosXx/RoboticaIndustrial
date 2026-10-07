# ur3_gazebo_demo

Para la conexión desde VMware al UR3 real, consulta
[la guía de configuración y comandos](CONEXION_UR3_REAL.md).

Paquete minimo para enviar una trayectoria articular a un UR3 simulado en Gazebo.

## Lanzar la simulacion

```bash
cd /home/ros/colcon_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch ur_simulation_gazebo ur_sim_control.launch.py ur_type:=ur3
```

## Ejecutar la trayectoria

En otra terminal:

```bash
cd /home/ros/colcon_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run ur3_gazebo_demo ur3_joint_trajectory
```

## Cambiar de controlador

Por defecto usa `joint_trajectory_controller`, que es el controlador inicial del launch de Gazebo.

Para URSim o el driver real con el controlador escalado activo (no con la
configuración de Gazebo de este repositorio), puedes ejecutar:

```bash
ros2 run ur3_gazebo_demo ur3_joint_trajectory --ros-args -p controller_name:=scaled_joint_trajectory_controller
```

## Pick and place con ventosa en D0 (URSim)

El ejecutable `ur3_pick_and_place` realiza un ciclo:

1. Apaga la ventosa y va a `home` (iniciar sin pieza sujetada).
2. Va a `pick_approach`, luego a `pick`.
3. Activa D0 y espera `vacuum_settle_time`.
4. Regresa a `pick_approach`, va a `place_approach` y luego a `place`.
5. Desactiva D0, espera y se retira por `place_approach` hasta `home`.

Cada movimiento debe terminar correctamente antes de continuar. D0 es la salida
digital estándar del armario, `pin=0`, no la salida de herramienta (`pin=16`).
Se usa `ur_msgs/srv/SetIO` en `/io_and_status_controller/set_io` con `fun=1`.
Por defecto 1 activa la ventosa y 0 la desactiva; para una válvula de lógica
inversa configura `vacuum_active_high: false`.

### Compilar

```bash
cd /home/ros/colcon_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select ur3_gazebo_demo
source install/setup.bash
```

### Conectar con tu URSim

```bash
ros2 launch ur_robot_driver ur_control.launch.py \
  ur_type:=ur3 \
  robot_ip:=192.168.19.131 \
  reverse_ip:=192.168.19.128 \
  launch_rviz:=true
```

Mantén el programa External Control en Play. En otra terminal, sin ejecutar
simultáneamente las otras demos:

```bash
cd /home/ros/colcon_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 control list_controllers
ros2 run ur3_gazebo_demo ur3_pick_and_place --ros-args \
  --params-file /home/ros/colcon_ws/src/ur3_gazebo_demo/config/pick_and_place.yaml
```

`scaled_joint_trajectory_controller` e `io_and_status_controller` deben estar
activos. En PolyScope, pestaña I/O, observa la salida digital estándar 0:
se enciende al recoger y se apaga al depositar.

### Ajustar posiciones y tiempos

Edita `config/pick_and_place.yaml`. Cada posición contiene seis ángulos en
radianes: shoulder_pan, shoulder_lift, elbow, wrist_1, wrist_2, wrist_3.
Puedes consultar una postura enseñada con `ros2 topic echo /joint_states --once`;
ordena los valores por `name` según ese orden, no por su posición en el mensaje.

Las posiciones incluidas son ilustrativas para URSim: no son posiciones
cartesianas de una pieza o mesa concreta. Los movimientos son interpolaciones
articulares, no descensos verticales garantizados; no hay planificación de
colisiones ni confirmación de agarre por sensor. URSim permite observar la
secuencia y D0, pero este ejemplo no simula la física de una ventosa ni adjunta
un objeto en RViz. Antes de usar hardware real deben enseñarse y validarse las
posturas, los recorridos y la conexión de la válvula.

`move_duration` es el tiempo nominal de cada tramo; el escalado puede alargarlo.
`motion_timeout` usa tiempo de reloj real (120 s por defecto, incluso si URSim
está pausado). Si falla un movimiento o SetIO, el proceso termina con error e
intenta cancelar el objetivo pendiente. No envía una orden de apagar la ventosa
al abortar, para no soltar una pieza durante el transporte. Si falla SetIO por
tiempo agotado, el estado de la salida es incierto: comprueba I/O antes de
reiniciar. Cada nuevo ciclo comienza apagando la ventosa.

### Pruebas sin mover el robot

```bash
cd /home/ros/colcon_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
python3 -m unittest discover -s src/ur3_gazebo_demo/test -v
```
