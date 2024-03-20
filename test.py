import RPi.GPIO as GPIO
import time


LDAC_1 = 15
LDAC_2 = 16
SDA = 11 #  I2C Data
SCL = 13 # I2C Clock
MCP_DEF_ADDR = 0x60


def setup_board():
    # Set up pin numbering scheme
    GPIO.setmode(GPIO.BOARD)

    # Set up pins we are going to be using
    GPIO.setup(LDAC_1,GPIO.OUT, initial=1)
    GPIO.setup(LDAC_2,GPIO.OUT, initial=1)

    GPIO.setup(SDA, GPIO.OUT, initial=1)
    GPIO.setup(SCL, GPIO.OUT, initial=1)

    GPIO.output(LDAC_1, GPIO.HIGH)
    GPIO.output(LDAC_2, GPIO.HIGH)
    GPIO.output(SDA, GPIO.HIGH)
    GPIO.output(SCL, GPIO.HIGH)


# Start: high-to-low transition on SDA while SCL is high
def do_start_condition():
    if GPIO.input(SDA) != 1:
        # SCL must be high when SDA goes low - otherwise this is a stop condition
        GPIO.output(SCL, GPIO.LOW)
        GPIO.output(SDA, GPIO.HIGH)

    # A high-to-low transition for SDA while SCL is HIGH indicates start condition
    GPIO.output(SCL, GPIO.HIGH)
    GPIO.output(SDA, GPIO.LOW)

    # Pull SCL low, so ready to send clock pulses
    GPIO.output(SCL, GPIO.LOW)

def do_stop_condition():
    # SDA should be low if not already low
    if GPIO.input(SDA) != 1:
        # Bring clock down first just in case
        GPIO.output(SCL, GPIO.LOW)
        GPIO.output(SDA, GPIO.LOW)

    # A low-to-high transition for SDA while SCL is HIGH indicates stop condition
    GPIO.output(SCL, GPIO.HIGH)
    GPIO.output(SDA, GPIO.HIGH)

def num_to_byte_str(val):
    return '{0:b}'.format(val).zfill(8)

def send_byte(
    byte_str,
    set_ldac1_before_ack=None,
    set_ldac2_before_ack=None,
    ):
    if len(byte_str) != 8:
        raise Exception("Byte string should contain 8 characters")
    # if val > 0xFF or val < 0 or int(val) != val:
    #     raise Exception("Invalid byte ''".format(val))
    
    # Take control of SDA
    GPIO.setup(SDA, GPIO.OUT)

    # Set SCL and SDA low to start out
    # GPIO.output(SCL, GPIO.LOW)
    GPIO.output(SDA, GPIO.LOW)
    dat_high = False

    for digit in byte_str:
        if digit == "1":
            if not dat_high:
                dat_high = True
                GPIO.output(SDA, GPIO.HIGH)
            else:
                # Don't need to change data bit
                pass
        elif digit == "0":
            if dat_high:
                dat_high = False
                GPIO.output(SDA, GPIO.LOW)
            else:
                # Don't need to change data bit
                pass
        else:
            raise Exception("Invalid binary digit '{}'".format(digit))
        GPIO.output(SCL, GPIO.HIGH)
        GPIO.output(SCL, GPIO.LOW)
    
    # GPIO
    # Release SDA
    GPIO.setup(SDA, GPIO.IN)

    if set_ldac1_before_ack is not None:
        if set_ldac1_before_ack != GPIO.HIGH and set_ldac1_before_ack != GPIO.LOW:
            raise Exception("Must provide GPIO HIGH/LOW ldac bit")
        GPIO.output(LDAC_1, set_ldac1_before_ack)
    if set_ldac2_before_ack is not None:
        if set_ldac2_before_ack != GPIO.HIGH and set_ldac2_before_ack != GPIO.LOW:
            raise Exception("Must provide GPIO HIGH/LOW ldac bit")
        GPIO.output(LDAC_2, set_ldac2_before_ack)
    
    # time.sleep(10/2000000)
    # Check acknowledge
    GPIO.output(SCL, GPIO.HIGH)
    ackbit_high = GPIO.input(SDA)
    GPIO.output(SCL, GPIO.LOW)

    # Low bit indicates acknowledgement
    return not ackbit_high

def do_general_reset():
    do_start_condition()
    general_call_command = '00000000'
    if not send_byte(general_call_command):
        raise Exception("Failed")
    
    general_call_reset_byte = '00000110'
    if not send_byte(general_call_reset_byte):
        raise Exception("Failed")

    do_stop_condition()


# def do_restart()
def read_byte_from_slave():
    GPIO.setup(SDA, GPIO.IN)
    result = []
    for i in range(8):
        GPIO.output(SCL, GPIO.HIGH)
        bit = GPIO.input(SDA)
        GPIO.output(SCL, GPIO.LOW)
        result.append(bit)
    
    # Acknowledge
    GPIO.setup(SDA, GPIO.OUT)
    GPIO.output(SDA, GPIO.HIGH)
    GPIO.output(SCL, GPIO.HIGH)
    GPIO.output(SCL, GPIO.LOW)

    return result

def do_write_ldac1_address_bits():
    do_start_condition()

    # Factory default address bits
    current_address_bits = '000'

    # New bits!
    new_address_bits = '001'

    first_byte = '1100' + current_address_bits + '0'

    if not send_byte(first_byte):
        raise Exception("first byte failed")

    second_byte = '011' + current_address_bits + '01'

    if not send_byte(second_byte, set_ldac1_before_ack=GPIO.LOW):
        raise Exception("Second byte failed")
    
    third_byte = '011' + new_address_bits + '10'
    if not send_byte(third_byte):
        raise Exception("third byte failed")
    
    third_byte = '011' + new_address_bits + '11'
    # Fourth byte is for confirmation
    if not send_byte(third_byte):
        raise Exception("Fourth byte (confirmation) failed")
    

    do_stop_condition()
    GPIO.output(LDAC_1, GPIO.HIGH)

def do_call_read_ldac1_address_bits():
    do_start_condition()
    general_call_command = '00000000'
    if not send_byte(general_call_command):
        raise Exception("Failed")
    
    gnl_read_second_byte = '00001100'
    if not send_byte(gnl_read_second_byte, set_ldac1_before_ack=GPIO.LOW):
        raise Exception("Failed")
    
    # Restart bit
    do_start_condition()

    gnl_read_third_byte = '11000001'
    if not send_byte(gnl_read_third_byte):
        raise Exception("Failed acknowledge third byte")
    
    # read_byte_from_slave()
    address_data = read_byte_from_slave()
    # print(address_data)
    do_stop_condition()

    GPIO.output(LDAC_1, GPIO.HIGH)

    return address_data

def main():
    setup_board()
    # print(MCP_DEF_ADDR)
    # Binary address as string
    # bin_addr_str = '{0:b}'.format(MCP_DEF_ADDR).zfill(8)
    # print(bin_addr_str)
    mcp_7bit_address = '{0:b}'.format(MCP_DEF_ADDR).zfill(7)
    # add a R/W 0 bit (read)
    read_mcp_byte = mcp_7bit_address + "0"



    # do_general_reset()

    # addr_data = do_call_read_ldac1_address_bits()

    # print(addr_data)

    do_write_ldac1_address_bits()



if __name__ == "__main__":
    try:
        main()
    except:
        GPIO.cleanup()
        raise
    GPIO.cleanup()