# ROS 2 básico: crear un paquete y mover el brazo en Gazebo

## Qué vas a construir

Un paquete llamado `arm_trajectory_demo` con **un único script de movimiento**, `send_trajectory.py`. El brazo recorrerá cuatro posiciones en unos 16 segundos de simulación:

**Inicio → A → B → Inicio.**

Objetivo: aprender a crear un paquete, usar una plantilla de VS Code y publicar una trayectoria. Duración sugerida: 60–90 minutos. Se usa el brazo de `arm_ws`, ROS 2 Humble y Gazebo Classic ya instalados. El movimiento se realiza solo en simulación; la pinza permanece sin órdenes nuevas.

El paquete entregado ya está completo. Para hacerlo desde cero, usar una copia de `arm_ws` donde todavía no exista `src/arm_trajectory_demo`. Si trabajas con la entrega, omite el comando de creación y sigue las actividades para estudiar o editar sus archivos.

## Actividad 1. Abrir el proyecto con el entorno de ROS

**Propósito:** que la terminal conozca los comandos ROS 2 y los paquetes del brazo.

```bash
source /opt/ros/humble/setup.bash
source ~/arm_ws/install/setup.bash
cd ~/arm_ws
code .
```

| Instrucción | Por qué se utiliza |
|---|---|
| `source /opt/ros/humble/setup.bash` | Carga las rutas de ROS 2 Humble en esta terminal. |
| `source ~/arm_ws/install/setup.bash` | Añade los paquetes del proyecto ya compilados, como la descripción y los controladores. |
| `cd ~/arm_ws` | Sitúa la terminal en la raíz del proyecto. |
| `code .` | Abre esa carpeta en VS Code. |

Si `install/setup.bash` no existe, primero debe prepararse y compilarse el proyecto base del brazo. Esta actividad añade un paquete a ese proyecto existente.

Instala la extensión **Python de Microsoft** desde la terminal:

```bash
code --install-extension ms-python.python
```

También puedes buscarla con **Ctrl+Shift+X**. Ayuda a completar código y a detectar problemas de Python. No instala ROS ni crea el paquete. [Extensión Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python).

Desde **Ctrl+Shift+P**, ejecuta `Python: Select Interpreter` y elige `/usr/bin/python3`, el Python del sistema usado por esta instalación de ROS.

**Comprobación:** abre una terminal integrada de VS Code y ejecuta:

```bash
source /opt/ros/humble/setup.bash
source ~/arm_ws/install/setup.bash
ros2 pkg prefix arm_description
```

Debe aparecer la ruta del paquete `arm_description`. Repite los dos `source` en cada terminal nueva de esta práctica.

## Actividad 2. Crear el paquete y el archivo Python automáticamente

**Propósito:** generar la estructura y el ejecutable sin escribir los archivos de instalación a mano.

Solo si el paquete todavía no existe:

```bash
cd ~/arm_ws/src
ros2 pkg create arm_trajectory_demo \
  --build-type ament_python \
  --node-name send_trajectory \
  --license Apache-2.0 \
  --dependencies rclpy trajectory_msgs
```

