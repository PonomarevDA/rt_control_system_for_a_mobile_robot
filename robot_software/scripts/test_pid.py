#!/usr/bin/env python
# coding: utf8
""" This script starts pid test and/or create plots for result."""
import json
import os
import matplotlib.pyplot as plt
import rospy
import argparse
from std_msgs.msg import Float32, Int32
from geometry_msgs.msg import Twist, Vector3, Point32

# Choose mode
# 1. Test mode
PLOT_ONLY = bool()
# 1.1. Plot only params
JSON_FILE_NAME = str()
# 1.2. Gathering type
ENABLE_TEST = True
# 1.2.1. Real gathering params
DATA_GATHERING_TIME = 30
# 1.2.2. Test gathering params
TIME_BEFORE_SPEED_CHANGE = float(2)
DESIRED_LINEAR_SPEEDS = [+0.15, -0.15, +0.00, +0.00, +0.00, +0.00]
DESIRED_ANGULAR_SPEEDS = [0.00, -0.00, +0.00, +0.50, -0.50, +0.00]
DESIRED_SPEED_LENGTH = len(DESIRED_LINEAR_SPEEDS)
# 2. Other settings
REAL_TIME_PLOTTING = False
LANGUAGE = 'rus'


# Constants
THIS_NODE_NAME = 'test_pid_node'
FILE_NAME_BASE = "test_pid_result_"
FILE_NAME_END = ".json"

class TopicName:
    CMD = "/cmd_vel"
    SPEED = "/speedTopic"
    ENCODER_LEFT_SPEED = "/encoderLeftSpeedTopic"
    ENCODER_RIGHT_SPEED = "/encoderRightSpeedTopic"
    LEFT_MOTOR = "/motorLeftTopic"
    RIGHT_MOTOR = "/motorRightTopic"
    POSITION = "/positionTopic"

class Json:
    LINEAR_SPEED = "linear speed"
    LEFT_ENCODER_SPEED = "left encoder speed"
    LEFT_MOTOR_SPEED = "left motor pwm"
    ANGULAR_SPEED = "angular speed"
    RIGHT_ENCODER_SPEED = "right encoder speed"
    RIGHT_MOTOR_SPEED = "right motor pwm"
    POSITION_X = "position x"
    POSITION_Y = "position y"
    POSITION_DIR = "position dir"

    ALL = [LINEAR_SPEED,  LEFT_ENCODER_SPEED,  LEFT_MOTOR_SPEED,
           ANGULAR_SPEED, RIGHT_ENCODER_SPEED, RIGHT_MOTOR_SPEED,
           POSITION_X,    POSITION_Y,          POSITION_DIR]

    DATA = "data"
    TIME = "time"

PLOT_TITLE = dict()
PLOT_LABEL = dict()
PLOT_TIME = str()
for obj_name in Json.ALL:
    PLOT_TITLE[obj_name] = str()
    PLOT_LABEL[obj_name] = str()
if LANGUAGE is 'rus':
    PLOT_TIME = u'время, сек'

    PLOT_LABEL[Json.LINEAR_SPEED] = u'скорость'
    PLOT_LABEL[Json.ANGULAR_SPEED] = u'скорость, рад/с'
    PLOT_LABEL[Json.LEFT_ENCODER_SPEED] = u'скорость, имп./сек'
    PLOT_LABEL[Json.RIGHT_ENCODER_SPEED] = u'скорость, имп./сек'
    PLOT_LABEL[Json.LEFT_MOTOR_SPEED] = u'скважность ШИМ, %'
    PLOT_LABEL[Json.RIGHT_MOTOR_SPEED] = u'скажность ШИМ, %'
    PLOT_LABEL[Json.POSITION_X] = u'положение, м'
    PLOT_LABEL[Json.POSITION_Y] = u'положение, м'
    PLOT_LABEL[Json.POSITION_DIR] = u'направление, рад'

    PLOT_TITLE[Json.LINEAR_SPEED] = u'линейная скорость'
    PLOT_TITLE[Json.ANGULAR_SPEED] = u'угловая скорость'
    PLOT_TITLE[Json.LEFT_ENCODER_SPEED] = u'левый энкодер'
    PLOT_TITLE[Json.RIGHT_ENCODER_SPEED] = u'правый энкодер'
    PLOT_TITLE[Json.LEFT_MOTOR_SPEED] = u'левый двигатель'
    PLOT_TITLE[Json.RIGHT_MOTOR_SPEED] = u'правый двигатель'
    PLOT_TITLE[Json.POSITION_X] = u'положение робота'
    PLOT_TITLE[Json.POSITION_Y] = u'положение робота'
    PLOT_TITLE[Json.POSITION_DIR] = u'направление робота'
