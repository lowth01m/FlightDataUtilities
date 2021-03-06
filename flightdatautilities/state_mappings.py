# -*- coding: utf-8 -*-
##############################################################################

'''
Multi-state Parameter State Value Mappings
'''

##############################################################################
# Import


import re

from fnmatch import translate


##############################################################################
# Constants


PARAMETER_CORRECTIONS = {
    'Alpha Floor': {1: 'Engaged'},
    'Alternate Law': {1: 'Engaged'},
    'Altitude Capture Mode': {1: 'Activated'},
    'Altitude Mode': {1: 'Activated'},
    'AP (*) Engaged': {1: 'Engaged'},
    'APU (*) On': {1: 'On'},
    'APU Bleed Valve Open': {1: 'Open'},
    'APU Fire': {1: 'Fire'},
    'AT Active': {1: 'Activated'},
    'Autobrake Selected RTO': {1: 'Selected'},
    'Cabin Altitude Warning': {1: 'Warning'},
    'Climb Mode Active': {1: 'Activated'},
    'Direct Law': {1: 'Engaged'},
    'ECS Pack (*) High Flow': {1: 'High', 0: 'Low'},
    'ECS Pack (*) On': {1: 'On'},
    'Eng (*) Anti Ice': {1: 'On'},
    'Eng (*) Bleed': {1: 'Open', 0: 'Closed'},
    'Eng (*) Fire': {1: 'Fire'},
    'Eng (*) Thrust Reverser Deployed': {1: 'Deployed'},
    'Eng (*) Thrust Reverser In Transit': {1: 'In Transit'},
    'Eng (*) Thrust Reverser Unlocked': {1: 'Unlocked'},
    'Eng (*) Fire (1L)': {1: 'Fire'},
    'Eng (*) Fire (1R)': {1: 'Fire'},
    'Eng (*) Fire (2L)': {1: 'Fire'},
    'Eng (*) Fire (2R)': {1: 'Fire'},
    'Eng (*) Oil Press Low': {1: 'Low Press'},
    'Eng (*) Thrust Reverser (L) Deployed': {1: 'Deployed'},
    'Eng (*) Thrust Reverser (L) Unlocked': {1: 'Unlocked'},
    'Eng (*) Thrust Reverser (R) Deployed': {1: 'Deployed'},
    'Eng (*) Thrust Reverser (R) Unlocked': {1: 'Unlocked'},
    'Eng (*) Thrust Reverser Unlocked': {1: 'Unlocked'},
    'Event Marker (*)': {1: 'Event'},
    'Event Marker (Capt)': {1: 'Event'},
    'Event Marker (FO)': {1: 'Event'},
    'Event Marker': {1: 'Event'},
    'Expedite Climb Mode': {1: 'Activated'},
    'Expedite Descent Mode': {1: 'Activated'},
    'Fire APU Single Bottle System': {1: 'Fire'},
    'Fire APU Dual Bottle System': {1: 'Fire'},
    'Flap Alternate Armed': {1: 'Armed'},  # FIXME: Add {0: 'Not Armed'}?
    'Flap Load Relief': {0: 'Normal', 1: 'Load Relief'},
    'Flare Mode': {1: 'Engaged'},
    'Fuel Qty (L) Low': {1: 'Warning'},
    'Fuel Qty (R) Low': {1: 'Warning'},
    'Fuel Qty Low': {1: 'Warning'},
    'Gear (*) Down': {1: 'Down', 0: 'Up'},
    'Gear (*) In Air': {1: 'Air', 0: 'Ground'},
    'Gear (*) On Ground': {1: 'Ground', 0: 'Air'},
    'Gear (*) Red Warning': {1: 'Warning'},
    'Gear (L) Down': {1: 'Down',0: 'Up'},
    'Gear (L) In Transit': {1: 'In Transit'},
    'Gear (L) On Ground': {1: 'Ground',0: 'Air'},
    'Gear (L) Red Warning': {1: 'Warning'},
    'Gear (L) Up': {1: 'Up',0: 'Down'},
    'Gear (N) Down': {1: 'Down',0: 'Up'},
    'Gear (N) In Transit': {1: 'In Transit'},
    'Gear (N) Red Warning': {1: 'Warning'},
    'Gear (N) Up': {1: 'Up',0: 'Down'},
    'Gear (R) Down': {1: 'Down',0: 'Up'},
    'Gear (R) In Transit': {1: 'In Transit'},
    'Gear (R) On Ground': {1: 'Ground',0: 'Air'},
    'Gear (R) Red Warning': {1: 'Warning'},
    'Gear (R) Up': {1: 'Up',0: 'Down'},
    'Gear Down Selected': {1: 'Down',0: 'Up'},
    'Gear Down': {1: 'Down', 0: 'Up'},
    'Gear In Air': {1: 'Air', 0: 'Ground'},
    'Gear In Transit': {1: 'In Transit'},
    'Gear On Ground': {1: 'Ground', 0: 'Air'},
    'Gear Up Selected': {1: 'Up', 0: 'Down'},
    'Gear Up Selected': {1: 'Up',0: 'Down'},
    'Gear Up': {1: 'Up'},
    'Heading Mode Active': {1: 'Activated'},
    'ILS Glideslope Capture Active': {1: 'Activated'},
    'ILS Inner Marker': {1: 'Present'},
    'ILS Inner Marker (Capt)': {1: 'Present'},
    'ILS Inner Marker (FO)': {1: 'Present'},
    'ILS Localizer Capture Active': {1: 'Activated'},
    'ILS Localizer Track Active': {1: 'Activated'},
    'ILS Middle Marker': {1: 'Present'},
    'ILS Middle Marker (Capt)': {1: 'Present'},
    'ILS Middle Marker (FO)': {1: 'Present'},
    'ILS Outer Marker': {1: 'Present'},
    'ILS Outer Marker (Capt)': {1: 'Present'},
    'ILS Outer Marker (FO)': {1: 'Present'},
    'Jettison Nozzle': {1: 'Jettison'},
    'Key HF': {1: 'Keyed'},
    'Key HF (*)': {1: 'Keyed'},
    'Key Satcom (*)': {1: 'Keyed'},
    'Key Satcom': {1: 'Keyed'},
    'Key VHF': {1: 'Keyed'},
    'Key VHF (*)': {1: 'Keyed'},
    'Key VHF (*) (Capt)': {1: 'Keyed'},
    'Key VHF (*) (FO)': {1: 'Keyed'},
    'Land Track Activated': {1: 'Activated'},
    'Landing Configuration Gear Warning': {1: 'Warning'},
    'Landing Configuration Speedbrake Caution': {1: 'Caution'},
    'Master Caution (Capt)': {1: 'Caution'},
    'Master Caution (FO)': {1: 'Caution'},
    'Master Caution': {1: 'Caution'},
    'Master Warning (Capt)': {1: 'Warning'},
    'Master Warning (FO)': {1: 'Warning'},
    'Master Warning': {1: 'Warning'},
    'NAV Mode Active': {1: 'Activated'},
    'Normal Law': {1: 'Engaged'},
    'Open Climb Mode': {1: 'Activated'},
    'Open Descent Mode': {1: 'Activated'},
    'Overspeed Warning': {1: 'Overspeed'},
    'Pitch Alternate Law (*)': {1: 'Engaged'},
    'Pitch Alternate Law': {1: 'Engaged'},
    'Pitch Direct Law': {1: 'Engaged'},
    'Pitch Normal Law': {1: 'Engaged'},
    'Roll Alternate Law': {1: 'Engaged'},
    'Roll Direct Law': {1: 'Engaged'},
    'Roll Go Around Mode Active': {1: 'Activated'},
    'Roll Normal Law': {1: 'Engaged'},
    'Runway Mode Active': {1: 'Activated'},
    'Slat Alternate Armed': {1: 'Armed'},  # FIXME: Add {0: 'Not Armed'}?
    'Speed Control (*) Auto': {1: 'Auto'},
    'Speed Control (*) Manual': {0: 'Auto'},
    'Speed Control Auto': {1: 'Auto'},
    'Speed Control Manual': {0: 'Auto'},
    'Speedbrake Armed': {1: 'Armed'},
    'Speedbrake Deployed': {1: 'Deployed'},
    'Spoiler (L) Deployed': {1: 'Deployed'},
    'Spoiler (L) Outboard Deployed': {1: 'Deployed'},
    'Spoiler (R) Outboard Deployed': {1: 'Deployed'},
    'Spoiler (R) Deployed': {1: 'Deployed'},
    'Stick Pusher': {1: 'Push'},
    'Stick Pusher (L)': {1: 'Push'},
    'Stick Pusher (R)': {1: 'Push'},
    'Stick Shaker': {1: 'Shake'},
    'Stick Shaker (*)': {1: 'Shake'},
    'Stick Shaker (L)': {1: 'Shake'},
    'Stick Shaker (R)': {1: 'Shake'},
    'Takeoff And Go Around': {1: 'TOGA'},
    'Takeoff Configuration Aileron Warning': {1: 'Warning'},
    'Takeoff Configuration AP Warning': {1: 'Warning'},
    'Takeoff Configuration Flap Warning': {1: 'Warning'},
    'Takeoff Configuration Gear Warning': {1: 'Warning'},
    'Takeoff Configuration Parking Brake Warning': {1: 'Warning'},
    'Takeoff Configuration Rudder Warning': {1: 'Warning'},
    'Takeoff Configuration Spoiler Warning': {1: 'Warning'},
    'Takeoff Configuration Stabilizer Warning': {1: 'Warning'},
    'Takeoff Configuration Warning': {1: 'Warning'},
    'TAWS (L) Dont Sink': {1: 'Warning'},
    'TAWS (L) Glideslope Cancel': {1: 'Cancel'},
    'TAWS (L) Too Low Gear': {1: 'Warning'},
    'TAWS (R) Dont Sink': {1: 'Warning'},
    'TAWS (R) Glideslope Cancel': {1: 'Cancel'},
    'TAWS (R) Too Low Gear': {1: 'Warning'},
    'TAWS Alert': {1: 'Alert'},
    'TAWS Caution Obstacle': {1: 'Caution'},
    'TAWS Caution Terrain': {1: 'Caution'},
    'TAWS Caution': {1: 'Caution'},
    'TAWS Dont Sink': {1: 'Warning'},
    'TAWS Failure': {1: 'Failed'},
    'TAWS Glideslope': {1: 'Warning'},
    'TAWS Glideslope Cancel': {1: 'Cancel'},
    'TAWS Minimums': {1: 'Minimums'},
    'TAWS Obstacle Warning': {1: 'Warning'},
    'TAWS Predictive Windshear': {1: 'Warning'},
    'TAWS Pull Up': {1: 'Warning'},
    'TAWS Sink Rate': {1: 'Warning'},
    'TAWS Terrain Caution': {1: 'Caution'},
    'TAWS Terrain Ahead Pull Up': {1: 'Warning'},
    'TAWS Terrain Pull Up': {1: 'Warning'},
    'TAWS Terrain Override' : {1: 'Override'},
    'TAWS Terrain Warning Amber': {1: 'Warning'},
    'TAWS Terrain Warning Red': {1: 'Warning'},
    'TAWS Terrain': {1: 'Warning'},
    'TAWS Too Low Flap': {1: 'Warning'},
    'TAWS Too Low Gear': {1: 'Warning'},
    'TAWS Too Low Terrain': {1: 'Warning'},
    'TAWS Warning': {1: 'Warning'},
    'TAWS Windshear Caution': {1: 'Caution'},
    'TAWS Windshear Siren': {1: 'Siren'},
    'TAWS Windshear Warning': {1: 'Warning'},
    'TCAS (L) Failure': {1: 'Failed'},
    'TCAS (R) Failure': {1: 'Failed'},
    'TCAS Failure': {1: 'Failed'},
    'Thrust Mode Selected (L)': {1: 'Selected'},
    'Thrust Mode Selected (R)': {1: 'Selected'},
    'Wing Anti Ice': {1: 'On'},
    'Alpha Floor': {1:'Engaged'},
    'Takeoff And Go Around': {1:'TOGA'},
    'Cabin Altitude Warning': {1:'Warning'},
    'Eng (*) Bleed': {1:'Open'},
    'Fuel Jettison Nozzle': {1:'Disagree'},
    'Alternate Law': {1:'Engaged'},
    'Pitch Alternate Law': {1:'Engaged'},
    'Roll Alternate Law': {1:'Engaged'},
    'Direct Law': {1:'Engaged'},
    'Pitch Direct Law': {1:'Engaged'},
    'Roll Direct Law': {1:'Engaged'},
    'Overspeed Warning': {1:'Overspeed'},
    'Master Warning': {1: 'Warning'},
    'TAWS Obstacle Warning': {1:'Warning'},
    'TAWS Terrain Ahead': {1:'Warning'},
    'TCAS TA': {1:'TA'},
    'TCAS RA': {1:'RA'},
    'TCAS Failure': {1:'Failed'}, 
}

