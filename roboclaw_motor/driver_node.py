from serial import Serial
import time
from roboclaw_motor.roboclaw_3 import Roboclaw

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray, String
from std_srvs.srv import SetBool

class RoboclawDriver(Node):
    def __init__(self):
        super().__init__('roboclaw_motor_driver_node')

        self.get_params()

        self.setup_interface()

        self.setup_ros()

    def get_params(self):
        """
        This function is used for param loading
        """        

        # Declare parameters with default values
        self.declare_parameter('control_device', '/dev/ttyUSB0')
        self.declare_parameter('control_baudrate', 115200)        

        self.declare_parameter('read_device', '/dev/ttyACM0')
        self.declare_parameter('read_baudrate', 115200)                

        # Retrieve parameters
        self.serial_port_control = self.get_parameter('control_device').get_parameter_value().string_value
        self.serial_baudrate_control = self.get_parameter('control_baudrate').get_parameter_value().integer_value

        self.serial_port_read = self.get_parameter('read_device').get_parameter_value().string_value
        self.serial_baudrate_read = self.get_parameter('read_baudrate').get_parameter_value().integer_value

        # Gloabl flags
        self.flag_send_down = False
        self.flag_send_up = False
        self.flag_send_stop = False

    def setup_interface(self):
        """
        This function is used to setup serial devices
        """

        # This is the serial used for controlling motor speed
        # It use "Simple Serial" protocol 
        self.control_serial = Serial(self.serial_port_control, self.serial_baudrate_control, timeout=1)        
        time.sleep(1)

        # This is the serial used for read info from motor
        # It use "Packet Serial" protocol
        # NOTE: "Packet Serial" ideally can send motor speed, somehow it not works right now
        self.read_serial = Roboclaw(self.serial_port_read, self.serial_baudrate_read)
        self.read_serial.Open()        
        time.sleep(1)

    def setup_ros(self):
        """
        This function is used for ros setup: publisher, subscribers, 
        service, timer and more
        """

        # Publishers
        self.current_pub = self.create_publisher(Float64MultiArray, 'roboclaw/current', 10)
        self.version_pub = self.create_publisher(String, 'roboclaw/version', 10)

        # Timer: calls timer every 0.1 seconds (10 Hz)
        self.timer = self.create_timer(0.1, self.process)

        # Services
        self.srv_down = self.create_service(SetBool, 'roboclaw/going_down', self.going_down_srv)
        self.srv_up = self.create_service(SetBool, 'roboclaw/going_up', self.going_up_srv)
        self.srv_stop = self.create_service(SetBool, 'roboclaw/stop', self.stop_srv)

    def going_down_srv(self, request, response):
        if request.data:
            response.success = True
            response.message = "Enable Going Down Now."

            self.flag_send_down = True
        else:
            response.success = False
            response.message = "Enable Going Down Failed."

        return response 

    def going_up_srv(self, request, response):
        if request.data:
            response.success = True
            response.message = "Enable Going Up Now."

            self.flag_send_up = True
        else:
            response.success = False
            response.message = "Enable Going Up Failed."

        return response
    
    def stop_srv(self, request, response):
        if request.data:
            response.success = True
            response.message = "Enable Stop Now."

            self.flag_send_stop = True
        else:
            response.success = False
            response.message = "Enable Stop Failed."

        return response    
            
    def process(self):
        """
        This function is used to process: 1) read info; 2) send motor cmd
        """        
        # =================================================================== #
        # Send cmd
        # =================================================================== #
        if self.flag_send_down:
            self.flag_send_down = False

            self.get_logger().info(
                f"{self.get_name()}: motor going down (Ch1 half speed reverse)")
                        
            # NOTE: for velocity cmd: 
            #   check the roboclaw_user_manual.pdf: Standard Serial Command Syntax
            self.control_serial.write(bytes([32]))

        if self.flag_send_up:
            self.flag_send_up = False

            self.get_logger().info(
                f"{self.get_name()}: motor going up (Ch1 half speed forward)")
                        
            # NOTE: for velocity cmd: 
            #   check the roboclaw_user_manual.pdf: Standard Serial Command Syntax
            self.control_serial.write(bytes([94]))

        if self.flag_send_stop:
            self.flag_send_stop = False

            self.get_logger().info(
                f"{self.get_name()}: motor stop (Ch1 stop)")
                        
            # NOTE: for velocity cmd: 
            #   check the roboclaw_user_manual.pdf: Standard Serial Command Syntax
            self.control_serial.write(bytes([64]))

        # =================================================================== #
        # Read version
        # =================================================================== #
        version = self.read_serial.ReadVersion(0x80)

        if version[0]==False:
            self.get_logger().error(
                f"{self.get_name()}: Get Version Failed")
        else:
            if self.version_pub.get_subscription_count() > 0:
                msg = String()
                msg.data = repr(version[1])
                self.version_pub.publish(msg)            
                  
        # =================================================================== #
        # Read current
        # =================================================================== #
        current = self.read_serial.ReadCurrents(0x80)

        if current[0] == False:
            self.get_logger().error(
                f"{self.get_name()}: Get Current Failed")  
        else:
            if self.current_pub.get_subscription_count() > 0:
                # format: [voltage, current]
                # follow the power_monitor standard
                msg = Float64MultiArray()
                msg.data = [0.0, current[1]/100.0]
                self.current_pub.publish(msg) 

    def close(self):
        """
        This function is used to read info from motor
        """  

        # close control serial
        if self.control_serial.is_open:
            self.control_serial.close()        

        # close read serial
        self.read_serial.Close()

def main(args=None):
    rclpy.init(args=args)

    try:
        node = RoboclawDriver()  # your node class, subclass of rclpy.node.Node
        node.get_logger().info(f"{node.get_name()}: Start node ...")

        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    # Cleanup on shutdown
    node.close()  # your cleanup method

    node.get_logger().info(f"{node.get_name()}: Everything is shutdown now!")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()                  