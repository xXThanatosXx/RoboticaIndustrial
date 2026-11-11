# Práctica ROS 2: de Gazebo al brazo real

## Objetivo y alcance

Crear un paquete Python que mueva el brazo entre dos posiciones, coordine la pinza y repita la rutina. El mismo programa se ejecuta con los controladores de Gazebo y con los del robot real.

Duración sugerida: tres sesiones de dos horas. Requisitos: Ubuntu con ROS 2 Humble, Gazebo Classic y los paquetes de `arm_ws` instalados. Esta práctica usa la infraestructura existente de `arm_description` y `arm_controller`.

La secuencia es: **inicio → abrir → A → cerrar → B → abrir → inicio**. Las posiciones A y B son configuraciones articulares de demostración; no representan puntos de agarre calibrados. No se incluye un objeto ni un sistema de agarre físico en Gazebo.

El paquete ya está creado en `/home/ros/arm_ws/src/arm_student_demo`. Los bloques de código de esta guía corresponden a sus archivos. No hay que volver a crearlo para ejecutarlo. La actividad de creación sirve para reproducirlo en una copia del proyecto que todavía no lo tenga.

## Actividad 1. Entender cómo se comunican los componentes

**Objetivo:** identificar qué programa ordena el movimiento y cuál lo ejecuta.

Un **paquete** organiza código, configuración, archivos de lanzamiento y dependencias. Un **nodo** es un participante de ROS 2: ejecuta una tarea y puede publicar mensajes, recibirlos o solicitar operaciones. Aquí, `sequence_controller` es el nodo que decide el orden de los movimientos.

Un **tópico** es un canal con nombre y tipo de mensaje. Un publicador envía datos y uno o varios suscriptores los reciben. `/joint_states`, de tipo `sensor_msgs/msg/JointState`, contiene nombres y posiciones articulares. Los valores se relacionan por su índice: `name[i]` corresponde a `position[i]`.

Un **servicio** es una petición con una respuesta. El administrador de controladores ofrece servicios para consultar y activar controladores.

Una **acción** sirve para una operación que tarda: el cliente envía un objetivo, el servidor lo acepta o rechaza, puede enviar realimentación y finalmente devuelve un resultado. También puede recibir una solicitud de cancelación. Nuestro nodo espera la aceptación y el resultado de cada movimiento; no necesita un callback de realimentación para esta práctica.

Un **parámetro** configura un nodo, por ejemplo `move_seconds`. Un archivo **launch** inicia nodos y pasa parámetros; no es un nodo por sí mismo.

```text
sequence_controller (cliente de acciones)
    ├── /arm_controller/follow_joint_trajectory
    │       └── joint_1, joint_2, joint_3
    └── /gripper_controller/follow_joint_trajectory
            └── joint_4
                      ↓
             ros2_control + interfaz
               ├── Gazebo
               └── puerto serie → Arduino → servos

joint_state_broadcaster → /joint_states → herramientas de observación
```

ROS 2 descubre participantes automáticamente cuando comparten dominio y conectividad. Para comunicarse deben coincidir el nombre de la interfaz, el tipo de mensaje y, en los tópicos, políticas QoS compatibles. No conectamos nodos mediante cables en Python: creamos un cliente con el nombre de la acción que ofrece el controlador.

**Particularidades de este robot:**

- El brazo recibe tres posiciones en el orden `joint_1`, `joint_2`, `joint_3`.
- La pinza recibe solamente `joint_4`; `joint_5` imita su movimiento en sentido contrario.
- Los ángulos se expresan en radianes: aproximadamente 0.1745 rad son 10 grados.
- El URDF permite de `-pi/2` a `pi/2` en el brazo, y de `-pi/2` a `0` en `joint_4`.
- Respetar esos límites no garantiza ausencia de colisiones ni compatibilidad con todos los montajes físicos.

**Entrega:** dibujar el recorrido de una orden y explicar la diferencia entre un tópico y una acción.

## Actividad 2. Crear e instalar el paquete

**Objetivo:** reconocer la estructura mínima de un paquete Python de ROS 2.

### 2.1. Crear el paquete base

En una copia del proyecto que aún no tenga `arm_student_demo`. Si usas el paquete entregado, pasa al apartado 2.2: no repitas `ros2 pkg create` sobre una carpeta existente.

```bash
source /opt/ros/humble/setup.bash
mkdir -p ~/arm_ws/src
cd ~/arm_ws/src
ros2 pkg create arm_student_demo --build-type ament_python \
  --dependencies rclpy action_msgs control_msgs trajectory_msgs sensor_msgs
cd arm_student_demo
mkdir -p launch config docs test
```

`ament_python` indica cómo construir e instalar el paquete. `rclpy` permite programar nodos ROS 2 en Python. `control_msgs` define la acción de trayectoria; `trajectory_msgs` define los puntos de movimiento; `action_msgs` aporta los estados del resultado. `sensor_msgs` permite interpretar los estados articulares.

