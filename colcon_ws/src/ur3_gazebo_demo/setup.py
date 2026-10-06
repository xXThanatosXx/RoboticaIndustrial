from setuptools import setup

package_name = "ur3_gazebo_demo"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/config", ["config/pick_and_place.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Shadow",
    maintainer_email="shadow@example.com",
    description="Simple ROS 2 demo that sends a UR3 joint trajectory to Gazebo.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "ur3_joint_trajectory = ur3_gazebo_demo.ur3_joint_trajectory:main",
            "ur3_pick_and_place = ur3_gazebo_demo.ur3_pick_and_place:main",
        ],
    },
)
