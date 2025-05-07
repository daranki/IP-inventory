from PyQt6.QtWidgets import *
from gui import *
import subprocess
import re
import ipaddress
import csv
from datetime import datetime


class Logic(QMainWindow, Ui_MainWindow):
    IP_RANGE = []
    NETWORK_ID = None
    BROADCAST_ADDRESS = None
    SUBNETS_LIST = [0, 128, 192, 224, 240, 248, 252, 254, 255]
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.my_IP_button.clicked.connect(lambda : self.get_ip())
        self.my_subnet_mask_button.clicked.connect(lambda: self.get_subnet_mask())
        self.IP_range_button.clicked.connect(lambda: self.calculate_ip_range())
        self.generate_CSV_button.clicked.connect(lambda: self.generate_ip_table())
        self.subnet_mask_input.textChanged.connect(self.clear_ip_range_display)#found this method in google
        self.IP_input.textChanged.connect(self.clear_ip_range_display)



    def get_ip(self) -> None:#had ai assist with lines 27 to 31
        """
        Method that uses the subprocess and regex libraries to populate the ip address
        of the user's computer to the IP address text entry box with the "My IP" button
        :return:
        """
        result = subprocess.run(['ipconfig'], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        for i, line in enumerate(lines):
            if 'IPv4' in line:
                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)#regex matching each octet 1 or more digits
                if ip_match:
                    ip = ip_match.group(1)
                    self.IP_input.setText(ip)
                else:
                    self.feedback_label.setStyleSheet("color: red;")
                    self.feedback_label.setText('Could not find IP address')
                    return


    def get_subnet_mask(self) ->  None:#had ai assist with lines 46 to 50
        """
        Method that uses the subprocess and regex libraries to populate the subnet mask
        of the user's computer to the subnet mask text entry box with the "My subnet" button
        :return:
        """
        result = subprocess.run(['ipconfig'], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        for i, line in enumerate(lines):
            if 'Subnet Mask' in line:
                mask_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                if mask_match:
                    subnet = mask_match.group(1)
                    self.subnet_mask_input.setText(subnet)
                else:
                    self.feedback_label.setStyleSheet("color: red;")
                    self.feedback_label.setText('Could not find subnet mask')
                    return

    def validate_ip(self) -> list[str] | None:
        """
        function to validate the input in the IP address text entry box
        returns the ip address as a list containing strings of each octet
        :return: list[str]
        """
        try:  # input validation for ip address by analyzing input as a list
            ip_address = self.IP_input.text().strip().split('.')
            if len(ip_address) != 4:#exception handles if there's not 4 octets
                self.feedback_label.setStyleSheet("color: red;")
                raise ValueError('IP must have 4 octets')

            for octet in ip_address:#handles if any octet is not a number not a valid range
                if not octet.isdigit():
                    self.feedback_label.setStyleSheet("color: red;")
                    raise ValueError(f'Invalid octet input {octet}')
                if not (0 <= int(octet) < 256):
                    self.feedback_label.setStyleSheet("color: red;")
                    raise ValueError(f'Invalid octet range {octet}')

            if not (192 <= int(ip_address[0]) <= 223):#handles if ip is not class C
                self.feedback_label.setStyleSheet("color: red;")
                raise ValueError(f"{'.'.join(ip_address)} not class C")

            return ip_address

        except ValueError as e:
            self.feedback_label.setStyleSheet("color: red;")
            self.feedback_label.setText(f'IP Error: {e}')
            self.clear_ip_range_display()
            return None


    def validate_subnet_mask(self) -> list[str] | None:
        """
        function to validate the input in the subnet mask text entry box
        returns the subnet mask as a list containing strings of each octet
        :return: list[str]
        """
        try:#input validation for subnet mask by analyzing input as a list
            subnet_mask = self.subnet_mask_input.text().strip().split('.')
            if len(subnet_mask) != 4:
                self.feedback_label.setStyleSheet("color: red;")
                raise ValueError('Subnet must have 4 octets')

            for octet in subnet_mask:
                if not octet.isdigit():
                    self.feedback_label.setStyleSheet("color: red;")
                    raise ValueError(f'Invalid octet {octet}')
                if not (0 <= int(octet) < 256):
                    self.feedback_label.setStyleSheet("color: red;")
                    raise ValueError(f'Invalid octet range {octet}')

            first_three_octets = [int(n) for n in subnet_mask[0:3]]#validating first 3 octets are valid
            if first_three_octets != [255, 255, 255]:
                self.feedback_label.setStyleSheet("color: red;")
                raise ValueError(f"{'.'.join(subnet_mask)} not class C")

            if int(subnet_mask[3]) not in self.SUBNETS_LIST:#used AI to troubleshoot a bug here
                self.feedback_label.setStyleSheet("color: red;")
                raise ValueError(f"{'.'.join(subnet_mask)} not class C in 4th octet")

            return subnet_mask

        except ValueError as e:
            self.feedback_label.setStyleSheet("color: red;")
            self.feedback_label.setText(f'Subnet Error: {e}')
            self.clear_ip_range_display()
            return None

    def calculate_ip_range(self) -> list[str] | None:
        """
        method that takes the validated IP address and subnet mask
        then calculates and displays the IP range and available hosts
        then stores the IP range in the IP_RANGE list
        :return: list[str]
        """
        ip = self.validate_ip()
        subnet = self.validate_subnet_mask()

        if not ip or not subnet:
            return None

        try:
            ip_str = ".".join(ip)
            subnet_str = ".".join(subnet)
            network = ipaddress.IPv4Network(f"{ip_str}/{subnet_str}", strict=False)

            self.IP_RANGE = [str(ip) for ip in network]
            self.NETWORK_ID = str(network.network_address)
            self.BROADCAST_ADDRESS = str(network.broadcast_address)

            host_count = len(self.IP_RANGE) - 2

            if host_count > 2:
                self.IP_range_output.setText(f"{self.IP_RANGE[0]} - {self.IP_RANGE[-1]}")
                self.available_hosts_label.setText(f"Available hosts: {host_count}")
                self.feedback_label.setStyleSheet("color: green;")
                self.feedback_label.setText("IP range successfully calculated.")
            else:
                self.IP_range_output.setText(f"{self.IP_RANGE[0]} - {self.IP_RANGE[-1]}")
                self.available_hosts_label.setText("Available hosts: 0")
                self.feedback_label.setText("No usable hosts: subnet too small")
                self.IP_RANGE = []

            return self.IP_RANGE

        except Exception as e:
            self.feedback_label.setStyleSheet("color: red;")
            self.feedback_label.setText(f"Range Error: {e}")
            return None


    def generate_ip_table(self) -> None:
        """
        method that takes the IP_RANGE list and creates a CSV file
        that populates the available host IP addresses
        file name based on the date/time group for data keeping or clerical needs
        :return:
        """

        ip_list = self.validate_ip()
        if not ip_list:
            self.feedback_label.setStyleSheet("color: red;")
            self.feedback_label.setText("Enter a Valid IP address")
            return

        if not self.IP_RANGE:
            self.feedback_label.setStyleSheet("color: red;")
            self.feedback_label.setText("must calculate IP range first")
            return

        device_ip = ".".join(ip_list)

        timestamp = datetime.now().strftime("%d %b %y %H-%M-%S")#googled how to use this library
        filename = f"IP Inventory date-{timestamp}.csv"

        try:
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["IP Addresses",timestamp])
                for ip in self.IP_RANGE:
                    if ip == self.NETWORK_ID:
                        label = "Network ID"
                    elif ip == self.BROADCAST_ADDRESS:
                        label = "Broadcast Address"
                    elif ip == device_ip:
                        label = "Your computer"
                    else:
                        label = ""
                    writer.writerow([ip, label])

            self.feedback_label.setStyleSheet("color: green;")
            self.feedback_label.setText(f"CSV file created")

        except Exception as e:
            self.feedback_label.setStyleSheet("color: red;")
            self.feedback_label.setText(f"CSV Error: {e}")

    def clear_ip_range_display(self) -> None:
        """
        method for clearing the IP range for a cleaner UI
        also helps for reducing invalid inputs from users
        :return:
        """
        self.IP_range_output.setText("")
        self.available_hosts_label.setText("")
        self.IP_RANGE = []