# state_manager.py
import json

STATE_FILE = "shared_state.json"

def _load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

####################################################
## Getter and Setter Functions #####################
####################################################

#####################################################

def get_access_granted():
    return _load_state().get("access_granted", False)

def set_access_granted(value):
    state = _load_state()
    state["access_granted"] = value
    _save_state(state)

#####################################################

def get_door_unlocked():
    return _load_state().get("door_unlocked", False)

def set_door_unlocked(value):
    state = _load_state()
    state["door_unlocked"] = value
    _save_state(state)

######################################################

def get_motion_detected():
    return _load_state().get("motion_detected", False)

def set_motion_detected(value):
    state = _load_state()
    state["motion_detected"] = value
    _save_state(state)

######################################################

def get_nap_in_progress():
    return _load_state().get("nap_in_progress", False)

def set_nap_in_progress(value):
    state = _load_state()
    state["nap_in_progress"] = value
    _save_state(state)

######################################################

def get_motion_entering_pod():
    return _load_state().get("motion_entering_pod", False)

def set_motion_entering_pod(value):
    state = _load_state()
    state["motion_entering_pod"] = value
    _save_state(state)

######################################################

def get_motion_exiting_pod():
    return _load_state().get("motion_exiting_pod", False)

def set_motion_exiting_pod(value):
    state = _load_state()
    state["motion_exiting_pod"] = value
    _save_state(state)

######################################################

def get_nap_completed():
    return _load_state().get("nap_completed", False)

def set_nap_completed(value):
    state = _load_state()
    state["nap_completed"] = value
    _save_state(state)

######################################################

def get_alarm_sounding():
    return _load_state().get("alarm_sounding", False)

def set_alarm_sounding(value):
    state = _load_state()
    state["alarm_sounding"] = value
    _save_state(state)

######################################################

def get_snooze_alarm():
    return _load_state().get("snooze_alarm", False)

def set_snooze_alarm(value):
    state = _load_state()
    state["snooze_alarm"] = value
    _save_state(state)

######################################################