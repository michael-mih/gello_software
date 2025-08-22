import os
import subprocess

current_file_path = os.path.abspath(__file__)

def run_docker_container():
    user = os.getenv("USER")
    container_name = f"gello_{user}"
    gello_path = os.path.abspath(os.path.join(current_file_path, "../../"))
    volume_mapping = f"{gello_path}:/gello"

    # Get DISPLAY and X11 socket path
    display_var = os.getenv("DISPLAY", ":0")
    x11_socket = "/tmp/.X11-unix"
    try:
        subprocess.run(["xhost", "+local:root"], check=True)
    except FileNotFoundError:
        print("xhost not found — please install 'x11-xserver-utils' on host.")
    except subprocess.CalledProcessError:
        print("Failed to run xhost — X server permissions may block GUI.")
    cmd = [
        "docker",
        "run",
        "--runtime=nvidia",
        "--rm",
        "--name", container_name,
        "--privileged",
        "--net=host",
        "--env", f"DISPLAY={display_var}",
        "--volume", f"{x11_socket}:{x11_socket}:rw",  # X11 socket
        "--volume", volume_mapping,
        "--volume", "/home/gello:/homefolder",
        "--volume", "/dev/serial/by-id/:/dev/serial/by-id/",
        "--volume", "/usr/share/vulkan/icd.d:/usr/share/vulkan/icd.d:ro",
        #If you have an nvidia gpu
        "-e", "NVIDIA_DRIVER_CAPABILITIES=all",
        "-e", "NVIDIA_VISIBLE_DEVICES=all",
        "-it",
        "gello:latest",
        "bash",
        "-c",
        # Install missing tools, then start
        "apt-get update && apt-get install -y sudo psmisc && "
        "pip install -e third_party/DynamixelSDK/python && exec bash",
    ]

    subprocess.run(cmd)

if __name__ == "__main__":
    run_docker_container()
