import time
from typing import Dict

import numpy as np


import numpy as np
import tyro
from base_arm_teleop import BaseArmTeleopNode, BaseIKController
from loguru import logger

from dexcontrol.utils.rate_limiter import RateLimiter

from gello.robots.robot import Robot as GelloRobot
from dexcontrol.robot import Robot as DexcontrolRobot
from dexcontrol import Robot as DexcontrolRobot

#TODO why does the docs refer to the follower as leader?

class DexmateRobot(GelloRobot):
    def init(self):
        
        self._num_joints = 7
    

        self._dexmateBot = DexcontrolRobot()

        self._arm = self._dexmateBot.left_arm
        self._arm.set_mode("position")


        self._joint_state = np.zeros(self._num_joints)

    def num_dofs(self):
        return self._num_joints

    def get_joint_state(self) -> np.ndarray:
        self._joint_state = np.array(self._arm.get_joint_pos())
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
        self._joint_state= joint_state
        
        
        #IMPORTANT: When wait_time is 0, you MUST call this function repeatedly
         #       in a high-frequency loop (e.g., 100 Hz). DO NOT call it just once!
          #      The function is designed for continuous control when wait_time=0.
           #     The highest frequency that the user can call this function is 500 Hz.

        #TODO: is GELLO agent loop high enough frequency? set in dexmate.yaml?
        self._arm.set_joint_pos(self._joint_state,wait_time=0.0)


    def get_observations(self) -> Dict[str, np.ndarray]:
        joint_positions = np.array(self._arm.get_joint_pos_dict())
        joint_velocities = np.array(self._arm.get_joint_vel_dict())

        

        return {
            "joint_positions": joint_positions,
            "joint_velocities": joint_velocities,
            #"ee_pos_quat": np.concatenate([ee_pos, ee_quat]), #TODO: FK? dexmotion motionplanner? 
            #"gripper_position": gripper_pos, #TODO opened or closed? need to connect robotiq gripper
        }
    
