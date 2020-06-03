from configargparse import ArgParser, Namespace, YAMLConfigFileParser
from threading import Thread
from sys import exit
from socket import create_server, SHUT_RDWR

from socket_server import serve
from notification_handler import notify
from tray_icon_handler import get_tray_icon

from functools import partial
from typing import List



def main() -> int:
    running = [True]
    config = parse_config()

    icon = get_tray_icon()
    socket = create_server(("", config.port))

    network_thread = Thread(target=serve, args=(socket, handle_msg, running, ))
    network_thread.start()

    try:
        icon.run()
    except AttributeError:
        # Can't get rid of a strange AttributeError, not sure if upstream bug
        pass
    except Exception as ex:
        print("Unknown Error: ", ex)

    print("Shutting down server...")
    running.clear()
    socket.shutdown(SHUT_RDWR)

    network_thread.join()
    return 0

def handle_msg(title: str, msg : str) -> None:
    notify(title, msg)

def parse_config() -> Namespace:
    parser = ArgParser(config_file_parser_class = YAMLConfigFileParser, default_config_files = ["config.yml"])
    parser.add('-c', '--config', is_config_file=True, help='notification server config in yaml format (.yml)')
    parser.add('-p', '--port', type=int, required=True, help='notification server port')
    parser.add('-s', '--secrets-file', type=str, required=True, help='secrets file path')
    return parser.parse_args()

if __name__ == "__main__":
    exit(main())