| Parte del comando | Para qué sirve |
|---|---|
| `ros2 pkg create arm_trajectory_demo` | Crea la carpeta y los archivos del paquete. |
| `--build-type ament_python` | Selecciona un paquete escrito en Python. |
| `--node-name send_trajectory` | Genera el archivo Python y registra el ejecutable en `setup.py`. |
| `--license Apache-2.0` | Declara la licencia. |
| `--dependencies rclpy trajectory_msgs` | Declara las bibliotecas que usará el script. No las instala. |
| `\` al final de una línea | Permite continuar el mismo comando en la línea siguiente. |

Archivos principales generados:

```text
arm_trajectory_demo/
├── arm_trajectory_demo/
│   ├── __init__.py
│   └── send_trajectory.py
├── resource/arm_trajectory_demo
├── package.xml
├── setup.py
└── setup.cfg
```

`package.xml` describe el paquete y sus dependencias. `setup.py` registra el ejecutable. `setup.cfg` indica dónde instalarlo. `__init__.py` identifica el módulo Python y `resource/arm_trajectory_demo` permite localizar el paquete en el índice de ROS. El generador también puede crear una carpeta `test` y un archivo de licencia.

**No necesitas editar `setup.py`, crear un launch propio ni crear un YAML para esta práctica.** El generador ya registra `send_trajectory`, y reutilizaremos los lanzamientos del proyecto.

Abre el script:

```bash
code ~/arm_ws/src/arm_trajectory_demo/arm_trajectory_demo/send_trajectory.py
```

**Comprobación:** en VS Code deben verse el archivo Python y los archivos de instalación.

## Actividad 3. Insertar una plantilla con un snippet

**Propósito:** crear la base del nodo sin escribir siempre las mismas instrucciones.

Un **snippet** es una plantilla de código. Ya se incluye en `.vscode/ros2_basico.code-snippets` de esta entrega. Para crearlo en otra copia del proyecto:

```bash
cd ~/arm_ws
mkdir -p .vscode
code .vscode/ros2_basico.code-snippets
```

`mkdir -p` crea la carpeta si hace falta. En el archivo abierto, pega este contenido y guárdalo con **Ctrl+S**. Si el archivo ya existe, comprueba su contenido antes de reemplazarlo.

```json
{
  "Publicador ROS 2 basico": {
    "scope": "python",
    "prefix": "ros2pub",
    "isFileTemplate": true,
    "description": "Base sencilla de un publicador de trayectorias",
    "body": [
      "import rclpy",
      "from rclpy.node import Node",
      "from trajectory_msgs.msg import JointTrajectory",
      "",
      "",
      "def main(args=None):",
      "    rclpy.init(args=args)",
      "    node = Node('send_trajectory')",
      "    publisher = node.create_publisher(",
      "        JointTrajectory, '/arm_controller/joint_trajectory', 10)",
      "    # Completa aqui la trayectoria y su envio.",
      "    $0",
      "    node.destroy_node()",
      "    rclpy.shutdown()",
      "",
      "",
      "if __name__ == '__main__':",
      "    main()"
    ]
  }
}
```

| Campo | Significado |
|---|---|
| `scope: python` | La plantilla se ofrece en archivos Python. |
| `prefix: ros2pub` | Palabra que permite buscarla al escribir. |
| `isFileTemplate: true` | Permite usarla como plantilla de un archivo completo. |
| `body` | Líneas que se insertan; cada cadena es una línea del código. |
| `$0` | Lugar donde queda el cursor para continuar escribiendo. |

Para usarla en el archivo generado `send_trajectory.py`:

1. Borra el contenido inicial del archivo generado.
2. Escribe `ros2pub` y pulsa **Ctrl+Espacio**.
3. Selecciona **Publicador ROS 2 basico**.
4. Guarda con **Ctrl+S**.

También puedes abrir **Ctrl+Shift+P → Snippets: Fill File with Snippet** y seleccionar la plantilla. Debe estar abierta la carpeta `arm_ws` completa para que VS Code encuentre sus snippets. [Documentación de snippets](https://code.visualstudio.com/docs/editing/userdefinedsnippets).

**Qué creó la plantilla:**

- `rclpy.init()` inicia la comunicación ROS del programa.
- `Node('send_trajectory')` crea un nodo con ese nombre.
- `create_publisher(...)` prepara la salida de mensajes.
- `destroy_node()` y `shutdown()` liberan los recursos al terminar.

La plantilla aún no mueve el robot: falta construir y enviar el mensaje. Eso se completa en la siguiente actividad.

## Actividad 4. Completar el script de la trayectoria

**Propósito:** definir cuatro destinos y enviarlos al controlador existente.

Un **nodo** es un participante de ROS 2 que realiza una tarea. Nuestro nodo prepara y envía un movimiento. Un **tópico** es un canal de mensajes con nombre y tipo. El controlador del brazo recibe este canal:

```text
Nodo send_trajectory
      ↓ publica JointTrajectory
/arm_controller/joint_trajectory
      ↓ recibe
Controlador arm_controller
      ↓ controla
joint_1, joint_2, joint_3 en Gazebo
```

La conexión se establece cuando coinciden el nombre del tópico, el tipo de mensaje y la configuración de comunicación de ROS. El script es el publicador; el controlador es el suscriptor.

Completa la plantilla para que `send_trajectory.py` quede así. Puedes reemplazar su contenido por este código completo:

```python
"""Enviar cuatro posiciones al brazo simulado."""
import time

import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint


def create_trajectory():
    trajectory = JointTrajectory()
    trajectory.joint_names = ['joint_1', 'joint_2', 'joint_3']
    positions = [
        [0.0, 0.0, 0.0],       # Inicio
        [-0.25, -0.15, 0.10],  # Posicion A
        [0.25, -0.15, 0.10],   # Posicion B
        [0.0, 0.0, 0.0],       # Regreso
    ]
    for index, angles in enumerate(positions):
        point = JointTrajectoryPoint()
        point.positions = angles
        point.time_from_start.sec = (index + 1) * 4
        trajectory.points.append(point)
    return trajectory