STATE_CORRECTIONS = {
    'Not Closed': 'Open',
    'Down Lock': 'Down',
    'Openned': 'Open',
    'Not engaged': 'Not Engaged',
    'on': 'On',
    'off': 'Off',
    'Not armed': 'Not Armed',
    'APU Bleed Valve Fully Open': 'Open',
    'APU Bleed Valve not Fully Open': 'Closed',
    'no Fault': None,
    'false': 'False',
    'true': 'True',
    'valid': 'Valid',
    'not valid': 'Invalid',
    'down': 'Down',
    'up': 'Up',
    'UP': 'Up',
    'DOWN': 'Down',
}

# Examples where states conflict:
# * VMO/MMO Selected

TRUE_STATES = [
    'Engaged',
    'On',
    'CMD Mode',
    'CWS Mode',
    'Open',  # ?
    'FMA Displayed',
    'Event',  # ?
    'Asymmetrical',
    'Ground',  # ? Landing Squat Switch (L/N/R), Gear (L) On Ground
    'Down',  # ? Gear (L/R/N) Down
    'Good',
    'Warning',
    'Keyed',
    'Track Phase',
    'Selected',
    'Deployed',
    'Unlocked',
    'AC BUS 2 OFF',
    'APU Bleed Valve not Fully Open',  # APU Bleed Valve Not Open
    'Not armed',  # ? ATS Arming Lever Off
    'APU Fire',
    'Aft CG',
    'Fault',
    'Valid',
]