### 2.2. Crear las carpetas y los archivos del programa

Ejecutar desde la carpeta del paquete:

```bash
cd ~/arm_ws/src/arm_student_demo
mkdir -p arm_student_demo resource launch config docs test
touch arm_student_demo/__init__.py resource/arm_student_demo
touch arm_student_demo/sequence_controller.py
touch config/sequence.yaml
touch launch/robot.launch.py launch/sequence.launch.py
```

`mkdir -p` crea las carpetas que falten. `touch` crea un archivo vacío si no existe; si ya existe, conserva su contenido. Los dos primeros archivos deben permanecer vacíos: son marcadores para Python y ament. Los otros cuatro deben contener el código que aparece en las actividades siguientes.

**No compilar todavía si estás construyendo el paquete desde cero:** primero completar los archivos de los apartados 2.3 y 2.4. Un archivo creado con `touch` aún no contiene el programa.

### 2.3. Abrir cada archivo y pegar su código

Los siguientes comandos usan `nano`, un editor de texto de terminal. Abrir cada archivo, pegar el bloque completo indicado, guardar con **Ctrl+O**, confirmar con **Enter** y salir con **Ctrl+X**. Si el archivo ya tiene contenido, reemplazarlo por el bloque correspondiente; no añadir una segunda copia al final. Copiar solamente el contenido del bloque, sin las marcas de Markdown.

**Nodo de la secuencia — código de la actividad 4:**

```bash
nano ~/arm_ws/src/arm_student_demo/arm_student_demo/sequence_controller.py
```

Este archivo contiene la lógica que envía los movimientos.

**Parámetros — primer bloque YAML de la actividad 5:**

```bash
nano ~/arm_ws/src/arm_student_demo/config/sequence.yaml
```

Este archivo permite cambiar posiciones, tiempos y repeticiones sin editar Python. Conservar la indentación y usar espacios, no tabulaciones.

**Lanzamiento del robot — código de la actividad 3:**

```bash
nano ~/arm_ws/src/arm_student_demo/launch/robot.launch.py
```

Este archivo inicia la simulación o la conexión al hardware y carga los controladores.

**Lanzamiento de la rutina — código de la actividad 5:**

```bash
nano ~/arm_ws/src/arm_student_demo/launch/sequence.launch.py
```

Este archivo carga el YAML, selecciona el reloj y ejecuta el nodo de la secuencia.

### 2.4. Completar los archivos de instalación

`ros2 pkg create` ya genera estos tres archivos. Abrirlos uno por uno y reemplazar su contenido por los bloques completos del **anexo A**:

```bash
nano ~/arm_ws/src/arm_student_demo/setup.py
nano ~/arm_ws/src/arm_student_demo/setup.cfg
nano ~/arm_ws/src/arm_student_demo/package.xml
```

- `setup.py`: registra `sequence_controller` como ejecutable e instala los archivos de configuración y lanzamiento.
- `setup.cfg`: indica dónde instalar el ejecutable para que lo encuentre `ros2 run`.
- `package.xml`: declara las dependencias y el tipo de construcción.

No hace falta ejecutar `chmod +x` sobre `sequence_controller.py`: el apartado `console_scripts` de `setup.py` genera el ejecutable durante la instalación.

Para crear una guía propia en una copia nueva del paquete:

```bash
nano ~/arm_ws/src/arm_student_demo/docs/ACTIVIDADES.md
```

Guardar allí esta guía o las notas de la práctica. En el paquete entregado, este documento y `docs/VERIFICACION.md` ya existen y no se deben reemplazar por archivos vacíos.

Los archivos `test/test_sequence.py` y `test/verify_gazebo.py` son herramientas adicionales incluidas en el paquete entregado. No son necesarios para ejecutar la rutina. Si se reproduce solamente el código de esta guía en un paquete nuevo, solicitar esos dos archivos al docente antes de ejecutar sus pruebas automáticas; no crearlos vacíos. Las comprobaciones manuales de la actividad 6 sí pueden hacerse con los archivos anteriores.

### 2.5. Revisar los archivos antes de compilar

```bash
cd ~/arm_ws/src/arm_student_demo
ls -l package.xml setup.py setup.cfg
ls -l arm_student_demo/sequence_controller.py
ls -l config/sequence.yaml launch/robot.launch.py launch/sequence.launch.py
python3 -m py_compile setup.py arm_student_demo/sequence_controller.py
python3 -m py_compile launch/robot.launch.py launch/sequence.launch.py
```

`ls -l` confirma que los archivos existen y permite revisar su tamaño. Los archivos de código y configuración deben tener contenido. `py_compile` comprueba la sintaxis de Python sin iniciar ROS ni mover el robot; si no imprime errores, esa comprobación pasó. No sustituye la compilación ni las pruebas de ejecución.

