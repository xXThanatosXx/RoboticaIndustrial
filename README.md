# Clase Robot ARM Real robot Moveit


El objetivo de la presente práctica es realizar la ejecución de los nodos de comunicación de moveit con el robot real.

## Configuración del proyecto 

instalar dependencias 
```bash
sudo apt-get update && sudo apt-get install -y \
     ros-humble-joint-state-publisher-gui \
     ros-humble-gazebo-ros \
     ros-humble-xacro \
     ros-humble-ros2-control \
     ros-humble-moveit \
     ros-humble-ros2-controllers \
     ros-humble-gazebo-ros2-control 

```


```bash
sudo apt-get update && sudo apt-get install -y \
     libserial-dev \
     python3-pip
```
```bash
pip install pyserial
```

Clonar repositorio

```bash
git clone --branch Robot-Arm-Real-Robot --single-branch https://github.com/xXThanatosXx/RoboticaIndustrial.git
```
```bash
mv ~/RoboticaIndustrial/arm_ws ~/arm_ws
```
```bash
cd arm_ws
```
```bash
colcon build --cmake-clean-cache
```
```bash
rosdep install --from-paths src --ignore-src -r -y
```
```bash
colcon build
```

### Modificar el registro de Gazebo
```bash
sudo nano /usr/share/gazebo/setup.sh
```

Remplezar las lineas

```bash
export GAZEBO_MASTER_URI=""
export GAZEBO_MODEL_DATABASE_URI=""
```

Modificar el registro de gazebo 11

```bash
sudo nano /usr/share/gazebo-11/setup.sh
```

```bash
export GAZEBO_MASTER_URI=""
export GAZEBO_MODEL_DATABASE_URI=""

```bash
source /usr/share/gazebo-11/setup.sh
```

### Test de Control articular con Arduino

Lanzar nodo Gazebo

```bash
ros2 run arm_firmware simple_serial_transmitter --ros-args -p port:=/dev/ttyACM0
```
Listar los topicos de los nodos
```bash
ros2 topic list  
```
Publicar estado  y cambiar el ángulo del servo 

```bash
ros2 topic pub /serial_transmitter std_msgs/msg/String "data: '0'"  
```

Listar las articulaciones 
```bash
ros2 control list_hardware_components

```
```bash
ros2 control list_hardware_interfaces

```
```bash

ros2 topic list

```

En radianes cambiar el comportamiento in radians
```bash
ros2 topic pub /gripper_controller/commands std_msgs/msg/Float64MultiArray "layout: " 
```
### Ejecutar robot Real con planeación de trayectoria
```bash
ros2 launch arm_bringup real_robot.launch.py
```

### Tarea Slider controller

Lanzar el controllador bringup 
```bash
ros2 launch arm_bringup real_robot.launch.py
```
Lanzar el slider controller
```bash
ros2 launch arm_controller slider_controller.launch.py is_sim:=False
```
### Moution planing task (0,1,2)

```bash
ros2 launch arm_bringup real_robot.launch.py
```
```bash
ros2 launch arm_remote remote_interface.launch.py is_sim:=False
```

```bash
ros2 action send_goal /task_server arm_msgs/action/ArmTask "task_number: 2" 
```
