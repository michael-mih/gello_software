# WIP GELLO fork for Sapien Simulation and Teleop for Dexmate VEGA

<p align="center">
  <img src="imgs/title.png" />
</p>
This repository contains software components for using the GELLO in SAPIEN as well as for teleop with the Dexmate VEGA. 
GELLO is a general, low-cost, and intuitive teleoperation framework for robot manipulators. 

For additional resources:
- [Project Website](https://wuphilipp.github.io/gello_site/)
- [Dexmate Github](https://github.com/dexmate-ai)

## Quick Start

```bash
git clone https://github.com/michael-mih/gello_software.git
cd gello_software
```

## Installation


### Docker

Install [Docker](https://docs.docker.com/engine/install/ubuntu/), then:

```bash
docker build . -t gello:latest
python scripts/launch_with_X11.py
```
## Usage (VEGA)
On robot:
```bash
dextop node start
```
On client:
```bash
// ask your admin to get the communication certificates
dextop cert unpack <certificate_file>.zip  
dextop cfg gen
export ROBOT_NAME=<the robot name>
```
For simulation or real-world, run each respectively:
```bash
python experiments/launch_yaml.py --left-config-path configs/sapien_dexmate.yaml 
python experiments/launch_yaml.py --left-config-path configs/dexmate.yaml 
```

## Adding New Robots

To integrate a new robot to the Python configs:

1. **Check Compatibility**: Ensure your GELLO kinematics match the target robot
2. **Implement Robot Interface**: Create a new class implementing the `Robot` protocol from `gello/robots/robot.py`
3. **Add Configuration**: Update the configuration system with your robot's parameters

#### Configuration Components

- **Robot Config**: Defines robot type, communication parameters, and physical settings.
- **Agent Config**: Defines GELLO device settings, joint mappings, and calibration.
- **DynamixelRobotConfig**: Motor-specific settings including IDs, offsets, signs, and gripper.
- **Control Parameters**: Update rates (`hz`), step limits (`max_steps`), and safety settings.
See existing implementations in `gello/robots/` for reference:
- `dexmate.py` - VEGA robot
- `sapien_sim_robot.py`- robot simulated in SAPIEN (VEGA by default)

#### Create Custom YAML Configurations
1. Copy an existing config from `configs/` as a template.
2. Modify the robot `_target_` and parameters for your setup:
   - For hardware: `gello.robots.ur.URRobot`, `gello.robots.panda.PandaRobot`, etc.
   - For SAPIEN simulation: `gello.robots.sapien_sim_robot.SapienRobotServer`
3. Update the agent configuration with your GELLO device settings:
   - `port`: Your U2D2 device path
   - `joint_offsets`: From the offset detection script
   - `joint_signs`: Based on your robot type
   - `start_joints`: Your GELLO's starting position

### Troubleshooting

If some joints in your arm are not behaving as expected, you may need to modify the joint signs of your configuration. Simply invert the affected joint sign(s) in your .yaml or `gello_agent.py` or physically reverse the installation of the servo.

## Development

### Code Organization

```
├── scripts/             # Utility scripts
├── experiments/         # Entry points and launch scripts
├── gello/               # Core GELLO package
│   ├── agents/          # Teleoperation agents
│   ├── cameras/         # Camera interfaces
│   ├── data_utils/      # Data processing utilities
│   ├── dm_control_tasks/# MuJoCo environment utilities
│   ├── dynamixel/       # Dynamixel hardware interface
│   ├── robots/          # Robot-specific interfaces
│   ├── utils/           # Shared launch and control utilities
│   └── zmq_core/        # ZMQ multiprocessing utilities
```

### Contributing

Install development dependencies and set up pre-commit hooks to ensure code quality before contributing:
```bash
uv pip install -r requirements_dev.txt
uv pip install pre-commit
pre-commit install
```

The codebase uses `isort` and `black` for code formatting.

We welcome contributions! Submit pull requests to help make teleoperation more accessible and higher quality.

## Citation

```bibtex
@misc{wu2023gello,
    title={GELLO: A General, Low-Cost, and Intuitive Teleoperation Framework for Robot Manipulators},
    author={Philipp Wu and Yide Shentu and Zhongke Yi and Xingyu Lin and Pieter Abbeel},
    year={2023},
}
```

## License & Acknowledgements

This project is licensed under the MIT License (see LICENSE file).

### Third-Party Dependencies
- [google-deepmind/mujoco_menagerie](https://github.com/google-deepmind/mujoco_menagerie): Robot models for MuJoCo
- [brentyi/tyro](https://github.com/brentyi/tyro): Argument parsing and configuration
- [ZMQ](https://zeromq.org/): Multiprocessing communication framework