Estructura final:

```text
arm_student_demo/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/arm_student_demo             # archivo vacío
├── arm_student_demo/
│   ├── __init__.py                      # archivo vacío
│   └── sequence_controller.py
├── config/sequence.yaml
├── launch/robot.launch.py
├── launch/sequence.launch.py
├── test/test_sequence.py
├── test/verify_gazebo.py
└── docs/ACTIVIDADES.md
```

Los archivos completos de instalación aparecen en el anexo A. `setup.py` registra el ejecutable y copia los YAML y launch al directorio de instalación. `setup.cfg` coloca el ejecutable donde `ros2 run` lo busca. `package.xml` declara las dependencias; declararlas no las instala automáticamente.

### 2.6. Compilar y comprobar la instalación

Después de guardar todos los archivos, compilar desde la raíz del workspace:

```bash
cd ~/arm_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon build --packages-select arm_student_demo
source install/setup.bash
ros2 pkg prefix arm_student_demo
ros2 pkg executables arm_student_demo
```

**Resultado esperado:** la compilación termina sin errores y la última orden muestra `arm_student_demo sequence_controller`. El comando de compilación presupone que las dependencias del proyecto ya están construidas. En una instalación nueva se deben construir también esas dependencias.

`source` carga las rutas de los paquetes y bibliotecas en la terminal actual. Repetir en **cada terminal nueva**:

```bash
source /opt/ros/humble/setup.bash
source ~/arm_ws/install/setup.bash
```

Tras modificar los archivos del paquete, volver a compilar y cargar `install/setup.bash`. Esta guía utiliza una instalación normal, que copia los archivos.

**Entrega:** explicar para qué sirven `package.xml`, `setup.py` y `source`.

## Actividad 3. Iniciar Gazebo y descubrir las interfaces

**Objetivo:** separar el arranque del robot de la ejecución de movimientos.

En la terminal A:

```bash
ros2 launch arm_student_demo robot.launch.py is_sim:=true
```

Para una máquina sin pantalla, añadir `gui:=false`. El servidor de Gazebo sigue simulando aunque no se abra la ventana.

El archivo siguiente inicia Gazebo, publica el modelo y lo inserta en la simulación. Reutiliza `controller.launch.py` para activar los controladores. En modo real, ese lanzamiento existente publica el modelo y abre la interfaz serie. No se inicia `sequence_controller` automáticamente.

Archivo `launch/robot.launch.py`:

```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    description = get_package_share_directory('arm_description')
    controller = get_package_share_directory('arm_controller')
    gazebo = get_package_share_directory('gazebo_ros')
    is_sim = LaunchConfiguration('is_sim')
    model = ParameterValue(Command([
        'xacro ', os.path.join(description, 'urdf', 'arm.urdf.xacro'),
        ' is_sim:=true',
    ]), value_type=str)
    return LaunchDescription([
        DeclareLaunchArgument('is_sim', default_value='true'),
        DeclareLaunchArgument('gui', default_value='true'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(gazebo, 'launch', 'gazebo.launch.py')),
            condition=IfCondition(is_sim),
            launch_arguments={'gui': LaunchConfiguration('gui')}.items(),
        ),
        Node(
            package='robot_state_publisher', executable='robot_state_publisher',
            condition=IfCondition(is_sim),
            parameters=[{'robot_description': model, 'use_sim_time': True}],
        ),
        Node(
            package='gazebo_ros', executable='spawn_entity.py',
            condition=IfCondition(is_sim), output='screen',
            arguments=['-entity', 'arm', '-topic', 'robot_description'],
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(
                controller, 'launch', 'controller.launch.py')),
            launch_arguments={'is_sim': is_sim}.items(),
        ),
    ])
```

**Por qué:** el estudiante puede comprobar que los controladores están listos antes de enviar una trayectoria. No se cargan Alexa ni MoveIt para esta práctica.

En la terminal B, después de cargar el entorno:

```bash
ros2 node list
ros2 control list_controllers
ros2 action list -t
ros2 topic list -t
ros2 topic echo /joint_states --once
ros2 topic echo /clock --once
```

**Resultados esperados:**

- `arm_controller`, `gripper_controller` y `joint_state_broadcaster` aparecen `active`.
- Existen las dos acciones `follow_joint_trajectory`, de tipo `control_msgs/action/FollowJointTrajectory`.
- `/joint_states` publica posiciones y `/clock` publica el tiempo de simulación.

Consultar una conexión:

```bash
ros2 action info /arm_controller/follow_joint_trajectory
ros2 topic info /joint_states --verbose
ros2 interface show control_msgs/action/FollowJointTrajectory
```

La primera orden identifica el servidor y los clientes activos. La segunda muestra publicadores, suscriptores y QoS. La tercera muestra los campos del objetivo, del resultado y de la realimentación, separados por `---`.

