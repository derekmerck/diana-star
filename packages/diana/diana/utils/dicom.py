import logging
from hashlib import sha1
from datetime import datetime
from aenum import Enum, auto

# Diana-agnostic Dicom info

class DicomLevel(Enum):
    """
    Enumerated DICOM service levels
    """
    INSTANCES = auto()
    SERIES = auto()
    STUDIES = auto()
    PATIENTS = auto()

    def parent_level(self):
        if self==DicomLevel.STUDIES:
            return DicomLevel.PATIENTS
        elif self==DicomLevel.SERIES:
            return DicomLevel.STUDIES
        elif self == DicomLevel.INSTANCES:
            return DicomLevel.SERIES
        else:
            logging.warning("Bad child request for {}".format(self))

    def child_level(self):
        if self==DicomLevel.PATIENTS:
            return DicomLevel.STUDIES
        elif self==DicomLevel.STUDIES:
            return DicomLevel.SERIES
        elif self==DicomLevel.SERIES:
            return DicomLevel.INSTANCES
        else:
            logging.warning("Bad child request for {}".format(self))

    def __str__(self):
        return '{0}'.format(self.name.lower())


def orthanc_id(PatientID, StudyInstanceUID, SeriesInstanceUID=None, SOPInstanceUID=None):
    if not SeriesInstanceUID:
        s = "|".join([PatientID, StudyInstanceUID])
    elif not SOPInstanceUID:
        s = "|".join([PatientID, StudyInstanceUID, SeriesInstanceUID])
    else:
        s = "|".join([PatientID, StudyInstanceUID, SeriesInstanceUID, SOPInstanceUID])
    h = sha1(s.encode("UTF8"))
    d = h.hexdigest()
    return '-'.join(d[i:i+8] for i in range(0, len(d), 8))


def dicom_strftime( dtm ):

    try:
        # GE Scanner dt format
        ts = datetime.strptime( dtm , "%Y%m%d%H%M%S")
        return ts
    except ValueError:
        # Wrong format
        pass

    try:
        # Siemens scanners use a slightly different aggregated format with fractional seconds
        ts = datetime.strptime( dtm , "%Y%m%d%H%M%S.%f")
        return ts
    except ValueError:
        # Wrong format
        pass

    logging.error("Can't parse date time string: {0}".format( dtm ))
    ts = datetime.now()
    return ts



def dicom_strptime( dts ):
    return datetime.strptime( dts, "%Y%m%d%H%M%S" )



