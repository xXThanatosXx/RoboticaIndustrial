# Clase Robto ARM Task Moveit.


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
git clone --branch Robot-ARM-Action --single-branch https://github.com/xXThanatosXx/RoboticaIndustrial.git
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