**Entrega:** registrar los controladores activos y asociar cada acción con sus articulaciones.

## Actividad 4. Programar la secuencia

**Objetivo:** enviar una trayectoria y avanzar solamente cuando termine correctamente.

El programa usa una clase porque un nodo ROS 2 se representa mediante `Node`. Cada método tiene una tarea concreta; no hay hilos propios ni máquinas de estados en el programa del estudiante.

Archivo `arm_student_demo/sequence_controller.py`:

```python
"""Una secuencia corta: inicio, A, cerrar, B, abrir, inicio."""
import math
import time

import rclpy
from action_msgs.msg import GoalStatus
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from trajectory_msgs.msg import JointTrajectoryPoint


class SequenceController(Node):
    def __init__(self):
        super().__init__('sequence_controller')
        defaults = {
            'home': [0.0, 0.0, 0.0],
            'position_a': [-0.25, -0.15, 0.10],
            'position_b': [0.25, -0.15, 0.10],
            'gripper_open': -0.35, 'gripper_closed': -0.05,
            'move_seconds': 4.0, 'pause_seconds': 1.0,
            'repetitions': 1, 'server_timeout': 15.0, 'result_margin': 10.0,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)
        self.active_goal = None
        self.pending_goal = None
        self.arm = ActionClient(self, FollowJointTrajectory,
                                '/arm_controller/follow_joint_trajectory')
        self.gripper = ActionClient(self, FollowJointTrajectory,
                                    '/gripper_controller/follow_joint_trajectory')

    def value(self, name):
        return self.get_parameter(name).value

    def validate(self):
        for name in ['home', 'position_a', 'position_b']:
            values = self.value(name)
            if len(values) != 3:
                raise ValueError(f'{name}: se necesitan tres posiciones')
            for angle in values:
                if not math.isfinite(angle) or abs(angle) > math.pi / 2:
                    raise ValueError(f'{name}: fuera de los limites del URDF')
        for name in ['gripper_open', 'gripper_closed']:
            angle = self.value(name)
            if not math.isfinite(angle) or not -math.pi / 2 <= angle <= 0:
                raise ValueError(f'{name}: debe estar entre -pi/2 y 0')
        for name in ['move_seconds', 'server_timeout', 'result_margin']:
            if not math.isfinite(self.value(name)) or self.value(name) <= 0:
                raise ValueError(f'{name}: debe ser positivo y finito')
        pause = self.value('pause_seconds')
        if not math.isfinite(pause) or pause < 0:
            raise ValueError('pause_seconds: debe ser finito y no negativo')
        if self.value('repetitions') < 1:
            raise ValueError('repetitions: debe ser al menos 1')

    def wait(self, future, seconds):
        rclpy.spin_until_future_complete(self, future, timeout_sec=seconds)
        if not future.done():
            raise RuntimeError('Tiempo de espera agotado')
        return future.result()

    def move(self, client, joints, positions, label):
        self.get_logger().info(label)
        point = JointTrajectoryPoint()
        point.positions = list(positions)
        nanoseconds = round(self.value('move_seconds') * 1_000_000_000)
        point.time_from_start.sec = nanoseconds // 1_000_000_000
        point.time_from_start.nanosec = nanoseconds % 1_000_000_000
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = joints
        goal.trajectory.points = [point]
        self.pending_goal = client.send_goal_async(goal)
        self.active_goal = self.wait(self.pending_goal, self.value('server_timeout'))
        self.pending_goal = None
        if not self.active_goal.accepted:
            self.active_goal = None
            raise RuntimeError('El controlador rechazo el objetivo')
        response = self.wait(self.active_goal.get_result_async(),
                             self.value('move_seconds') + self.value('result_margin'))
        self.active_goal = None
        if (response.status != GoalStatus.STATUS_SUCCEEDED
                or response.result.error_code != FollowJointTrajectory.Result.SUCCESSFUL):
            raise RuntimeError(f'Movimiento fallido: {response.result.error_string}')
        self.get_logger().info('Movimiento completado')
        time.sleep(self.value('pause_seconds'))

    def run_sequence(self):
        self.validate()
        for client in [self.arm, self.gripper]:
            if not client.wait_for_server(timeout_sec=self.value('server_timeout')):
                raise RuntimeError('Controlador no disponible; inicia robot.launch.py')
        arm_joints = ['joint_1', 'joint_2', 'joint_3']
        steps = [
            (self.arm, arm_joints, self.value('home'), 'Inicio'),
            (self.gripper, ['joint_4'], [self.value('gripper_open')], 'Abrir pinza'),
            (self.arm, arm_joints, self.value('position_a'), 'Posicion A'),
            (self.gripper, ['joint_4'], [self.value('gripper_closed')], 'Cerrar pinza'),
            (self.arm, arm_joints, self.value('position_b'), 'Posicion B'),
            (self.gripper, ['joint_4'], [self.value('gripper_open')], 'Soltar'),
            (self.arm, arm_joints, self.value('home'), 'Regresar'),
        ]
        for cycle in range(self.value('repetitions')):
            self.get_logger().info(f'Ciclo {cycle + 1}/{self.value("repetitions")}')
            for client, joints, positions, label in steps:
                self.move(client, joints, positions, label)
        self.get_logger().info('SECUENCIA COMPLETADA')

    def cancel_motion(self):
        # Recuperar una aceptacion tardia antes de intentar cancelar.
        if self.pending_goal is not None:
            try:
                self.active_goal = self.wait(self.pending_goal, 2.0)
            except RuntimeError:
                self.get_logger().error('Sin respuesta: no se pudo confirmar la cancelacion')
        if self.active_goal is not None and self.active_goal.accepted:
            try:
                response = self.wait(self.active_goal.cancel_goal_async(), 2.0)
                if not response.goals_canceling:
                    self.get_logger().warning('El controlador no confirmo la cancelacion')
                else:
                    self.get_logger().info('Cancelacion aceptada por el controlador')
            except RuntimeError:
                self.get_logger().error('No se pudo confirmar la cancelacion')


def main(args=None):
    # Mantener ROS activo durante Ctrl+C para poder solicitar la cancelacion.
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = None
    exit_code = 0
    try:
        node = SequenceController()
        node.run_sequence()
    except KeyboardInterrupt:
        exit_code = 130
    except Exception as error:
        if node is not None:
            node.get_logger().error(str(error))
        else:
            print(error)
        exit_code = 1
    finally:
        if node is not None:
            node.cancel_motion()
            node.destroy_node()
        rclpy.shutdown()
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
```