elif LANGUAGE is 'eng':
    PLOT_TIME = 'time, sec'

    PLOT_LABEL[Json.LINEAR_SPEED] = 'speed, m/s'
    PLOT_LABEL[Json.ANGULAR_SPEED] = 'speed, rad/sec'
    PLOT_LABEL[Json.LEFT_ENCODER_SPEED] = 'speed, imp./sec'
    PLOT_LABEL[Json.RIGHT_ENCODER_SPEED] = 'speed, imp./sec'
    PLOT_LABEL[Json.LEFT_MOTOR_SPEED] = 'duty cycle, %'
    PLOT_LABEL[Json.RIGHT_MOTOR_SPEED] = 'duty cycle, %'
    PLOT_LABEL[Json.POSITION_X] = 'position, m'
    PLOT_LABEL[Json.POSITION_Y] = 'position, m'
    PLOT_LABEL[Json.POSITION_DIR] = 'direction, rad'

    PLOT_TITLE[Json.LINEAR_SPEED] = 'linear speed'
    PLOT_TITLE[Json.ANGULAR_SPEED] = 'angular speed'
    PLOT_TITLE[Json.LEFT_ENCODER_SPEED] = 'left encoder'
    PLOT_TITLE[Json.RIGHT_ENCODER_SPEED] = 'right encoder'
    PLOT_TITLE[Json.LEFT_MOTOR_SPEED] = 'left motor'
    PLOT_TITLE[Json.RIGHT_MOTOR_SPEED] = 'right motor'
    PLOT_TITLE[Json.POSITION_X] = 'robot position x'
    PLOT_TITLE[Json.POSITION_Y] = 'robot position y'
    PLOT_TITLE[Json.POSITION_DIR] = 'robot direction'


rospy.init_node(THIS_NODE_NAME)


class Topic(object):
    def __init__(self, topic, data_type):
        self.TOPIC = topic
        self.time = list()
        self.sub = rospy.Subscriber(self.TOPIC, data_type, self.handle)
        self.__start_time = rospy.get_rostime()
    def append_relative_time(self):
        current_time = rospy.get_rostime()
        relative_secs = current_time.secs - self.__start_time.secs
        relative_n_secs = current_time.nsecs - self.__start_time.nsecs
        relative_time = relative_secs + float(relative_n_secs)/1000000000
        self.time.append(relative_time)
    def off(self):
        self.sub.unregister()
    def handle(self, msg):
        pass

class Speed(Topic):
    def __init__(self, topic):
        super(Speed, self).__init__(topic, Twist)
        self.linear = list()
        self.angular = list()
    def handle(self, msg):
        self.append_relative_time()
        print("received: {0}, {1}, {2}".format(self.TOPIC, self.time[-1], msg.linear.x))
        print("received: {0}, {1}, {2}".format(self.TOPIC, self.time[-1], msg.angular.z))
        self.linear.append(msg.linear.x)
        self.angular.append(msg.angular.z)

class EncoderSpeed(Topic):
    def __init__(self, topic):
        super(EncoderSpeed, self).__init__(topic, Float32)
        self.data = list()
    def handle(self, msg):
        self.append_relative_time()
        print("received: {0}, {1}, {2}".format(self.TOPIC, self.time[-1], msg.data))
        self.data.append(msg.data)

class MotorSpeed(Topic):
    def __init__(self, topic):
        super(MotorSpeed, self).__init__(topic, Int32)
        self.data = list()
    def handle(self, msg):
        self.append_relative_time()
        print("received: {0}, {1}, {2}".format(self.TOPIC, self.time[-1], msg.data))
        self.data.append(msg.data)

