import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = FindPackageShare(package='rover_parkur').find('rover_parkur')

    # Gazebo'nun internet sunucusuna bağlanıp takılmasını önlemek için online database URI'sini boşaltıyoruz.
    os.environ['GAZEBO_MODEL_DATABASE_URI'] = ''

    # Gazebo'nun model:// ve package:// yollarını bulabilmesi için model yollarını ayarlıyoruz.
    pkg_parent = os.path.dirname(pkg_share)

    gazebo_model_path = os.environ.get('GAZEBO_MODEL_PATH', '')
    gazebo_resource_path = os.environ.get('GAZEBO_RESOURCE_PATH', '')

    os.environ['GAZEBO_MODEL_PATH'] = pkg_parent + ':/usr/share/gazebo-11/models' + (':' + gazebo_model_path if gazebo_model_path else '')
    os.environ['GAZEBO_RESOURCE_PATH'] = pkg_parent + (':' + gazebo_resource_path if gazebo_resource_path else '')

    # Kayar engel plugin'inin (libkayar_engel_plugin.so) bulunabilmesi için plugin yolu
    gazebo_plugin_path = os.environ.get('GAZEBO_PLUGIN_PATH', '')
    os.environ['GAZEBO_PLUGIN_PATH'] = os.path.join(pkg_share, 'plugins') + (':' + gazebo_plugin_path if gazebo_plugin_path else '')

    # Gazebo'yu yeni parkur dünyasıyla başlat (parkur world dosyasının içinde, ayrıca spawn gerekmiyor)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare('gazebo_ros').find('gazebo_ros'),
            '/launch/gazebo.launch.py'
        ]),
        launch_arguments={'world': os.path.join(pkg_share, 'worlds', 'parkur_yeni.world')}.items()
    )

    # Rover URDF'ini oku ve controller yapılandırma dosyasının yolunu yerleştir
    rover_urdf_file = os.path.join(pkg_share, 'urdf', 'rover.urdf')
    controllers_config = os.path.join(pkg_share, 'config', 'rover_controllers.yaml')
    with open(rover_urdf_file, 'r') as f:
        rover_description = f.read().replace('${CONTROLLERS_CONFIG}', controllers_config)

    # Robot state publisher (Rover)
    robot_state_pub_rover = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_rover',
        output='screen',
        parameters=[{
            'robot_description': rover_description,
            'use_sim_time': True,
        }]
    )

    # Rover'ı parkurun başlangıç kenarına, zeminin biraz üstüne bırak
    spawn_entity_rover = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity_rover',
        arguments=[
            '-topic', '/robot_description',
            '-entity', 'rover',
            '-x', '2.40', '-y', '-0.35', '-z', '0.3',
            '-R', '0', '-P', '0', '-Y', '-3.106'
        ],
        output='screen'
    )

    # Controller spawner'ları: rover spawn edildikten sonra başlat
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    wheel_velocity_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['wheel_velocity_controller', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    start_controllers = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity_rover,
            on_exit=[joint_state_broadcaster_spawner, wheel_velocity_controller_spawner]
        )
    )

    # Skid-steer kontrolcü: /cmd_vel -> 4 teker hızı
    skid_steer_node = Node(
        package='rover_parkur',
        executable='skid_steer_controller.py',
        name='skid_steer_controller',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    ld = LaunchDescription()
    ld.add_action(gazebo)
    ld.add_action(robot_state_pub_rover)
    ld.add_action(spawn_entity_rover)
    ld.add_action(start_controllers)
    ld.add_action(skid_steer_node)

    return ld
