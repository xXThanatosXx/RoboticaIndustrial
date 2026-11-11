# Verificación de arm_student_demo

Fecha: 21 de octubre de 2026. Entorno: ROS 2 Humble y Gazebo Classic, en el workspace `/home/ros/arm_ws`.

## Resultados

| Comprobación | Resultado |
|---|---|
| Construcción con `colcon build --packages-select arm_student_demo` | Correcta. |
| Registro del ejecutable | `arm_student_demo sequence_controller`. |
| Argumentos de `sequence.launch.py` | Disponibles `is_sim` y `config`. |
| Pruebas automatizadas | 15 aprobadas; ejecución final: 1.65 s. |
| Gazebo, configuración inicial, tres ciclos | 21 movimientos completados; regreso a `home`; 1094 mensajes de estado recibidos. |
| Gazebo, variante B, mediante `sequence.launch.py` y YAML externo | Un ciclo, siete movimientos completados; regreso a `home`; 581 mensajes de estado recibidos. |
| Código incluido en la guía | Coincide con los siete archivos de implementación e instalación documentados. |
| Sintaxis de bloques de la guía | 23 bloques de comandos, cuatro de Python, tres de YAML y uno de XML revisados sin ejecutarlos como instrucciones. |

Las pruebas automatizadas cubren parámetros válidos, nueve configuraciones inválidas, tres ciclos con servidores de prueba, objetivo rechazado, ejecución abortada, cancelación por tiempo agotado y servidor ausente. Usan acciones con rutas privadas bajo `/student_test/`, distintas en cada prueba.

## Estados observados en Gazebo

Ángulos en radianes, redondeados a cuatro decimales. Se tomaron de `/joint_states` de la simulación.

| Articulación | Mínimo, rutina inicial | Máximo, rutina inicial | Final |
|---|---:|---:|---:|
| joint_1 | -0.2500 | 0.2500 | 0.0000 |
| joint_2 | -0.1500 | 0.0000 | 0.0000 |
| joint_3 | 0.0000 | 0.1000 | 0.0000 |
| joint_4 | -0.3500 | 0.0000 | -0.3500 |

| Articulación | Mínimo, variante B | Máximo, variante B | Final |
|---|---:|---:|---:|
| joint_1 | -0.3500 | 0.1500 | 0.0000 |
| joint_2 | -0.2000 | 0.0000 | 0.0000 |
| joint_3 | -0.0002 | 0.1500 | 0.0000 |
| joint_4 | -0.3500 | 0.0000 | -0.3500 |

La comprobación automática exige cambios de más de 0.04 rad en cada articulación y una diferencia final inferior a 0.05 rad respecto al destino. Además comprueba el número de resultados exitosos y el mensaje `SECUENCIA COMPLETADA`.

## Reproducción

```bash
cd ~/arm_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ROS_LOCALHOST_ONLY=1 ROS_DOMAIN_ID=175 \
  python3 -m pytest -q src/arm_student_demo/test/test_sequence.py
python3 src/arm_student_demo/test/verify_gazebo.py
python3 src/arm_student_demo/test/verify_gazebo.py --variant
```

La prueba de Gazebo usa el dominio ROS 174, conexión local y el puerto Gazebo 11359. Inicia y termina su propia simulación. No ejecutarla dos veces simultáneamente.

Los registros temporales de Gazebo y la rutina se escriben en `/tmp/arm_student_gazebo.log` y `/tmp/arm_student_sequence.log`; cada ejecución los reemplaza. Se conservó una copia de los registros de la variante B en `/home/ros/arm_ws/log/arm_student_demo_validation/`.

## Alcance y limitaciones

- Gazebo se ejecutó sin ventana (`gui:=false`), con sus controladores reales de simulación. La rutina no se validó solamente con servidores de prueba.
- Se necesitó acceso local ampliado porque el entorno restringido bloqueaba los sockets ROS/Gazebo y la carpeta de trabajo de Gazebo.
- El controlador existente funciona a 10 Hz y Gazebo advierte que ese periodo es mayor que el de la física. La prueba completó correctamente con esa configuración. No se cambiaron los controladores originales.
- No se conectó ni se movió un robot físico. La transferencia al hardware está documentada, pero requiere una prueba supervisada de puerto, firmware, calibración y movimiento.
- La interfaz física existente copia posiciones ordenadas a estados publicados y los controladores usan lazo abierto. Estos resultados no acreditan precisión física, ausencia de colisiones ni capacidad de agarrar objetos.