**Lectura del código:**

| Parte | Función y motivo |
|---|---|
| `__init__` | Nombra el nodo, declara parámetros y crea los dos clientes de acciones. |
| `value` | Lee un parámetro para evitar repetir una expresión larga. |
| `validate` | Revisa todas las posiciones antes de enviar la primera orden. |
| `wait` | Procesa comunicaciones ROS mientras espera una respuesta, con tiempo máximo. |
| `move` | Construye un punto, envía un objetivo y comprueba aceptación y resultado. |
| `run_sequence` | Describe los siete pasos y repite la lista. |
| `cancel_motion` | Solicita cancelar un objetivo pendiente si la rutina se interrumpe. |
| `main` | Inicializa ROS, ejecuta la rutina y libera los recursos. |

Un `Future` representa una respuesta que todavía puede estar pendiente. `spin_until_future_complete` permite recibirla procesando los eventos del nodo. No basta con enviar la petición y dejar de atender ROS.

`JointTrajectoryPoint.positions` contiene las posiciones de destino. `time_from_start` indica cuánto tiempo debe tardar ese movimiento. Aquí se envía **un punto por objetivo**; por eso cada paso puede durar cuatro segundos sin acumular el tiempo de los anteriores. Si se añadieran varios puntos a un mismo objetivo, sus tiempos tendrían que ser crecientes.

El controlador interpola entre su posición de partida y el destino. Esta rutina envía posiciones; no calcula cinemática inversa ni planifica para evitar obstáculos. `SUCCESSFUL` y `STATUS_SUCCEEDED` deben indicar éxito antes de pasar al siguiente paso.

Cada fila de `steps` contiene cuatro datos: cliente, articulaciones, posiciones y texto informativo. Para añadir un paso se añade otra fila, conservando el número y el orden de las articulaciones.

`pause_seconds` usa tiempo real mediante `time.sleep`. Los límites de espera también se miden en tiempo real; si Gazebo está pausado o corre muy lento, puede agotarse la espera. La trayectoria utiliza el reloj del controlador.

Con Ctrl+C se intenta cancelar la acción activa. Una cancelación ROS no sustituye un paro físico; si no hay comunicación, el programa avisa que no pudo confirmarla. El proceso devuelve 0 al completar, 1 ante un error y 130 al interrumpirse.

## Actividad 5. Ejecutar y cambiar el comportamiento

**Objetivo:** cambiar movimientos sin reescribir el nodo.

Configuración inicial:

Archivo `config/sequence.yaml`:

```yaml
sequence_controller:
  ros__parameters:
    home: [0.0, 0.0, 0.0]
    position_a: [-0.25, -0.15, 0.10]
    position_b: [0.25, -0.15, 0.10]
    gripper_open: -0.35
    gripper_closed: -0.05
    move_seconds: 4.0
    pause_seconds: 1.0
    repetitions: 1
    server_timeout: 15.0
    result_margin: 10.0
```

La clave `sequence_controller` debe coincidir con el nombre del nodo. `ros__parameters` identifica los parámetros ROS. Los arreglos de posiciones usan números decimales para ser arreglos de tipo `double`.

