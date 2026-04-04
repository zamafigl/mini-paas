import os
import socket
from pathlib import Path

import docker


class DockerService:
    def __init__(self) -> None:
        self.client = docker.from_env()
        self.docker_network = os.getenv("DOCKER_NETWORK", "mini-paas_default")
        self.nginx_container_name = os.getenv("NGINX_CONTAINER_NAME", "mini-paas-nginx")
        self.nginx_dynamic_dir = Path(os.getenv("NGINX_DYNAMIC_DIR", "/app/nginx/dynamic"))

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
            network=self.docker_network,
        )
        return container

    def start_container(self, container_id: str) -> None:
        container = self.client.containers.get(container_id)
        container.start()

    def stop_container(self, container_id: str) -> None:
        container = self.client.containers.get(container_id)
        container.stop()

    def restart_container(self, container_id: str) -> None:
        container = self.client.containers.get(container_id)
        container.restart()

    def remove_container(self, container_id: str) -> None:
        container = self.client.containers.get(container_id)
        container.remove(force=True)

    def get_logs(self, container_id: str) -> str:
        container = self.client.containers.get(container_id)
        return container.logs(tail=100).decode("utf-8")

    def write_nginx_route(self, app_id: int, container_name: str, internal_port: int) -> None:
        self.nginx_dynamic_dir.mkdir(parents=True, exist_ok=True)
        route_file = self.nginx_dynamic_dir / f"app-{app_id}.conf"

        route_file.write_text(
            f"""
location /apps/{app_id}/ {{
    proxy_pass http://{container_name}:{internal_port}/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}}
""".strip()
            + "\n",
            encoding="utf-8",
        )

    def remove_nginx_route(self, app_id: int) -> None:
        route_file = self.nginx_dynamic_dir / f"app-{app_id}.conf"
        if route_file.exists():
            route_file.unlink()

    def reload_nginx(self) -> None:
        nginx_container = self.client.containers.get(self.nginx_container_name)
        exit_code, output = nginx_container.exec_run("nginx -s reload")
        if exit_code != 0:
            raise RuntimeError(output.decode("utf-8"))
