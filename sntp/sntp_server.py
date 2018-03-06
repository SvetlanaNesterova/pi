import logging
import traceback
import sys
from datetime import datetime
from socket import socket, AF_INET, SOCK_DGRAM

LOG = logging.getLogger("sntp.sntp_server")
START_DATE = datetime(1900, 1, 1)


class SNTPServer:
    def __init__(self):
        shift = self.read_config_shift_time_sec()
        self.shift = 0 if shift is None else shift

    def read_config_shift_time_sec(self):
        try:
            with open("server_shift_config.txt") as file:
                time = int(file.readline())
                return time
        except Exception as e:
            LOG.warning(traceback.format_exc())
            print("\tFailed to read shift time from config-file.\n"
                  "\tError: \"%s\" \n"
                  "\tShift time was set up to 0." % e)

    def start(self):
        try:
            with socket(AF_INET, SOCK_DGRAM) as _socket:
                try:
                    _socket.bind(("", 123))
                except OSError:
                    LOG.error(traceback.format_exc())
                    print("Failed to bind port 123.")
                    sys.exit(1)

                while True:
                    message, client_address = _socket.recvfrom(1024)
                    #print(message)
                    response = self.get_response_for_request(
                        message, datetime.now())
                    print(response)
                    print(len(response))
                    if isinstance(response, str):
                        LOG.info("Strange request from %s, error: %s \n"
                                 "%s" % (client_address, response, message))
                    else:
                        _socket.sendto(response, client_address)

        except Exception:
            LOG.error(traceback.format_exc())
            print("Unexpected error was happend. Sorry... :(( See Details in logs.")
            sys.exit(1)

    def get_response_for_request(self, request_message: bytes,
                                 recv_time: datetime):
        if len(request_message) < 48:
            return "Too short message"
        client_transmit_timestamp = request_message[40:48]
        version = request_message[0] >> 3 & 0b00000111
        mode = request_message[0] & 0b00000111
        if mode != 3:
            return "Wrong mode"
        return self.create_response_message(
            version, client_transmit_timestamp, recv_time)

    def create_response_message(self, ver: int, client_trans_time: bytes,
                                recv_time: datetime):
        correction_id = 0b11 # 3 - no correction
        version_number = int(bin(ver), 2)  # from_request or 4 - current version?
        mode = 0b100  # 4 - server
        first = (correction_id << 6) + (version_number << 3)+ mode
        first_byte = int_to_bytes(first, 1)
        stratum = int_to_bytes(2, 1)  # should be 0?
        poll_interval = int_to_bytes(4, 1)
        precision = int_to_bytes(-6, 1)  # ?
        root_delay = int_to_bytes(0, 4)  # ?
        root_dispersion = int_to_bytes(0, 4)  # ?
        reference_identifier = b"LOCL"
        reference_timestamp = int_to_bytes(0, 8)
        originate_timestamp = client_trans_time
        receive_timestamp = pairtime_to_bytes(dt_to_pairtime(recv_time))
        cur_time = self.shift_pairtime(dt_to_pairtime(datetime.now()))
        transmit_timestamp = pairtime_to_bytes(cur_time)

        return first_byte + stratum + poll_interval + precision + \
               root_delay + root_dispersion + reference_identifier + \
               reference_timestamp + originate_timestamp + \
               receive_timestamp + transmit_timestamp

    def shift_pairtime(self, time: tuple):
        return time[0] + self.shift, time[1]


def dt_to_pairtime(dt: datetime):
    delta = (dt - START_DATE).total_seconds()
    int_seconds = int(delta)
    fraction_seconds = int((delta - int_seconds) * (2 ** 32))
    return (int_seconds, fraction_seconds)


def pairtime_to_bytes(pt: tuple):
        return int_to_bytes(pt[0], 4) + int_to_bytes(pt[1], 4)


def int_to_bytes(number: int, length: int):
    signed = number < 0
    return int.to_bytes(number, length=length,
                        byteorder="big", signed=signed)
