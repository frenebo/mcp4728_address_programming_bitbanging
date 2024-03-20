import RPi.GPIO as GPIO



LDAC_1 = 15
LDAC_2 = 16
SDA = 3 #  I2C Data
SCL = 5 # I2C Clock
MCP_DEF_ADDR = 0x60


def setup_board():
    # Set up pin numbering scheme
    GPIO.setmode(GPIO.BOARD)

    # Set up pins we are going to be using
    GPIO.setup(LDAC_1,GPIO.OUT)
    GPIO.setup(LDAC_2,GPIO.OUT)

    GPIO.setup(SDA, GPIO.OUT)
    GPIO.setup(SCL, GPIO.OUT)

    GPIO.output(LDAC_1, GPIO.HIGH)
    GPIO.output(LDAC_2, GPIO.HIGH)
    GPIO.output(SDA, GPIO.HIGH)
    GPIO.output(SCL, GPIO.HIGH)


# Start: high-to-low transition on SDA while SCL is high
def do_start_condition():
    GPIO.output(SCL, GPIO.HIGH)
    GPIO.output(SDA, GPIO.LOW)

    # Pull SCL low, so ready for first bit
    GPIO.output(SCL, GPIO.LOW)

def num_to_byte_str(val):
    return '{0:b}'.format(val).zfill(8)

def send_byte(byte_str):
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
        else:
            if dat_high:
                dat_high = False
                GPIO.output(SDA, GPIO.LOW)
            else:
                # Don't need to change data bit
                pass
        GPIO.output(SCL, GPIO.HIGH)
        GPIO.output(SCL, GPIO.LOW)
    
    # Release SDA
    GPIO.setup(SDA, GPIO.OUT)

    # Check acknowledge
    GPIO.output(SCL, GPIO.HIGH)
    ackbit_high = GPIO.input(SDA)
    GPIO.output(SCL, GPIO.LOW)

    # Low bit indicates acknowledgement
    return not ackbit_high


def main():
    setup_board()
    # print(MCP_DEF_ADDR)
    # Binary address as string
    # bin_addr_str = '{0:b}'.format(MCP_DEF_ADDR).zfill(8)
    # print(bin_addr_str)
    mcp_7bit_address = '{0:b}'.format(MCP_DEF_ADDR).zfill(7)
    # add a R/W 0 bit (read)
    read_mcp_byte = mcp_7bit_address + "0"


    do_start_condition()
    general_call_command = '00000000'
    if not send_byte(general_call_command):
        raise Exception("Failed")
    
    general_call_reset_byte = '00000110'
    if not send_byte(general_call_reset_byte):
        raise Exception("Failed")


if __name__ == "__main__":
    try:
        main()
    except:
        GPIO.cleanup()
        raise
    GPIO.cleanup()