class Position(Topic):
    def __init__(self, topic):
        super(Position, self).__init__(topic, Point32)
        self.x = list()
        self.y = list()
        self.z = list()
    def handle(self, msg):
        self.append_relative_time()
        print("received: {0}, {1}, {2}, {3}, {4}".format(self.TOPIC, self.time[-1],
                                                         msg.x, msg.y, msg.z))
        self.x.append(msg.x)
        self.y.append(msg.y)
        self.z.append(msg.z)


class Test():
    def __init__(self):
        self.topics = dict()
        self.file_name = str()
    def do(self, mode):
        if PLOT_ONLY is True:
            self.read_data_and_create_plot(JSON_FILE_NAME)
        else:
            self.set_mode_and_show_info(mode)
            self.gather_data()
            self.write_data_to_file()
            self.read_data_and_create_plot()
        if ENABLE_TEST is True:
            Test.create_desired_plot()
        plt.show()

    def set_mode_and_show_info(self, mode):
        print("Node have started. The settings are:")
        if PLOT_ONLY is True:
            print("- script mode: only create plot.")
        else:
            print("- script mode: data gathering and create plot;")
            if ENABLE_TEST is True:
                print("-- data gathering type: test enabled;")
                print("--- desired linear speed: " + str(DESIRED_LINEAR_SPEEDS))
                print("--- desired angular speed: " + str(DESIRED_ANGULAR_SPEEDS))
                print("--- speed change interval: " + str(TIME_BEFORE_SPEED_CHANGE))
            else:
                print("-- data gathering type: real data gathering;")
                print("--- time interval: " + str(DATA_GATHERING_TIME))
            print("Sleep for short time...")
    def gather_data(self):
        # Preparation
        cmd = rospy.Publisher(TopicName.CMD, Twist, queue_size=10)
        rospy.sleep(0.1)
        msg = Twist(Vector3(0, 0, 0), Vector3(0, 0, 0))
        cmd.publish(msg)
        rate = rospy.Rate(1 / TIME_BEFORE_SPEED_CHANGE)
        rate.sleep()
        # Gather data
        print("Data is gathering now...")
        self.topics = dict()
        self.topics[TopicName.SPEED] = Speed(TopicName.SPEED)
        self.topics[TopicName.ENCODER_LEFT_SPEED] = EncoderSpeed(TopicName.ENCODER_LEFT_SPEED)
        self.topics[TopicName.ENCODER_RIGHT_SPEED] = EncoderSpeed(TopicName.ENCODER_RIGHT_SPEED)
        self.topics[TopicName.LEFT_MOTOR] = MotorSpeed(TopicName.LEFT_MOTOR)
        self.topics[TopicName.RIGHT_MOTOR] = MotorSpeed(TopicName.RIGHT_MOTOR)
        self.topics[TopicName.POSITION] = Position(TopicName.POSITION)
        if ENABLE_TEST is True:
            for i in range(0, len(DESIRED_LINEAR_SPEEDS)):
                msg.linear.x = DESIRED_LINEAR_SPEEDS[i]
                msg.angular.z = DESIRED_ANGULAR_SPEEDS[i]
                cmd.publish(msg)
                print("\ncommand:\n" + str(msg))
                rate.sleep()
        else:
            rospy.sleep(DATA_GATHERING_TIME)
        # Off subscribers
        for key in self.topics:
            self.topics[key].off()

    def write_data_to_file(self):
        counter = 0
        calculate_name = lambda i: FILE_NAME_BASE + str(i) + FILE_NAME_END
        while os.path.isfile(calculate_name(counter)) is not False:
            counter += 1
        self.file_name = calculate_name(counter)

        write_file = open(self.file_name, "w")
        new_dump = dict()

        data = dict([(Json.DATA, self.topics[TopicName.SPEED].linear),
                     (Json.TIME, self.topics[TopicName.SPEED].time)])
        new_dump[Json.LINEAR_SPEED] = data

        data = dict([(Json.DATA, self.topics[TopicName.ENCODER_LEFT_SPEED].data),
                     (Json.TIME, self.topics[TopicName.ENCODER_LEFT_SPEED].time)])
        new_dump[Json.LEFT_ENCODER_SPEED] = data

        data = dict([(Json.DATA, self.topics[TopicName.LEFT_MOTOR].data),
                     (Json.TIME, self.topics[TopicName.LEFT_MOTOR].time)])
        new_dump[Json.LEFT_MOTOR_SPEED] = data

        data = dict([(Json.DATA, self.topics[TopicName.SPEED].angular),
                     (Json.TIME, self.topics[TopicName.SPEED].time)])
        new_dump[Json.ANGULAR_SPEED] = data

        data = dict([(Json.DATA, self.topics[TopicName.ENCODER_RIGHT_SPEED].data),
                     (Json.TIME, self.topics[TopicName.ENCODER_RIGHT_SPEED].time)])
        new_dump[Json.RIGHT_ENCODER_SPEED] = data

        data = dict([(Json.DATA, self.topics[TopicName.RIGHT_MOTOR].data),
                     (Json.TIME, self.topics[TopicName.RIGHT_MOTOR].time)])
        new_dump[Json.RIGHT_MOTOR_SPEED] = data

        data = dict([(Json.DATA, self.topics[TopicName.POSITION].x),
                     (Json.TIME, self.topics[TopicName.POSITION].time)])
        new_dump[Json.POSITION_X] = data

        data = dict([(Json.DATA, self.topics[TopicName.POSITION].y),
                     (Json.TIME, self.topics[TopicName.POSITION].time)])
        new_dump[Json.POSITION_Y] = data

        data = dict([(Json.DATA, self.topics[TopicName.POSITION].z),
                     (Json.TIME, self.topics[TopicName.POSITION].time)])
        new_dump[Json.POSITION_DIR] = data

        json.dump(new_dump, write_file, indent=2)
        print("File with name has just been created:" + \
               os.getcwd() + "/" + self.file_name + ".")
        print("Finish.")

    def read_data_and_create_plot(self, file_name=None):
        if file_name is not None:
            self.file_name = file_name
        read_file = open(self.file_name, "r")
        data = json.load(read_file)

        names = Json.ALL
        for i in range(0, len(names)):
            plt.subplot(3, 3, i + 1)
            plt.plot(data[names[i]][Json.TIME], data[names[i]][Json.DATA], 'b')
            plt.grid()
            plt.title(PLOT_TITLE[names[i]])
            plt.ylabel(PLOT_LABEL[names[i]])
            plt.xlabel(PLOT_TIME)

    @staticmethod
    def create_desired_plot():
        reference_time = list([0, 0])
        for i in range(1, DESIRED_SPEED_LENGTH):
            reference_time.append(i * TIME_BEFORE_SPEED_CHANGE)
            reference_time.append(i * TIME_BEFORE_SPEED_CHANGE)
        reference_time.append(TIME_BEFORE_SPEED_CHANGE * DESIRED_SPEED_LENGTH)

        plt.subplot(3, 3, 1)
        desired_speeds = DESIRED_LINEAR_SPEEDS
        reference_speed = list([0, desired_speeds[0]])
        for i in range(1, DESIRED_SPEED_LENGTH):
            reference_speed.append(desired_speeds[i - 1])
            reference_speed.append(desired_speeds[i])
        reference_speed.append(desired_speeds[-1])
        plt.plot(reference_time, reference_speed, 'r')

        plt.subplot(3, 3, 4)
        desired_speeds = DESIRED_ANGULAR_SPEEDS
        reference_speed = list([0, desired_speeds[0]])
        for i in range(1, DESIRED_SPEED_LENGTH):
            reference_speed.append(desired_speeds[i - 1])
            reference_speed.append(desired_speeds[i])
        reference_speed.append(desired_speeds[-1])
        plt.plot(reference_time, reference_speed, 'r')


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Test cpu load tool')
    parser.add_argument('--jdir',
                        type=str,
                        help='Default JSON dir',
                        default=str())
    parser.add_argument('--mode', 
                        help='Mode: [only_plot, gather_and_plot]',
                        default='only_plot')
    args = vars(parser.parse_args())

    try:
        JSON_FILE_NAME = args['jdir']
        if args['mode'] == "gather_and_plot":
            PLOT_ONLY = False
        else:
            PLOT_ONLY = True
        test = Test()
        test.do("mode")
    except (rospy.ROSInterruptException, KeyboardInterrupt):
        rospy.logerr('Exception catched')
