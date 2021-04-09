from enum import Enum

class AbstractEnum(Enum):
    # Formats the names of the Enum items
    def to_value(self):
        return str(self.name).lower()

    # Formats the html representation of the field
    def __str__(self):
        return self.to_value()

    def __repr__(self):
        return self.to_value()

class MeasurementType():

    class AnalogueInput(AbstractEnum):
        GENERAL_PURPOSE = 1
        VOLTAGE = 2
        CURRENT = 3
        STRAIN_GAGE = 4
        VIBRATION = 5
        ACCELEROMETER = 6
        RESOLVER = 7
        POTENTIOMETER = 8
        MV_V = 9

    class AnalogueOutput(AbstractEnum):
        GENERAL_PURPOSE = 1
        VOLTAGE = 2
        CURRENT = 3
        SIMULATED_RESOLVER = 4
        SIMULATED_LVDT = 5

    class Temperature(AbstractEnum):
        RTD = 1
        THERMOCOUPLE = 2
    
    class Frequency(AbstractEnum):
        GENERAL_PURPOSE = 1
        SPEED = 2
        TURBINE_FLOWMETER = 3
        ANEMOMETER = 4
        TTL = 5

    class DigitalInput(AbstractEnum):
        GENERAL_PURPOSE = 1

    class DigitalOutput(AbstractEnum):
        GENERAL_PURPOSE = 1

    class Ethernet(AbstractEnum):
        COPPER = 1
        FIBER = 2

    class Pressure(AbstractEnum):
        GAS = 1
        LIQUID = 2

    class Humidity(AbstractEnum):
        GENERAL_PURPOSE = 1
        DEW_POINT = 2

    class Thrust(AbstractEnum):
        GENERAL_PURPOSE = 1

    class Buzzout(AbstractEnum):
        END_2_END = 1
        POLARITY = 2

# Convert these into Enums at some point
ENG_UNITS = {0: 'V', 1: 'mA', 2: 'degC', 3: 'Hz', 4: 'Ohms',
    5: 'm', 6: 'psi', 7: 'kg', 8: 'm/s', 9: 'lbf'
}
TOLERANCE_TYPES = {0: 'Units', 1: f'%FS', 2: '%RDG'}


#class Measurement():
    # Dictionary of units
    # Type
    # Description
    # 
    