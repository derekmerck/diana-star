import hashlib

def simple_anon_map(item):
    # If not item.meta['AnonName'] get it this way...

    return {
        'Replace': {
            'PatientName': item.meta['AnonName'],
            'PatientID': item.meta['AnonID'],
            'PatientBirthDate': item.meta['AnonDoB'].replace('-', ''),
            'AccessionNumber': hashlib.md5(item.meta['AccessionNumber']).hexdigest(),
        },
        'Keep': ['PatientSex', 'StudyDescription', 'SeriesDescription'],
        'Force': True
    }