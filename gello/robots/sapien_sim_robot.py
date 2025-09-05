import pickle
import threading
from typing import Any, Dict, Optional
import sapien
import numpy as np
import zmq
from gello.robots.robot import Robot

#TODO abstract for any robot?

class SapienRobotServer(Robot):

    """Setup independent between robots, such as collision groups and drive properties.
    Will likely need to modify for your own robot
    """
    def vega_setup(self) -> None:
        for link_idx, link in enumerate(self._robot_sapien.get_links()):
                if(link.name == "L_arm_l8"):
                    self._eef_idx = link_idx
                for shape in link.get_collision_shapes():
                    shape.set_collision_groups([1, 1, 17, 0])
        
        #For now no EEF so just end of left arm
        self._eef_link = self._robot_sapien.get_links()[self._eef_idx]
        
        for joint_idx, joint in enumerate(self._robot_sapien.get_active_joints()):
                if "torso" in joint.name:
                    joint.set_drive_property(
                        stiffness=4000, damping=500, mode="acceleration"
                    )
                else:
                    joint.set_drive_property(
                        stiffness=4000, damping=500, force_limit=1000, mode="force"
                    )

    
    def __init__(self, urdf_path: str,
                 gripper_urdf_path: Optional[str] = None, 
                 host: str = "127.0.0.1",
                 port: int = 5556,
                 print_joints: bool = False
                 ):
        
        self._scene = sapien.Scene()
        self._scene.add_ground(-0.1)

        self._scene.set_ambient_light([0.5, 0.5, 0.5])
        self._scene.add_directional_light([0, 1, -1], [0.5, 0.5, 0.5])

        loader = self._scene.create_urdf_loader()
        loader.fix_root_link = True
        loader.load_multiple_collisions_from_file = True
        self._robot_sapien = loader.load(urdf_path)

        

        ##Any unique robot setup (collisions, drive properties, etc) setup here
        self.vega_setup()

        self._zmq_server = ZMQRobotServer(robot=self, host=host, port=port)
        self._zmq_server_thread = ZMQServerThread(self._zmq_server)
        
        
        #Assuming you are teleoperating just a part of the robot (ex. arm) list the relevant joints in order.
        left_arm_idx = [10, 13, 16, 18, 20, 22, 24]
        #right_idx = [11, 14, 17, 19, 21, 23, 25]

        self._active_idx = left_arm_idx
        
        self._active_joints = self._robot_sapien.get_active_joints()

        self._num_joints = len(self._active_idx)
        self._joint_state = np.zeros(self._num_joints)
        self._joint_cmd = self._joint_state
        self._print_joints = print_joints
    
    def num_dofs(self) -> int:
        """Get the number of joints of the robot.

        Returns:
            int: The number of joints of the robot.
        """
        return self._num_joints

    def get_joint_state(self) -> np.ndarray:
        """Get the current state of the leader robot.

        Returns:
            T: The current state of the leader robot.
        """
        
        return self._joint_state

    def command_joint_state(self, joint_state: np.ndarray) -> None:
        """Command the leader robot to a given state.

        Args:
            joint_state (np.ndarray): The state to command the leader robot to.
        """
        if len(joint_state) != self._num_joints:
            assert len(joint_state) == self._num_joints, (
            f"Expected joint state of length {self._num_joints}, "
            f"got {len(joint_state)}."
        )
        self._joint_cmd = joint_state.copy()

    def get_observations(self) -> Dict[str, np.ndarray]:
        """Get the current observations of the robot.

        This is to extract all the information that is available from the robot,
        such as joint positions, joint velocities, etc. This may also include
        information from additional sensors, such as cameras, force sensors, etc.

        Returns:
            Dict[str, np.ndarray]: A dictionary of observations.
        """
        #only pull relevant joints
        joint_positions = np.array([self._robot_sapien.get_qpos()[i] for i in self._active_idx])
        joint_velocities = np.array([self._robot_sapien.get_qvel()[i] for i in self._active_idx])
        
        ee_pos = self._eef_link.get_articulation().get_pose().p
        ee_quat = self._eef_link.get_articulation().get_pose().q
        gripper_pos = joint_positions[len(joint_positions)-1]

        return {
            "joint_positions": joint_positions,
            "joint_velocities": joint_velocities,
            "ee_pos_quat": np.concatenate([ee_pos, ee_quat]),
            "gripper_position": gripper_pos,
        }

    def serve(self) -> None:
        self._zmq_server_thread.start()
        
        viewer = self._scene.create_viewer()
        viewer.set_camera_xyz(x=-2, y=0, z=1)
        viewer.set_camera_rpy(r=0, p=-0.3, y=0)
        self._robot_sapien.set_root_pose(sapien.Pose([0, 0, 0], [1, 0, 0, 0]))

        while not viewer.closed:
        
            for i in range (self._num_joints):
                self._active_joints[self._active_idx[i]].set_drive_target(self._joint_cmd[i])
            self._scene.step()
            self._scene.update_render()
            viewer.render()
            if(self._print_joints):
                print(f"Joint States: {self._joint_cmd}")



class ZMQServerThread(threading.Thread):
    def __init__(self, server):
        super().__init__()
        self._server = server

    def run(self):
        self._server.serve()

    def terminate(self):
        self._server.stop()


class ZMQRobotServer:
    """A class representing a ZMQ server for a robot."""

    def __init__(self, robot: Robot, host: str = "127.0.0.1", port: int = 5556):
        self._robot = robot
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        addr = f"tcp://{host}:{port}"
        self._socket.bind(addr)
        self._stop_event = threading.Event()

    def serve(self) -> None:
        """Serve the robot state and commands over ZMQ."""
        self._socket.setsockopt(zmq.RCVTIMEO, 1000)  # Set timeout to 1000 ms
        while not self._stop_event.is_set():
            try:
                message = self._socket.recv()
                request = pickle.loads(message)

                # Call the appropriate method based on the request
                method = request.get("method")
                args = request.get("args", {})
                result: Any
                if method == "num_dofs":
                    result = self._robot.num_dofs()
                elif method == "get_joint_state":
                    result = self._robot.get_joint_state()
                elif method == "command_joint_state":
                    result = self._robot.command_joint_state(**args)
                elif method == "get_observations":
                    result = self._robot.get_observations()
                else:
                    result = {"error": "Invalid method"}
                    print(result)
                    raise NotImplementedError(
                        f"Invalid method: {method}, {args, result}"
                    )
                
  
                self._socket.send(pickle.dumps(result))
            except zmq.error.Again:
                print("Timeout in ZMQLeaderServer serve")
                # Timeout occurred, check if the stop event is set

    def stop(self) -> None:
        self._stop_event.set()
        self._socket.close()
        self._context.term()