| Parámetro | Significado |
|---|---|
| `home` | Configuración inicial y final del brazo. |
| `position_a`, `position_b` | Destinos articulares de la demostración. |
| `gripper_open`, `gripper_closed` | Posiciones de apertura y cierre parcial. |
| `move_seconds` | Duración de cada uno de los siete movimientos. |
| `pause_seconds` | Pausa después de cada movimiento. |
| `repetitions` | Cantidad de ciclos completos. |
| `server_timeout` | Espera máxima por un servidor o por aceptación del objetivo. |
| `result_margin` | Margen adicional para recibir el resultado de un movimiento. |

Estos valores de pinza son de demostración: verificar su apertura real antes de intentar sujetar un objeto.

Lanzamiento de la rutina:

Archivo `launch/sequence.launch.py`:

```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share = get_package_share_directory('arm_student_demo')
    return LaunchDescription([
        DeclareLaunchArgument('is_sim', default_value='true'),
        DeclareLaunchArgument('config', default_value=os.path.join(
            share, 'config', 'sequence.yaml')),
        Node(
            package='arm_student_demo', executable='sequence_controller',
            output='screen',
            parameters=[LaunchConfiguration('config'), {
                'use_sim_time': ParameterValue(LaunchConfiguration('is_sim'), value_type=bool),
            }],
        ),
    ])
```

`is_sim` es un argumento del lanzamiento. Se convierte al parámetro booleano `use_sim_time`: `true` permite que el nodo use `/clock`; `false` utiliza el reloj del sistema. Este lanzamiento solamente inicia la rutina; el robot debe estar funcionando en la terminal A.

En la terminal B:

```bash
ros2 launch arm_student_demo sequence.launch.py is_sim:=true
```

**Resultado esperado:** aparecen `Ciclo 1/1`, siete mensajes `Movimiento completado` y `SECUENCIA COMPLETADA`. El nodo termina al finalizar. La duración nominal es unos 35 segundos: siete movimientos de cuatro segundos y siete pausas de un segundo, más comunicación.

Mientras se ejecuta, en la terminal C:

```bash
ros2 node info /sequence_controller
ros2 param get /sequence_controller use_sim_time
ros2 action info /arm_controller/follow_joint_trajectory
```

Al terminar, es normal que `sequence_controller` desaparezca de `ros2 node list`.

### Variante A: tres ciclos

Para probar una configuración sin editar la instalada:

```bash
cp ~/arm_ws/src/arm_student_demo/config/sequence.yaml /tmp/sequence_student.yaml
nano /tmp/sequence_student.yaml
```

Cambiar únicamente:

```yaml
    repetitions: 3
```

Ejecutar:

```bash
ros2 launch arm_student_demo sequence.launch.py is_sim:=true \
  config:=/tmp/sequence_student.yaml
```

Se esperan tres ciclos, 21 movimientos completados y regreso a `home`.

### Variante B: otra trayectoria y otro ritmo

En la misma copia del YAML, cambiar:

```yaml
    position_a: [-0.35, -0.10, 0.15]
    position_b: [0.15, -0.20, 0.05]
    move_seconds: 6.0
    pause_seconds: 2.0
    repetitions: 1
```

Volver a ejecutar el comando anterior. Se esperan posiciones diferentes y una duración nominal de 56 segundos. Estos destinos se ensayan primero en Gazebo.

Los parámetros se leen para construir la secuencia al inicio. Para esta actividad, editar el YAML y **volver a lanzar**; no usar `ros2 param set` a mitad de un movimiento.

**Entrega:** mostrar las dos variantes y explicar qué cambia al aumentar la duración. Aumentar el tiempo reduce la velocidad media para el mismo desplazamiento, pero no demuestra por sí solo un límite de velocidad física.

## Actividad 6. Verificar resultados y provocar un error controlado

**Objetivo:** distinguir entre una orden enviada, un resultado del controlador y una medición.

Mientras corre una rutina, consultar:

```bash
ros2 topic echo /joint_states
ros2 topic hz /joint_states
ros2 topic echo /arm_controller/controller_state --once
```

Detener la observación con Ctrl+C. `JointState` muestra las posiciones; `controller_state` contiene los valores deseados, reales según la interfaz y su diferencia. El estado no debe interpretarse como una medida independiente si el controlador o el hardware trabaja en lazo abierto.

Para guardar evidencia, iniciar antes de la rutina en una tercera terminal:

```bash
mkdir -p ~/arm_ws/student_results
cd ~/arm_ws/student_results
ros2 bag record -o ciclo_01 /joint_states /arm_controller/controller_state /clock
```

Después de terminar la rutina, detener la grabación con Ctrl+C y consultar:

```bash
ros2 bag info ~/arm_ws/student_results/ciclo_01
```

