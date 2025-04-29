from PyQt6.QtWidgets import *
from gui import *

class Logic(QMainWindow, Ui_MainWindow):
    SUBNETS_LIST = [0, 128, 192, 224, 240, 248, 252, 254, 255]
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.my_IP_button.clicked.connect(lambda : self.get_ip())
        self.my_subnet_mask_button.clicked.connect(lambda: self.get_subnet_mask())
        self.IP_range_button.clicked.connect(lambda: self.calculate_ip_range())
        self.generate_CSV_button.clicked.connect(lambda: self.generate_ip_table())



    def get_ip(self):
        pass

    def get_subnet_mask(self):
        pass

    def validate_ip(self) -> list[str] | None:
        try:  # input validation for ip address by analyzing input as a list
            ip_address = self.IP_input.text().strip().split('.')
            if len(ip_address) != 4:#exception handles if there's not 4 octets
                raise ValueError('IP must have 4 octets')

            for octet in ip_address:#handles if any octet is not a number not a valid range
                if not octet.isdigit():
                    raise ValueError(f'Invalid octet input {octet}')
                if not (0 <= int(octet) < 256):
                    raise ValueError(f'Invalid octet range {octet}')

            if not (192 <= int(ip_address[0]) <= 223):#handles if ip is not class C
                raise ValueError(f"{'.'.join(ip_address)} not class C")

            return ip_address

        except ValueError as e:
            self.feedback_label.setText(f'IP Error: {e}')
            return None


    def validate_subnet_mask(self) -> list[str] | None:
        try:#input validation for subnet mask by analyzing input as a list
            subnet_mask = self.subnet_mask_input.text().strip().split('.')
            if len(subnet_mask) != 4:
                raise ValueError('Subnet must have 4 octets')

            for octet in subnet_mask:
                if not octet.isdigit():
                    raise ValueError(f'Invalid octet {octet}')
                if not (0 <= int(octet) < 256):
                    raise ValueError(f'Invalid octet range {octet}')

            first_three_octets = [int(n) for n in subnet_mask[0:3]]#validating first 3 octets are valid
            if first_three_octets != [255, 255, 255]:
                raise ValueError(f"{'.'.join(subnet_mask)} not class C")

            if int(subnet_mask[3]) not in self.SUBNETS_LIST:#used AI to troubleshoot a bug here
                raise ValueError(f"{'.'.join(subnet_mask)} not class C in 4th octet")

            return subnet_mask

        except ValueError as e:
            self.feedback_label.setText(f'Subnet Error: {e}')
            return None

    def calculate_ip_range(self):
        ip = self.validate_ip()
        subnet = self.validate_subnet_mask()

        if ip and subnet:#debugging
            self.feedback_label.setText(f"IP: {'.'.join(ip)}, Subnet: {'.'.join(subnet)}")


    def generate_ip_table(self) -> None:
        pass