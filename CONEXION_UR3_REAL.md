# Conexión de ROS 2 Humble con el UR3 real

Guía del montaje utilizado en este proyecto. Se confirmó la conexión con el robot
y la ejecución de la prueba `test_scaled_joint_trajectory_controller`.
La configuración del pick and place real sigue pendiente.

## 1. Datos del montaje

| Elemento | Configuración |
|---|---|
| Robot | Universal Robots UR3 (usar `ur_type:=ur3`) |
| ROS | ROS 2 Humble en Ubuntu dentro de una máquina virtual VMware |
| Workspace | `/home/ros/colcon_ws` |
| IP del robot real | `192.168.0.2` |
| IP de Ubuntu en la VM | `192.168.0.10` |
| Máscara de red | `255.255.255.0` (`/24`) |
| Red de VMware | Bridged / puente sobre la tarjeta Ethernet conectada al robot |
| Host IP de External Control | `192.168.0.10` |
| Puerto de External Control | `50002` |
| Controlador de movimiento | `scaled_joint_trajectory_controller` |
| Calibración del robot | `/home/ros/colcon_ws/ur3_real_calibration.yaml` |

Verificar las IP antes de cada cambio de red. La IP de `reverse_ip` es la de
Ubuntu dentro de la VM, no la del PC anfitrión. No reutilizar las direcciones
`192.168.19.131` y `192.168.19.128` empleadas anteriormente con URSim.

## 2. Configurar VMware y la conexión física

1. Conectar por Ethernet el PC y el controlador del robot, directamente o mediante
   un switch.
2. En VMware, abrir **Virtual Machine Settings → Network Adapter**.
3. Marcar **Connected** y **Connect at power on**.
4. Seleccionar **Bridged: Connected directly to the physical network**.
5. En **Configure Adapters**, seleccionar la tarjeta Ethernet conectada al robot.
   Evitar que el puente se asocie al Wi-Fi.
6. Aplicar los cambios y comprobar que el adaptador ya no figure como NAT.

El robot debe poder iniciar conexiones hacia la VM. El modo puente facilita esa
comunicación bidireccional. Evitar suspender la VM o el anfitrión durante el control.

## 3. Configurar IPv4 dentro de Ubuntu

1. Abrir **Configuración → Red → Cableada → engranaje → IPv4**.
2. Seleccionar **Manual**.
3. Introducir dirección `192.168.0.10` y máscara `255.255.255.0`.
4. Para una conexión directa y aislada al robot, dejar vacíos puerta de enlace y
   DNS. Esta conexión por sí sola no proporciona Internet.
5. Aplicar y desactivar/reactivar la conexión cableada.

El robot debe tener IP `192.168.0.2` y la misma máscara. Las direcciones deben
estar libres y ser distintas de la del PC anfitrión.

Comprobar desde Ubuntu:

```bash
ip -br addr
ip route get 192.168.0.2
ping -c 4 192.168.0.2
```

La interfaz debe mostrar `192.168.0.10/24`; la ruta al robot debe usar esa IP como
`src`. El ping satisfactorio confirma conectividad básica, no la disponibilidad
de todos los servicios.

Si existe un firewall, permitir solo entre los equipos implicados los puertos
del driver; no es necesario desactivar todo el firewall:

| Dirección | Puertos TCP |
|---|---|
| VM → robot | `29999`, `30001`, `30002`, `30004` |
| Robot → VM | `50001`–`50004` |

En este driver: `50001` es reverse, `50002` script sender, `50003` trajectory y
`50004` script command. Los puertos entrantes estarán disponibles cuando el
driver correspondiente esté funcionando.

## 4. Preparar el robot y External Control

1. Verificar el modelo y la versión de PolyScope. Para UR3 CB3, la documentación
   oficial consultada indica PolyScope 3.14.3 o superior para External Control;
   comprobar compatibilidad antes de cambiar software del robot.
2. Instalar **External Control URCap** si no está instalado y reiniciar según sus
   instrucciones.
3. En **Installation → External Control**, configurar:

   ```text
   Host IP: 192.168.0.10
   Custom port: 50002
   ```

4. Guardar la instalación y crear o abrir un programa con un nodo **External Control**.
5. Verificar el TCP, carga útil, centro de gravedad y ajustes de seguridad de la
   herramienta instalada antes de efectuar movimientos.

El procedimiento de esta guía utiliza el programa External Control iniciado
desde el panel; no usa `headless_mode`.

## 5. Preparar cada terminal

```bash
cd /home/ros/colcon_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
```

Ejecutar estos comandos en cada terminal nueva. Mantener el mismo `ROS_DOMAIN_ID`
y una configuración ROS compatible en todas las terminales.

Si se modificó el código de las demos, compilar antes de ejecutarlas:

```bash
colcon build --symlink-install --packages-select ur3_gazebo_demo
source install/setup.bash
```

## 6. Extraer la calibración —una vez por robot—

Con el robot encendido y accesible, desde una terminal preparada:

```bash
ros2 launch ur_calibration calibration_correction.launch.py \
  robot_ip:=192.168.0.2 \
  target_filename:=/home/ros/colcon_ws/ur3_real_calibration.yaml
```

Esperar la confirmación de guardado antes de continuar. Reutilizar este archivo
solo para el robot del que se extrajo. No sustituye la instalación de PolyScope:
no contiene el TCP, el modelo del gripper ni las posturas de la tarea.

## 7. Conectar el driver al robot real

Cerrar URSim, Gazebo y cualquier demo que esté enviando trayectorias. En la
**terminal 1**, preparada como se indica arriba:

