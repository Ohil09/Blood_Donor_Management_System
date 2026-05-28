from flask_login import current_user


def get_current_hospital_id():
    if not current_user.is_authenticated:
        return None
    return current_user.hospital_id


def get_current_hospital_info():
    if not current_user.is_authenticated:
        return None, None
    return current_user.hospital_id, current_user.hospital_name
