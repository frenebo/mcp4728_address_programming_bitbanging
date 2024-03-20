import RPi.GPIO as GPIO



LDAC_1 = 15
LDAC_2 = 16
SDA = 3 #  I2C Data
SCL = 5 # I2C Clock
MCP_DEF_ADDR = 0x60


def setup_board():
    # Set up pin numbering scheme
    GPIO.setmode(GPIO.board)

    # Set up pins we are going to be using
    GPIO.setup(LDAC_1,GPIO.out)
    GPIO.setup(LDAC_2,GPIO.out)

    GPIO.setup(SDA, GPIO.out)
    GPIO.setup(SCL, GPIO.out)

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

def send_byte():
    GPIO.output(SCL)


if __name__ == "__main__":
    print(MCP_DEF_ADDR)