Usar otro nombre para una nueva grabación. Esta bolsa registra los tópicos seleccionados; no se afirma que registre los objetivos y resultados de las acciones. Guardar también la salida de la terminal de la rutina.

### Comprobar el rechazo de parámetros inválidos

Con Gazebo activo, ejecutar directamente el nodo:

```bash
ros2 run arm_student_demo sequence_controller --ros-args \
  -p use_sim_time:=true -p 'position_a:=[2.0, 0.0, 0.0]'
echo $?
```

**Resultado esperado:** error de límites del URDF, código de salida distinto de cero y ninguna orden enviada por esta ejecución. La validación ocurre antes de cualquier movimiento.

### Comprobar la falta de servidor

Cerrar Gazebo y esperar a que terminen sus controladores. Ejecutar:

```bash
ros2 run arm_student_demo sequence_controller --ros-args -p server_timeout:=2.0
echo $?
```

**Resultado esperado:** `Controlador no disponible`, salida distinta de cero y ninguna espera indefinida.

### Pruebas automáticas incluidas

```bash
cd ~/arm_ws
source install/setup.bash
ROS_LOCALHOST_ONLY=1 ROS_DOMAIN_ID=175 \
  python3 -m pytest -q src/arm_student_demo/test/test_sequence.py
```

Las pruebas revisan límites y parámetros; utilizan servidores de acciones de prueba para éxito, rechazo, fallo y cancelación por tiempo agotado. Usan rutas de acciones privadas bajo `/student_test/`, con un identificador distinto por prueba, sin mandar órdenes a las acciones habituales del robot.

Prueba completa con Gazebo sin ventana:

```bash
python3 ~/arm_ws/src/arm_student_demo/test/verify_gazebo.py
```

Para comprobar también el lanzamiento de la rutina con otras posiciones y tiempos:

```bash
python3 ~/arm_ws/src/arm_student_demo/test/verify_gazebo.py --variant
```

La opción `--variant` ejecuta un ciclo de siete movimientos con la configuración de la variante B.

Esta prueba inicia su propia simulación, usa el dominio ROS 174 y el puerto Gazebo 11359, ejecuta tres ciclos y comprueba 21 resultados exitosos, cambios articulares y posición final. No ejecutar dos copias de esta prueba simultáneamente. Sus registros están en `/tmp/arm_student_gazebo.log` y `/tmp/arm_student_sequence.log`. Al finalizar detiene los procesos que inició.

**Entrega:** tabla con variante, ciclos, movimientos completados, tiempo aproximado y observaciones. Añadir evidencia del parámetro inválido y del servidor ausente.

## Actividad 7. Ejecutar en el robot real

**Objetivo:** conservar el programa y cambiar la interfaz que ejecuta las órdenes.

Primero terminar Gazebo y cualquier otra interfaz que pueda mandar movimientos, incluidos sliders, MoveIt o Alexa. No mantener simulación y hardware con los mismos nombres de acciones en el mismo dominio ROS.

Antes de energizar los actuadores, el docente debe verificar el firmware, los ceros articulares, la alimentación, el recorrido libre y un medio de cortar la energía. La interfaz existente inicializa comandos en cero al activarse: incluso iniciar el hardware requiere comprobar la postura de partida. Las coordenadas de demostración no son posiciones de agarre certificadas.

El proyecto configura `/dev/ttyACM0` y 115200 baudios. Comprobar el dispositivo:

```bash
ls -l /dev/ttyACM0
id -nG
```

El puerto está definido en `arm_description/urdf/arm_ros2_control.xacro`. Si el dispositivo es otro, ajustar ese archivo y recompilar `arm_description`. Si faltan permisos, el administrador debe conceder acceso al grupo correspondiente al dispositivo y renovar la sesión.

En la terminal A:

```bash
ros2 launch arm_student_demo robot.launch.py is_sim:=false
```

En la terminal B:

```bash
ros2 control list_controllers
ros2 action list -t
```

Continuar solamente cuando estén activos los controladores y se haya revisado físicamente la postura. Preparar una copia del YAML para el primer ensayo:

```bash
cp ~/arm_ws/src/arm_student_demo/config/sequence.yaml /tmp/sequence_real.yaml
nano /tmp/sequence_real.yaml
```

Empezar con una repetición, tiempos de seis segundos y posiciones aprobadas por el docente. Hacer primero el ensayo sin objeto. Ejecutar después:

```bash
ros2 launch arm_student_demo sequence.launch.py is_sim:=false \
  config:=/tmp/sequence_real.yaml
```

La comunicación conserva las mismas acciones y nombres de articulaciones. Cambian la infraestructura y el reloj. No hay que enviar este programa Python al Arduino: se ejecuta en el computador con ROS 2; la interfaz del proyecto convierte los comandos y los transmite por el puerto serie al firmware.

