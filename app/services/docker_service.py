import socket

import docker


class DockerService:
    def __init__(self) -> None:
        self.client = docker.from_env()

    def get_free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.listen(1)
            return int(s.getsockname()[1])

    def run_container(self, name: str, image: str, internal_port: int, external_port: int):
        container = self.client.containers.run(
            image=image,
            detach=True,
            name=name,
            ports={f"{internal_port}/tcp": external_port},
        )
        return container

    def stop_container(self, container_id: str) -> None:
        container = self.client.containers.get(container_id)
        container.stop()

    def remove_container(self, container_id: str) -> None:
        container = self.client.containers.get(container_id)
        container.remove(force=True)

    def get_logs(self, container_id: str) -> str:
        container = self.client.containers.get(container_id)
        return container.logs(tail=100).decode("utf-8")