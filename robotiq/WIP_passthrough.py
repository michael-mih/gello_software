# Copyright (C) 2025 Dexmate Inc.
#
# This software is dual-licensed:
#
# 1. GNU Affero General Public License v3.0 (AGPL-3.0)
#    See LICENSE-AGPL for details
#
# 2. Commercial License
#    For commercial licensing terms, contact: contact@dexmate.ai

"""Example script demonstrating customized end effector control via RS485 pass-through.

This script shows how to control a custom end effector (e.g., gripper, tool) by sending
raw RS485 commands through the robot arm's pass-through mode.
"""

from dexcontrol import Robot
from time import sleep

'[docs] See link below for Robotiq modbus RTU frame examples'
'[docs] https://assets.robotiq.com/website-assets/support_documents/document/online/Hand-E_TM_InstructionManual_HTML5_20190306.zip/Hand-E_TM_InstructionManual_HTML5/Content/4.%20Control.html'

def main():
    bot = Robot()
    arm = bot.left_arm   # or right_arm if gripper is connected there

    #clear activation 
    print("clearing act")
    clear_act = "09 10 03 E8 00 03 06 00 00 00 00 00 00 73 30"
    print(arm.send_ee_pass_through_message(bytes.fromhex(clear_act)))
    sleep(1)
    
    #set act
    print("setting act")5
    #set_act = "09 10 03 E8 00 03 06 01 00 00 00 00 00 72 E1"
    set_act = "09 10 07 D0 00 03 06 01 00 00 00 00 00 E6 C4"
    arm.send_ee_pass_through_message(bytes.fromhex(set_act))
    
    sleep(2)
    print("Opening and closing gripper")
    close_gripper = "09 10 03 E8 00 03 06 09 00 00 FF FF FF 42 29"
    arm.send_ee_pass_through_message(bytes.fromhex(close_gripper))
    sleep(2)
    open_gripper = "09 10 03 E8 00 03 06 09 00 00 00 FF FF 72 19"
    arm.send_ee_pass_through_message(bytes.fromhex(open_gripper))

    # Optionally, shutdown the robot after use
    bot.shutdown()


if __name__ == "__main__":
    main()