FALSE_STATES = [
    'Not Engaged',
    'Off',
    'Not in CMD Mode',
    'Not in CWS Mode',
    'Closed',  # ?
    'FMA Not Displayed',
    'Air',  # ? Landing Squat Switch (L/N/R)
    'Up',  # ? Gear (L/R/N) Down
    'FAIL/OFF',  # Slat Assymetrical
    'AC BUS 2 not OFF',
    'APU Bleed Valve Fully Open',  # APU Bleed Valve Not Open
    'Armed',  # ? ATS Arming Lever Off
    'No APU Fire',
    'No Aft CG',
    'Normal',
    'No Warning',
    'No Fault',
    'Invalid',
]


##############################################################################
# Functions


def get_parameter_correction(parameter_name):

    if parameter_name in PARAMETER_CORRECTIONS:
        return PARAMETER_CORRECTIONS[parameter_name]

    for pattern, mapping in PARAMETER_CORRECTIONS.items():
        if '(*)' in pattern or '(?)' in pattern:
            regex = translate(pattern)
            re_obj = re.compile('^' + regex + '$')
            matched = re_obj.match(parameter_name)
            if matched:
                return mapping


def normalise_discrete_mapping(original_mapping, parameter_name=None):

    true_state = original_mapping[1]
    false_state = original_mapping[0]

    true_state = STATE_CORRECTIONS.get(true_state, true_state)
    false_state = STATE_CORRECTIONS.get(false_state, false_state)

    inverted = true_state in FALSE_STATES or false_state in TRUE_STATES

    normalised_mapping = \
        get_parameter_correction(parameter_name) if parameter_name else None

    if not normalised_mapping:
        normalised_mapping = {0: false_state, 1: true_state}

    return normalised_mapping, inverted


def normalise_multistate_mapping(original_mapping, parameter_name=None):

    normalised_mapping = \
        get_parameter_correction(parameter_name) if parameter_name else None

    if not normalised_mapping:
        normalised_mapping = {}

        for value, state in original_mapping.items():
            normalised_mapping[value] = STATE_CORRECTIONS.get(state, state)

    return normalised_mapping