```bash
ros2 launch ur_robot_driver ur_control.launch.py \
  ur_type:=ur3 \
  robot_ip:=192.168.0.2 \
  reverse_ip:=192.168.0.10 \
  kinematics_params_file:=/home/ros/colcon_ws/ur3_real_calibration.yaml \
  use_fake_hardware:=false \
  initial_joint_controller:=scaled_joint_trajectory_controller \
  launch_rviz:=true
```

Mantener esta terminal abierta. Comprobar en su salida que la calibración coincide.
Con el robot listo para operar y el área despejada, pulsar **Play** en el programa
External Control del panel.

En la **terminal 2**, también preparada:

```bash
ros2 control list_controllers
ros2 action list
ros2 topic echo /joint_states --once
```

Se espera ver `scaled_joint_trajectory_controller` e `io_and_status_controller`
activos, la acción `/scaled_joint_trajectory_controller/follow_joint_trajectory`
y las posiciones actuales del robot. Esta comprobación no envía movimientos.

## 8. Prueba predefinida del driver

**Este comando mueve el robot real.** Validar previamente las posturas y todo el
recorrido con el gripper montado, sin pieza y a velocidad reducida. No hay
planificación automática de obstáculos. Ejecutar solo una demo a la vez.

El ejemplo comprueba una postura inicial aproximada de:

| Articulación | Ángulo aproximado |
|---|---:|
| shoulder_pan_joint | 0° |
| shoulder_lift_joint | −90° |
| elbow_joint | 0° |
| wrist_1_joint | −90° |
| wrist_2_joint | 0° |
| wrist_3_joint | 0° |

Es una postura extendida: no ordenar ese movimiento sin verificar su viabilidad
en el montaje. No deshabilitar la comprobación para forzar el inicio.

Las posiciones de destino se encuentran en
`src/Universal_Robots_ROS2_Driver/ur_robot_driver/config/test_goal_publishers_config.yaml`.

Con el driver abierto y External Control en Play, en otra terminal preparada:

```bash
ros2 launch ur_robot_driver test_scaled_joint_trajectory_controller.launch.py
```

La prueba publica un objetivo cada 6 segundos y repite cuatro posiciones. No
espera a que cada movimiento termine antes de publicar el siguiente; al reducir
la velocidad un nuevo objetivo puede llegar antes de completar el anterior.

Para finalizar, detener el programa desde **PolyScope** y cerrar la prueba con
`Ctrl+C`. Cerrar el publicador no garantiza cancelar el movimiento ya enviado.

## 9. Demo propia de trayectoria

Esta demo utiliza posiciones distintas de la prueba anterior. Validar también
sus recorridos antes de ejecutarla en hardware real. No activa la ventosa.

Con la otra prueba cerrada, el driver abierto y External Control en Play:

```bash
ros2 run ur3_gazebo_demo ur3_joint_trajectory \
  --ros-args \
  -p controller_name:=scaled_joint_trajectory_controller
```

Realiza cuatro posiciones una sola vez, con duración nominal total de 11 segundos.
El escalado de velocidad puede alargarla. El código y las posiciones están en
`src/ur3_gazebo_demo/ur3_gazebo_demo/ur3_joint_trajectory.py`.

Para interrumpirla, detener el programa desde PolyScope. `Ctrl+C` en el cliente
no garantiza cancelar la trayectoria enviada.

## 10. Pick and place: pendiente de configurar para el robot real

No ejecutar en el robot real las posiciones ilustrativas de URSim. Falta:

- Enseñar y validar `home`, `pick_approach`, `pick`, `place_approach` y `place`.
- Guardar los seis ángulos de cada postura, en radianes y ordenados por nombre,
  en `src/ur3_gazebo_demo/config/pick_and_place.yaml`.
- Verificar la conexión y polaridad de la ventosa: D0 estándar del armario es
  `pin=0`; la salida 0 de herramienta es otro pin (`16`).
- Validar los recorridos articulares completos con la herramienta y la pieza.

El ejemplo comienza apagando la ventosa: iniciar sin pieza sujetada. No incluye
detección de agarre, planificación de colisiones ni movimientos cartesianos
verticales garantizados.

## 11. Diagnóstico rápido

| Síntoma | Qué comprobar |
|---|---|
| No responde al ping | Cable, IP/máscara, adaptador puente y tarjeta Ethernet seleccionada |
| Ping responde, pero no conecta External Control | Host IP de la VM, `reverse_ip`, puerto 50002 y firewall |
| Controlador de trayectoria no disponible | Driver abierto, lista de controladores, mismo dominio ROS y tiempo de arranque |
| Driver conectado, pero no ejecuta movimientos | External Control en Play, estado del robot y escalado de velocidad |
| Calibración no coincide | Archivo extraído del robot correcto y ruta pasada al driver |
| Prueba rechaza la postura inicial | Consultar `/joint_states`; verificar postura y recorrido sin desactivar la comprobación |

Comandos de diagnóstico (no ordenan movimientos):

```bash
ip -br addr
ip route get 192.168.0.2
ping -c 4 192.168.0.2
printenv ROS_DOMAIN_ID
ros2 control list_controllers
ros2 action list
ros2 topic echo /joint_states --once
```

## Referencias

- [Configuración oficial del robot y External Control](https://docs.universal-robots.com/Universal_Robots_ROS2_Documentation/doc/ur_client_library/doc/setup/robot_setup.html)
- [Arranque del driver](https://docs.universal-robots.com/Universal_Robots_ROS2_Documentation/doc/ur_robot_driver/ur_robot_driver/doc/usage/startup.html)
- Los comandos de esta guía corresponden al driver Humble instalado en este
  workspace; otras versiones pueden cambiar nombres de parámetros.
