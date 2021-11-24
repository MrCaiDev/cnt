from re import fullmatch

from utils.constant import InputType, MessageType, Mode, Network
from utils.io import get_device_map, search_rsc

from layer._abstract import AbstractLayer


class AppLayer(AbstractLayer):
    """主机应用层。"""

    def __init__(self, device_id: str) -> None:
        """
        初始化应用层。

        Args:
            device_id: 设备号。
        """
        self._device_id = device_id
        config = get_device_map(device_id)
        super().__init__(config["app"])
        self._net = config["net"]

    def __str__(self) -> str:
        """打印应用层信息。"""
        return f"[Device {self._device_id}] <App Layer @{self._port}>"

    def receive_from_net(self) -> str:
        """
        从网络层接收消息。

        Returns:
            接收到的消息。
        """
        # 保证消息来自网络层。
        port = None
        while port != self._net:
            message, port, _ = self._receive(bufsize=Network.IN_NE_BUFSIZE)

        return message

    def send_to_net(self, message: str) -> int:
        """
        向网络层发送消息。

        Args:
            message: 要发的消息。

        Returns:
            总共发送的字节数。
        """
        return self._send(message, self._net)

    def receive_from_user(self, input_type: InputType) -> str:
        """
        从用户键盘输入接收消息。

        Args:
            input_type: 用户输入的分类，包括下列五种：
            - `utils.constant.InputType.MODE`：网元模式。
            - `utils.constant.InputType.DST`：目标应用层端口号。
            - `utils.constant.InputType.MSGTYPE`：要发送的消息类型。
            - `utils.constant.InputType.TEXT`：要发送的消息。
            - `utils.constant.InputType.FILE`：要发送的文件名。

        Returns:
            接收到的消息。
        """
        if input_type == InputType.MODE:
            return AppLayer._get_mode_from_user()
        elif input_type == InputType.DST:
            return self._get_dst_from_user()
        elif input_type == InputType.MSGTYPE:
            return AppLayer._get_msgtype_from_user()
        elif input_type == InputType.TEXT:
            return AppLayer._get_text_from_user()
        elif input_type == InputType.FILE:
            return AppLayer._get_file_from_user()
        else:
            return ""

    @staticmethod
    def _get_mode_from_user() -> str:
        """
        从用户键盘输入获取当前工作模式。

        Returns:
            网元当前的工作模式，包括下列四种：
            - `utils.constant.Mode.RECEIVE`: 接收模式。
            - `utils.constant.Mode.UNICAST`: 单播模式。
            - `utils.constant.Mode.BROADCAST`: 广播模式。
            - `utils.constant.Mode.QUIT`: 退出程序。
        """
        print(
            f"""{'-'*29}\n|{'Select Mode'.center(27)}|\n| 1::Receive     2::Unicast |\n| 3::Broadcast   4::Quit    |\n{'-'*29}"""
        )
        while True:
            mode = input(">>> ")
            if mode in Mode.LIST:
                return mode
            else:
                print("[Warning] Invalid mode.")

    def _get_dst_from_user(self) -> str:
        """
        从用户键盘输入获取目的应用层端口号。

        Returns:
            目的应用层端口号。
        """
        print("Input destination device ID:")
        while True:
            device_id = input(">>> ")

            # 只能输入1-9间的整数。
            if not fullmatch(r"[1-9]", device_id):
                print("[Warning] ID should be an integer between 1 and 9.")
                continue

            # 不能输入本机设备号。
            if device_id == self._device_id:
                print("[Warning] This is my ID.")
                continue

            return f"1{device_id}300"

    @staticmethod
    def _get_msgtype_from_user() -> str:
        """
        从用户键盘输入获取要发送的消息类型。

        Returns:
            消息类型，包括下列两种：
            - `utils.constant.MessageType.TEXT`：字符串。
            - `utils.constant.MessageType.FILE`：文件。
        """
        print("Input message type:\n1::Text  2::File")
        while True:
            msgtype = input(">>> ")
            if msgtype in MessageType.LIST:
                return msgtype
            else:
                print("[Warning] Invalid message type!")

    @staticmethod
    def _get_text_from_user() -> str:
        """
        从用户键盘输入获取要发送的消息。

        Returns:
            消息字符串。
        """
        print("Input a piece of message:")
        while True:
            message = input(">>> ")
            if message != "":
                return message

    @staticmethod
    def _get_file_from_user() -> str:
        """
        从用户键盘输入获取要发送的文件名。

        Returns:
            文件的绝对路径。
        """
        print("Input file name: (i.e. foo.png)")
        while True:
            filename = input(">>> ")
            filepath = search_rsc(filename)
            if filepath != None:
                return filepath
            else:
                print(f"[Warning] {filepath} not found.")