def main(args=None):
    rclpy.init(args=args)
    node = Node('send_trajectory')
    publisher = node.create_publisher(
        JointTrajectory, '/arm_controller/joint_trajectory', 10)
    try:
        deadline = time.monotonic() + 10.0
        while publisher.get_subscription_count() == 0:
            if time.monotonic() > deadline:
                node.get_logger().error('No hay suscriptores. Revisa los controladores.')
                return 1
            rclpy.spin_once(node, timeout_sec=0.1)
        publisher.publish(create_trajectory())
        if not publisher.wait_for_all_acked(Duration(seconds=2)):
            node.get_logger().error('No se confirmo la entrega del mensaje.')
            return 1
        node.get_logger().info('Trayectoria enviada. Observa los 16 segundos en Gazebo.')
        return 0
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    raise SystemExit(main())
```

**Explicación del código, en el mismo orden:**

| Instrucción | Qué hace y por qué |
|---|---|
| `import time` | Permite limitar cuánto esperamos una conexión. |
| `import rclpy` | Da acceso a ROS 2 desde Python. |
| `Duration` | Expresa el límite de espera de entrega del mensaje. |
| `Node` | Permite crear el nodo. |
| `JointTrajectory` | Es el mensaje completo: articulaciones y puntos de movimiento. |
| `JointTrajectoryPoint` | Representa un destino y el tiempo para alcanzarlo. |
| `def create_trajectory()` | Agrupa únicamente la construcción del mensaje. |
| `joint_names` | Fija el orden de las tres articulaciones; debe coincidir con el controlador. |
| `positions` | Define cuatro listas de ángulos, en radianes. |
| `enumerate(positions)` | Recorre cada posición junto con su índice: 0, 1, 2 y 3. |
| `point.positions = angles` | Copia los tres ángulos del destino al punto. |
| `(index + 1) * 4` | Asigna los tiempos 4, 8, 12 y 16 segundos desde el comienzo. |
| `trajectory.points.append(point)` | Añade el punto al mensaje completo. |
| `return trajectory` | Entrega el mensaje listo para publicar. |
| `def main(args=None)` | Es la función que ejecuta `ros2 run`; acepta los argumentos de ROS. |
| `create_publisher(..., 10)` | Crea el publicador; 10 es la profundidad del historial de mensajes, no una velocidad. |
| `try` / `finally` | Garantiza que se liberen los recursos al terminar o ante un error. |
| `time.monotonic() + 10.0` | Establece un plazo de diez segundos de tiempo real. |
| `get_subscription_count()` | Comprueba si ya se descubrió algún suscriptor del tópico. |
| `while` | Espera mientras no haya suscriptores. |
| `if time.monotonic() > deadline` | Evita esperar indefinidamente. |
| `spin_once(..., timeout_sec=0.1)` | Atiende comunicaciones de ROS durante la espera. |
| `publish(create_trajectory())` | Envía la trayectoria completa una sola vez. |
| `wait_for_all_acked(...)` | Espera hasta dos segundos la confirmación de entrega a suscriptores fiables. |
| `get_logger().info/error` | Muestra información o explica un problema en la terminal. |
| `return 0` / `return 1` | Indica envío correcto o error, respectivamente. |
| `destroy_node()` / `shutdown()` | Cierra el nodo y la comunicación ROS. |
| `if __name__ == '__main__'` | Permite iniciar el archivo directamente con Python. |
| `raise SystemExit(main())` | Conserva el código de salida devuelto por `main`. |

Los tiempos son **acumulados** dentro de una misma trayectoria:

| Destino | joint_1 | joint_2 | joint_3 | Tiempo desde el inicio |
|---|---:|---:|---:|---:|
| Inicio | 0.00 | 0.00 | 0.00 | 4 s |
| A | -0.25 | -0.15 | 0.10 | 8 s |
| B | 0.25 | -0.15 | 0.10 | 12 s |
| Regreso | 0.00 | 0.00 | 0.00 | 16 s |

El controlador interpola entre los puntos. La cabecera queda con tiempo cero, que indica comenzar la trayectoria al recibirla. No se necesitan coordenadas cartesianas ni cálculo de cinemática inversa para ordenar estas posiciones articulares.

**Diferencia importante:** un suscriptor puede ser el controlador o una herramienta como `ros2 topic echo`. Detectar un suscriptor y confirmar la entrega **no prueba que el brazo haya terminado el movimiento**. Por eso primero comprobaremos que el controlador está activo y después observaremos sus estados.

El script termina tras enviar el mensaje. La trayectoria continúa ejecutándose en el controlador; cerrar el script no la cancela. Esta práctica usa el tópico para mantener el código corto. No incluye seguimiento de resultados mediante acciones ni cancelación desde el script. [Interfaz del controlador de trayectorias](https://control.ros.org/humble/doc/ros2_controllers/joint_trajectory_controller/doc/userdoc.html).

## Actividad 5. Compilar el paquete

**Propósito:** registrar el ejecutable para poder iniciarlo con `ros2 run`.

Guarda el archivo y ejecuta:

```bash
cd ~/arm_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon build --packages-select arm_trajectory_demo
source install/setup.bash
ros2 pkg executables arm_trajectory_demo
```

| Comando | Por qué se ejecuta |
|---|---|
| `cd ~/arm_ws` | La compilación se hace desde la raíz del workspace. |
| Primeros `source` | Habilitan ROS y los paquetes ya instalados del proyecto. |
| `colcon build --packages-select ...` | Construye e instala solamente el paquete nuevo. |
| Segundo `source install/setup.bash` | Actualiza las rutas con el paquete recién instalado. |
| `ros2 pkg executables ...` | Comprueba que ROS encuentra el ejecutable. |

Debe aparecer:

```text
arm_trajectory_demo send_trajectory
```

No hace falta `chmod +x`: el generador registró la función `main` y la instalación crea el ejecutable. Cuando cambies el script, guarda, vuelve a compilar y vuelve a cargar `install/setup.bash`.

## Actividad 6. Iniciar Gazebo y los controladores

**Propósito:** preparar el robot antes de enviar movimientos.

Usa tres terminales. Mantén abiertas A y B mientras trabajas. Cierra otras simulaciones o programas que envíen órdenes al mismo brazo. Esta práctica se realiza sin conectar el controlador del robot físico.

**Terminal A: iniciar Gazebo y cargar el robot.**

```bash
source /opt/ros/humble/setup.bash
source ~/arm_ws/install/setup.bash
ros2 launch arm_description gazebo.launch.py
```

`ros2 launch` ejecuta un archivo de lanzamiento. Aquí se reutiliza el archivo de `arm_description`: inicia Gazebo, publica la descripción e inserta el robot.

**Terminal B: activar los controladores simulados.**

```bash
source /opt/ros/humble/setup.bash
source ~/arm_ws/install/setup.bash
ros2 launch arm_controller controller.launch.py is_sim:=True
```

El lanzamiento activa los controladores del proyecto. `is_sim:=True` selecciona la infraestructura de simulación.

**Terminal C: comprobar que el brazo está listo.**

```bash
source /opt/ros/humble/setup.bash
source ~/arm_ws/install/setup.bash
ros2 control list_controllers
ros2 topic info /arm_controller/joint_trajectory
```

La primera orden debe mostrar `arm_controller` y `joint_state_broadcaster` como `active`. También se carga el controlador de pinza, aunque este ejercicio no le envía órdenes.

La segunda orden debe mostrar el tipo `trajectory_msgs/msg/JointTrajectory` y al menos un suscriptor. No ejecutes la trayectoria si el controlador del brazo no está activo.

## Actividad 7. Enviar la trayectoria y comprobar el movimiento

**Propósito:** relacionar el código con el movimiento del robot.

En la terminal C:

```bash
ros2 run arm_trajectory_demo send_trajectory --ros-args -p use_sim_time:=true
```

- `ros2 run` inicia un ejecutable instalado.
- `arm_trajectory_demo` es el paquete.
- `send_trajectory` es el ejecutable generado.
- `--ros-args` introduce opciones de ROS.
- `-p use_sim_time:=true` configura el nodo para usar el reloj de Gazebo. Los tiempos de la trayectoria los ejecuta el controlador simulado.

Debe aparecer `Trayectoria enviada`. Observa el brazo durante unos 16 segundos de simulación: va al inicio, pasa por A y B y vuelve al inicio. Si Gazebo está pausado, el tiempo simulado no avanza.

Para observar posiciones durante el movimiento, abre otra terminal, carga el entorno y ejecuta:

```bash
source /opt/ros/humble/setup.bash
source ~/arm_ws/install/setup.bash
ros2 topic echo /joint_states
```

`/joint_states` contiene listas de nombres y posiciones. Busca `joint_1`, `joint_2` y `joint_3`, y relaciona cada nombre con la posición del mismo índice. Detén la observación con **Ctrl+C**; eso solo detiene el comando de observación.

Al terminar la trayectoria, puedes consultar una sola muestra:

```bash
ros2 topic echo /joint_states --once
```

Las tres articulaciones del brazo deben estar aproximadamente en `[0.0, 0.0, 0.0]`. La pinza puede mostrar otro valor porque no forma parte de esta trayectoria. El nodo `send_trajectory` desaparece cuando termina de enviar: es normal que no esté en `ros2 node list` durante todo el movimiento.

**Prueba de aprendizaje: modificar solo un número.**

En `create_trajectory()`, cambia la fila de la posición B por:

```python
        [0.15, -0.15, 0.10],   # Posicion B con menor giro de la base