**Limitación de verificación física:** `arm_controller/src/arm_interface.cpp`, en `read()`, copia `position_commands_` a `position_states_`. No lee encoders. Además, los controladores existentes configuran `open_loop_control: true`. Un resultado exitoso y un error publicado cercano a cero no prueban que el brazo físico alcanzó la posición. Comparar la ejecución con observación o mediciones externas; no calcular precisión física a partir de ese estado copiado.

**Entrega:** demostración supervisada y comparación breve de simulación y realidad. No es necesario sujetar un objeto para aprobar la transferencia del programa; un agarre requiere calibrar las posiciones y la pinza.

## Problemas frecuentes

| Síntoma | Comprobación o solución |
|---|---|
| `Package not found` | Compilar y cargar `install/setup.bash` en esa terminal. |
| No aparece el ejecutable | Revisar `entry_points` en `setup.py` y volver a compilar. |
| `Controlador no disponible` | Iniciar `robot.launch.py`, revisar controladores activos y dominio ROS. |
| Parámetro no aplicado | Revisar el nombre `sequence_controller`, indentación y ruta `config:=...`. |
| Error de tipo en YAML | Usar decimales en posiciones y tiempos; entero en `repetitions`. |
| Tiempo agotado en simulación | Revisar que Gazebo no esté pausado y que `/clock` avance; aumentar `result_margin` si la simulación es lenta. |
| Gazebo no encuentra mallas | Comprobar que `arm_description` está instalado y que se cargó el entorno. |
| `Operation not permitted` en sockets | Ejecutar en una terminal con permisos de red local; ROS y Gazebo necesitan comunicación entre procesos. |
| No se puede abrir el puerto serie | Revisar nombre del dispositivo, permisos y que otro programa no lo use. |
| La acción termina pero el brazo real no coincide | Revisar calibración, alimentación y firmware; el estado del driver no es una medición. |

## Evaluación

| Evidencia | Peso |
|---|---:|
| Paquete instalado y explicación de sus archivos | 20 % |
| Secuencia con acciones y comprobación de resultados | 25 % |
| Dos variantes configurables en Gazebo | 25 % |
| Transferencia supervisada al hardware | 20 % |
| Registro de pruebas y comparación crítica | 10 % |

## Anexo A. Archivos de instalación completos

Archivo `setup.py`:

```python
from glob import glob
from setuptools import setup

package_name = 'arm_student_demo'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/docs', glob('docs/*.md')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Estudiante',
    maintainer_email='student@example.com',
    description='Practica basica de trayectorias para arm_ws.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={'console_scripts': [
        'sequence_controller = arm_student_demo.sequence_controller:main',
    ]},
)
```

Archivo `setup.cfg`:

```ini
[develop]
script_dir=$base/lib/arm_student_demo
[install]
install_scripts=$base/lib/arm_student_demo
```

Archivo `package.xml`:

```xml
<?xml version="1.0"?>
<package format="3">
  <name>arm_student_demo</name>
  <version>0.1.0</version>
  <description>Practica basica de trayectorias para arm_ws.</description>
  <maintainer email="student@example.com">Estudiante</maintainer>
  <license>Apache-2.0</license>
  <buildtool_depend>ament_python</buildtool_depend>
  <exec_depend>rclpy</exec_depend>
  <exec_depend>action_msgs</exec_depend>
  <exec_depend>control_msgs</exec_depend>
  <exec_depend>trajectory_msgs</exec_depend>
  <exec_depend>sensor_msgs</exec_depend>
  <exec_depend>launch</exec_depend>
  <exec_depend>launch_ros</exec_depend>
  <exec_depend>ament_index_python</exec_depend>
  <exec_depend>ros2launch</exec_depend>
  <exec_depend>robot_state_publisher</exec_depend>
  <exec_depend>xacro</exec_depend>
  <exec_depend>gazebo_ros</exec_depend>
  <exec_depend>arm_description</exec_depend>
  <exec_depend>arm_controller</exec_depend>
  <test_depend>python3-pytest</test_depend>
  <test_depend>python3-yaml</test_depend>
  <export><build_type>ament_python</build_type></export>
</package>
```

Los archivos `resource/arm_student_demo` y `arm_student_demo/__init__.py` están vacíos. El primero registra el paquete en el índice ament; el segundo identifica el directorio como un paquete Python.

## Anexo B. Referencias

- [ROS 2 Humble: creación de paquetes](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html).
- [ROS 2 Humble: nodos](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Nodes/Understanding-ROS2-Nodes.html).
- [Controlador de trayectorias de ros2_control Humble](https://control.ros.org/humble/doc/ros2_controllers/joint_trajectory_controller/doc/userdoc.html).

Consultar `VERIFICACION.md` en esta misma carpeta para conocer las comprobaciones realizadas y las limitaciones de la entrega.

