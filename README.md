# Actividad: de los comandos de TurtleSim al brazo en Gazebo

Esta práctica adapta los ejercicios de [Clase-TurtleSim del repositorio MobileRobot](https://github.com/xXThanatosXx/MobileRobot/tree/Clase-TurtleSim) al brazo del proyecto `arm_ws`.

**Objetivo:** reconocer paquetes, nodos, tópicos, servicios y acciones; enviar una trayectoria; observar sus resultados con RQt y PlotJuggler; y crear un nodo Python sencillo que lea las articulaciones.

Trabaja únicamente con **Gazebo**. El proyecto base debe estar compilado y contener `arm_description`, `arm_controller` y `arm_trajectory_demo`. No ejecutes simultáneamente el controlador del robot físico ni otros programas que envíen órdenes al brazo. Los comandos de movimiento se ejecutan uno por uno, esperando a que termine cada trayectoria.

## Qué cambia respecto a TurtleSim

| Ejercicio de TurtleSim | Equivalente en este brazo |
|---|---|
| Iniciar `turtlesim_node` | Iniciar el modelo en Gazebo y sus controladores. |
| Mover con `turtle_teleop_key` | Enviar posiciones articulares al controlador. Este ejercicio no usa un teleoperador de teclado. |
| `/turtle1/cmd_vel` y `geometry_msgs/msg/Twist` | `/arm_controller/joint_trajectory` y `trajectory_msgs/msg/JointTrajectory`. |
| `/turtle1/pose` | `/joint_states` para ángulos; TF para la posición y orientación de un enlace. |
| `ros2 node`, `topic`, `service`, `action` | Se conservan los comandos; cambian los nombres y tipos de las interfaces. |
| Crear `turtle2` con `/spawn` | No tiene una sustitución directa. Un segundo brazo necesita nombres, espacios de nombres y controladores propios. |
| Remapear el tópico de la segunda tortuga | Remapear el tópico de entrada de nuestro observador hacia `/joint_states`. |
| Nodo Python que calcula diferencias de poses | Nodo Python que muestra los ángulos del brazo en radianes y grados. |

**Distinción:** una velocidad `Twist` no es una trayectoria articular. Tampoco `JointState` proporciona directamente las coordenadas `x`, `y`, `z` de la punta. No basta con cambiar el nombre del tópico manteniendo el mismo mensaje.

## Actividad 1. Preparar el entorno e iniciar el brazo

En **cada terminal nueva**, carga primero:

```bash
source /opt/ros/humble/setup.bash
source ~/arm_ws/install/setup.bash
```

El primer comando habilita ROS 2 Humble; el segundo añade los paquetes compilados de `arm_ws` a esa terminal.

Comprueba los paquetes:

```bash
ros2 pkg prefix arm_description
ros2 pkg prefix arm_controller
ros2 pkg executables arm_trajectory_demo
```

`pkg prefix` muestra dónde está instalado un paquete. `pkg executables` lista sus programas; debe aparecer `arm_trajectory_demo send_trajectory`. Un paquete puede contener launch, modelos o configuración sin tener un ejecutable propio.

**Terminal A — iniciar Gazebo:**

```bash
ros2 launch arm_description gazebo.launch.py
```

Este lanzamiento inicia la simulación, publica el modelo e inserta el brazo. Espera a verlo en Gazebo.

**Terminal B — activar los controladores simulados:**

```bash
ros2 launch arm_controller controller.launch.py is_sim:=True
```

`is_sim:=True` selecciona la simulación. Los procesos `spawner` terminan después de cargar los controladores: esto es normal y no significa que los controladores se hayan detenido.

**Terminal C — comprobar el estado:**

```bash
ros2 control list_controllers
```

**Resultado esperado:** `arm_controller`, `gripper_controller` y `joint_state_broadcaster` aparecen `active`. El brazo usa `joint_1`, `joint_2` y `joint_3`. La pinza usa `joint_4`, pero no la moveremos en esta práctica.

## Actividad 2. Identificar los nodos

Un nodo es un participante de ROS 2 que realiza una tarea. Puede enviar o recibir mensajes y ofrecer servicios o acciones.

```bash
ros2 node list
ros2 node info /robot_state_publisher
ros2 node info /arm_controller
```

| Comando | Qué debes observar |
|---|---|
| `node list` | Los nodos que están activos en ese momento. |
| `node info /robot_state_publisher` | Sus interfaces; utiliza las articulaciones para publicar las transformaciones del robot. |
| `node info /arm_controller` | Suscripciones, publicaciones, servicios y acciones del controlador. |

**Entrega:** identifica quién recibe órdenes y quién publica información del robot. Usa los nombres que aparezcan en `node list` si tu instalación emplea un espacio de nombres diferente.

## Actividad 3. Explorar tópicos y tipos de mensajes

Un tópico es un canal con nombre y tipo. Uno o más publicadores envían mensajes y los suscriptores compatibles los reciben.

```bash
ros2 topic list
ros2 topic list -t
ros2 topic info /arm_controller/joint_trajectory
ros2 topic info /joint_states --verbose
ros2 topic type /joint_states
```

- `list` muestra los nombres.
- `list -t` añade el tipo de cada tópico.
- `info` muestra el tipo y el número de conexiones.
- `info --verbose` detalla los nodos conectados y sus políticas de comunicación, llamadas QoS.
- `type` devuelve solamente el tipo, útil antes de consultar su estructura.

Consulta las estructuras:

```bash
ros2 interface show trajectory_msgs/msg/JointTrajectory
ros2 interface show trajectory_msgs/msg/JointTrajectoryPoint
ros2 interface show sensor_msgs/msg/JointState
```

`JointTrajectory` contiene `joint_names` y una lista de `points`. Cada punto contiene `positions` y `time_from_start`. `JointState` contiene listas `name`, `position`, `velocity` y `effort`; algunos campos pueden estar vacíos.

Lee una muestra del estado y luego su frecuencia:

```bash
ros2 topic echo /joint_states --once
ros2 topic hz /joint_states
```

`echo --once` imprime un mensaje y termina. `hz` estima cuántos mensajes llegan por segundo; finaliza la observación con **Ctrl+C**. La frecuencia medida no tiene por qué coincidir con la frecuencia interna de la física de Gazebo.

**Resultado esperado:** en `name` aparecen las articulaciones. La posición de `name[i]` está en `position[i]`; no asumas que las primeras tres entradas son siempre el brazo. Las posiciones de sus articulaciones giratorias se expresan en radianes.

## Actividad 4. Publicar una trayectoria desde la terminal

Este ejercicio reemplaza la publicación de velocidades con `Twist` en TurtleSim. Primero comprueba otra vez que `arm_controller` esté `active`.

Para ver la orden, en una terminal de observación ejecuta:

```bash
ros2 topic echo /arm_controller/joint_trajectory
```

En otra terminal, envía la trayectoria completa:

```bash
ros2 topic pub --once /arm_controller/joint_trajectory \
  trajectory_msgs/msg/JointTrajectory \
  '{joint_names: [joint_1, joint_2, joint_3], points: [
    {positions: [0.0, 0.0, 0.0], time_from_start: {sec: 4}},
    {positions: [-0.25, -0.15, 0.10], time_from_start: {sec: 8}},
    {positions: [0.25, -0.15, 0.10], time_from_start: {sec: 12}},
    {positions: [0.0, 0.0, 0.0], time_from_start: {sec: 16}}
  ]}'
```

| Parte | Explicación |
|---|---|
| `ros2 topic pub` | Publica un mensaje desde la terminal. |
| `--once` | Envía una sola vez, en vez de repetir la orden continuamente. |
| `/arm_controller/joint_trajectory` | Tópico que recibe el controlador del brazo. |
| `trajectory_msgs/msg/JointTrajectory` | Tipo del mensaje que espera el controlador. |
| Comillas simples | Mantienen el contenido YAML como un único argumento, incluso en varias líneas. |
| `joint_names` | Orden de las articulaciones que corresponde a cada lista de posiciones. |
| `positions` | Tres ángulos de destino en radianes. |
| `time_from_start.sec` | Tiempo acumulado desde el inicio: 4, 8, 12 y 16 segundos. |

**Resultado esperado:** inicio → A → B → inicio en unos 16 segundos de simulación. En Gazebo debe estar activada la ejecución, no la pausa.

La actividad de TurtleSim usa `--rate 1` para repetir velocidades. Aquí usamos `--once`: repetir una trayectoria cada segundo puede sustituir continuamente la trayectoria anterior. El proceso de publicación puede terminar antes de que el robot acabe de moverse. **Ctrl+C en el publicador no cancela una trayectoria que ya se entregó al controlador.**

Para repetir el mismo recorrido con el script ya creado, después de terminar el movimiento anterior:

```bash
ros2 run arm_trajectory_demo send_trajectory --ros-args -p use_sim_time:=true
```

No ejecutes a la vez el script y el comando de publicación: ambos escriben en el mismo tópico.

## Actividad 5. Consultar un servicio del controlador

Un servicio intercambia una petición y una respuesta. El cliente puede esperar la respuesta o gestionarla de forma asíncrona; los servicios no son necesariamente síncronos en todos los programas.

```bash
ros2 service list
ros2 service type /controller_manager/list_controllers
ros2 interface show controller_manager_msgs/srv/ListControllers
```

La primera orden descubre servicios. La segunda identifica el tipo de uno de ellos. La tercera muestra su petición y respuesta, separadas por `---`.

Realiza una consulta:

```bash
ros2 service call /controller_manager/list_controllers \
  controller_manager_msgs/srv/ListControllers '{}'
```

`{}` representa una petición vacía: no hay campos que rellenar. La respuesta contiene nombres, tipos y estados de los controladores. Es una consulta, no una orden de movimiento.

**Resultado esperado:** localizar `arm_controller` con `state: active`.

En TurtleSim, `/spawn` permite crear una tortuga adicional. No lo sustituyas por una llamada para insertar otro brazo: duplicar el modelo sin separar sus controladores no reproduce ese ejercicio. En esta práctica, el servicio equivalente para aprender petición/respuesta es la consulta anterior.

## Actividad 6. Enviar un objetivo mediante una acción

Una acción representa una tarea que puede tardar. Permite conocer la aceptación, recibir realimentación y obtener un resultado; también ofrece una interfaz de cancelación.

Descubre las acciones y su estructura:

```bash
ros2 action list -t
ros2 action info /arm_controller/follow_joint_trajectory
ros2 interface show control_msgs/action/FollowJointTrajectory
```

Después de terminar cualquier movimiento anterior, envía un objetivo pequeño:

```bash
ros2 action send_goal /arm_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory \
  '{trajectory: {joint_names: [joint_1, joint_2, joint_3], points: [
    {positions: [0.15, -0.10, 0.10], time_from_start: {sec: 4}}
  ]}}' --feedback
```

El contenido articular es similar al del tópico, pero ahora está dentro del campo `trajectory` del objetivo de la acción. `--feedback` solicita mostrar los mensajes de realimentación que envíe el servidor.

**Resultado esperado:** objetivo aceptado, movimiento y resultado exitoso (`SUCCEEDED` y `error_code: 0`). Esto informa sobre la ejecución según el controlador, mientras que publicar al tópico no entrega un resultado de acción.

Para regresar a cero, una vez recibas el resultado:

```bash
ros2 topic pub --once /arm_controller/joint_trajectory \
  trajectory_msgs/msg/JointTrajectory \
  '{joint_names: [joint_1, joint_2, joint_3], points: [
    {positions: [0.0, 0.0, 0.0], time_from_start: {sec: 4}}
  ]}'
```

## Actividad 7. Ver las conexiones con RQt

Inicia RQt desde una terminal con el entorno cargado:

```bash
rqt
```

En **Plugins**, según los complementos instalados, busca:

- **Topic Monitor:** inspeccionar `/joint_states` y sus mensajes.
- **Service Caller:** seleccionar `/controller_manager/list_controllers` y ejecutar su petición vacía.
- **Plot:** representar una posición articular en función del tiempo.

Para ver el grafo de conexiones:

```bash
ros2 run rqt_graph rqt_graph
```

Actualiza la vista y desactiva filtros que oculten tópicos si hace falta. Los publicadores que terminan rápidamente pueden desaparecer antes de que actualices el grafo. El observador de la siguiente actividad permanece activo y resulta más fácil de identificar.

**Entrega:** captura de una conexión entre un nodo y un tópico. Explica quién publica y quién recibe.

Si necesitas restablecer la configuración de ventanas, cierra RQt y ejecuta:

```bash
rqt --clear-config
```

Este comando restablece la configuración de RQt. No cambia el código ni los controladores del brazo.

## Actividad 8. Crear un nodo Python que lea las articulaciones

La referencia crea un nodo para leer las poses de las tortugas. Aquí crearemos un observador de ángulos, sin cálculos de cinemática ni órdenes de movimiento.

### Crear el paquete y el ejecutable

Solo si no existe todavía `src/arm_observer`:

```bash
cd ~/arm_ws/src
ros2 pkg create arm_observer --build-type ament_python \
  --node-name read_joints --license Apache-2.0 \
  --dependencies rclpy sensor_msgs
code ~/arm_ws/src/arm_observer/arm_observer/read_joints.py
```

`ament_python` elige Python. `--node-name` genera el archivo y registra su ejecutable automáticamente. `rclpy` permite crear el nodo y `sensor_msgs` aporta `JointState`. No hay que modificar `setup.py` para registrar este ejecutable.

Reemplaza el contenido generado de `read_joints.py` por:

```python
import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class ReadJoints(Node):
    def __init__(self):
        super().__init__('read_joints')
        self.subscription = self.create_subscription(
            JointState, '/estado_brazo', self.show_positions, 10)

    def show_positions(self, message):
        values = []
        for name, angle in zip(message.name, message.position):
            if name in ['joint_1', 'joint_2', 'joint_3']:
                values.append(
                    f'{name}: {angle:.2f} rad = {math.degrees(angle):.1f} grados')
        self.get_logger().info(' | '.join(values), throttle_duration_sec=1.0)


def main(args=None):
    rclpy.init(args=args)
    node = ReadJoints()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
```

| Instrucción | Por qué está en el programa |
|---|---|
| `import math` | Permite convertir radianes a grados. |
| `rclpy`, `Node`, `JointState` | Proporcionan la comunicación ROS, el nodo y el tipo de mensaje. |
| `class ReadJoints(Node)` | Agrupa la suscripción y la función que procesa los datos. |
| `super().__init__('read_joints')` | Crea el nodo con un nombre identificable. |
| `create_subscription(...)` | Conecta el tipo, el tópico y la función receptora. El 10 es la profundidad del historial. |
| `/estado_brazo` | Nombre genérico elegido para aprender remapeo en la actividad siguiente. |
| `show_positions` | Se ejecuta al recibir un mensaje. |
| `zip(message.name, message.position)` | Une cada nombre con su valor, sin asumir un orden fijo. |
| `if name in ...` | Selecciona las tres articulaciones del brazo. |
| `math.degrees(angle)` | Convierte el ángulo a grados. |
| `:.2f` y `:.1f` | Limitan la cantidad de decimales para facilitar la lectura. |
| `values.append(...)` y `' | '.join(values)` | Construyen una línea con los ángulos del brazo. |
| `throttle_duration_sec=1.0` | Evita imprimir demasiadas líneas; muestra como máximo una por segundo. |
| `rclpy.spin(node)` | Mantiene el nodo atendiendo mensajes. |
| `except KeyboardInterrupt` | Permite salir con Ctrl+C. |
| `finally`, `destroy_node`, `shutdown` | Liberan los recursos al finalizar. |

Guarda y compila:

```bash
cd ~/arm_ws
colcon build --packages-select arm_observer
source install/setup.bash
ros2 pkg executables arm_observer
```

Debe aparecer `arm_observer read_joints`.

## Actividad 9. Conectar el observador mediante remapeo

Primero ejecútalo sin remapear:

```bash
ros2 run arm_observer read_joints
```

En otra terminal consulta:

```bash
ros2 node info /read_joints
ros2 topic info /estado_brazo
```

El nodo está suscrito a `/estado_brazo`, pero el proyecto publica los datos en `/joint_states`. Por eso no imprime posiciones. Detén solamente el observador con Ctrl+C.

Ahora conecta su entrada al tópico existente, sin cambiar el código:

```bash
ros2 run arm_observer read_joints --ros-args \
  --remap /estado_brazo:=/joint_states
```

`--ros-args` introduce opciones de ROS. `--remap origen:=destino` cambia el nombre que utiliza ese nodo. No crea otro robot ni convierte tipos de mensajes.

**Resultado esperado:** una línea de ángulos aproximadamente cada segundo. Por ejemplo, cerca de la posición A:

```text
joint_1: -0.25 rad = -14.3 grados | joint_2: -0.15 rad = -8.6 grados | joint_3: 0.10 rad = 5.7 grados
```

El orden puede variar con el mensaje. Mantén el observador activo y, en otra terminal, ejecuta la trayectoria:

```bash
ros2 run arm_trajectory_demo send_trajectory --ros-args -p use_sim_time:=true
```

Actualiza `rqt_graph` para ver la conexión del observador a `/joint_states`.

## Actividad 10. Graficar el movimiento con PlotJuggler

Desde una terminal con el entorno cargado:

```bash
ros2 run plotjuggler plotjuggler
```

1. En **Streaming**, selecciona **ROS2 Topic Subscriber** y pulsa **Start**.
2. Selecciona `/joint_states` y confirma.
3. Ajusta el buffer a unos 60 segundos, si se muestra esa opción.
4. Arrastra las señales de posición de `joint_1`, `joint_2` y `joint_3` a la gráfica.
5. Ejecuta la trayectoria después de iniciar la recepción de datos.

Si las señales aparecen con índices, consulta el orden con:

```bash
ros2 topic echo /joint_states --once
```

No confundas `position[0]` con `joint_1` sin comprobar `name`. Los datos graficados son ángulos en radianes.

**Resultado esperado:** cerca de A, los ángulos son `[-0.25, -0.15, 0.10]`; cerca de B, `[0.25, -0.15, 0.10]`; al terminar, aproximadamente `[0.0, 0.0, 0.0]`. Estos valores corresponden al script original, sin modificaciones.

## Actividad 11. Consultar la posición de un enlace con TF

La referencia compara posiciones cartesianas de dos tortugas. En el brazo, esa información se obtiene de las transformaciones entre enlaces, no leyendo directamente un ángulo articular.

```bash
ros2 run tf2_ros tf2_echo base_link claw_support
```

`tf2_echo` consulta la transformación de `claw_support` respecto a `base_link`: traslación en metros y orientación. Estos son enlaces del modelo actual. `claw_support` es el soporte de la pinza, no un punto de herramienta calibrado.

Ejecuta una trayectoria en otra terminal y observa cómo cambia la transformación. Termina la consulta con Ctrl+C.

**Entrega:** explica la diferencia entre `joint_1` en radianes y la traslación de `claw_support` en metros. No es necesario programar matrices de transformación en esta actividad introductoria.

## Evidencias que debe entregar el estudiante

- Lista de controladores activos y tipos de los tópicos de orden y estado.
- Trayectoria enviada desde terminal y resultado de una acción.
- Respuesta del servicio `list_controllers`.
- Código de `read_joints.py` y salida después del remapeo.
- Captura de RQt o PlotJuggler y explicación de los resultados.

## Alcance de las comprobaciones

Esta práctica observa el robot simulado. La interfaz física del proyecto copia posiciones ordenadas a estados publicados; no se debe utilizar ese estado como evidencia de precisión física. Los controladores existentes también configuran lazo abierto. Las trayectorias directas no planifican para evitar colisiones.

Comprobado el 22 de octubre de 2026:

- Sintaxis de los 29 bloques de comandos y del código Python incluido.
- Construcción de los mensajes de tópico y acción con las interfaces ROS instaladas.
- Lectura correcta de articulaciones aunque cambie su orden dentro de `JointState`.
- En Gazebo: consulta del servicio, trayectoria publicada desde terminal, acción finalizada con `SUCCEEDED` y `error_code: 0`, y retorno a cero.
- Observador ejecutado con el remapeo `/estado_brazo:=/joint_states`, mostrando radianes y grados.

La comprobación automática usó Gazebo sin ventana y un dominio ROS separado. No se automatizó la interfaz gráfica de RQt o PlotJuggler ni se probó hardware físico. Los registros están en `~/arm_ws/log/arm_trajectory_demo_validation/readme/`.