```

Guarda y reinstala:

```bash
cd ~/arm_ws
colcon build --packages-select arm_trajectory_demo
source install/setup.bash
ros2 run arm_trajectory_demo send_trajectory --ros-args -p use_sim_time:=true
```

`joint_1` debe girar menos hacia B. Cambia solo valores pequeños durante la práctica. El URDF permite aproximadamente de `-1.57` a `1.57` rad en las tres articulaciones, pero estar dentro del límite no garantiza evitar colisiones. Este script básico no valida límites ni planifica para evitar obstáculos.

Para disminuir la velocidad media, cambia esta instrucción:

```python
        point.time_from_start.sec = (index + 1) * 6
```

Ahora los destinos se alcanzan a los 6, 12, 18 y 24 segundos. Guarda, recompila y vuelve a ejecutar. Espera a que termine una trayectoria antes de enviar otra; una nueva orden puede reemplazar la anterior.

**Entrega:** código del script, captura de los controladores activos y una comparación breve entre la trayectoria inicial y la modificada. Explica qué hacen `joint_names`, `positions` y `time_from_start`.

## Comprobación de esta entrega

Verificado el 21 de octubre de 2026 con ROS 2 Humble y Gazebo Classic:

- El paquete compila y registra el ejecutable `send_trajectory`.
- El mensaje contiene tres articulaciones y cuatro puntos con tiempos crecientes: 4, 8, 12 y 16 segundos.
- Sin suscriptores, el programa termina con un error claro después del plazo de espera.
- En Gazebo, el brazo pasó por A y B en ese orden y regresó al inicio. Se observaron 219 mensajes de estado; las posiciones finales de las tres articulaciones quedaron aproximadamente en cero.
- Se comprobó la sintaxis de los 14 bloques de comandos, el JSON del snippet y el código Python de la plantilla. El código completo mostrado en la actividad 4 coincide con el script entregado.

La prueba usó los lanzamientos existentes del modelo y los controladores, suprimiendo únicamente la ventana de Gazebo para la ejecución automática. Se comprobó el movimiento mediante estados de la simulación; no se probó la visualización gráfica ni hardware físico. Los registros se conservaron en `~/arm_ws/log/arm_trajectory_demo_validation/`.

Las comprobaciones con `/joint_states` de esta guía se refieren a Gazebo. La interfaz del robot físico del proyecto copia las posiciones ordenadas a sus estados: esos valores no demostrarían precisión física.

## Si algo no funciona

| Problema | Qué revisar |
|---|---|
| El paquete ya existe | Omitir el comando de creación; no crear otro paquete del mismo nombre dentro del workspace. |
| No aparece `ros2pub` | Abrir `arm_ws` como carpeta de VS Code, guardar el archivo de snippets y usarlo dentro de un archivo `.py`. |
| `Package not found` | Compilar y cargar `install/setup.bash` en la terminal actual. |
| El cambio del script no aparece | Guardar y volver a compilar; esta práctica usa instalación normal. |
| `No hay suscriptores` | Comprobar el lanzamiento y los controladores activos. El script termina con error tras unos diez segundos. |
| Se envía el mensaje, pero no hay movimiento | Verificar `arm_controller active`, que Gazebo esté en ejecución y que otro programa no sustituya la trayectoria. |
| No se encuentra `rclpy` | Cargar el entorno ROS y seleccionar `/usr/bin/python3` en VS Code. |
| Error al crear el publicador o al conectar | Revisar que la terminal permita comunicación local y que todos los procesos usen el mismo dominio ROS. |
