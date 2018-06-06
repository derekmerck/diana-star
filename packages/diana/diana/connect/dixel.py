from diana.utils.dicom import DicomLevel, orthanc_id
from .apis import Item
import attr


@attr.s
class DicomItem(Item):
    level = attr.ib(default=DicomLevel.STUDIES)
    file = attr.ib(repr=False, default=None)

    def oid(self, level=None):
        # This is not a property because a dixel can generate the OID for any higher level
        # - instances can return instance(default), series, study
        # - series can return series (default), study
        # - studies can return study (default)

        # Already have a precomputed oid available
        if not level and self.meta.get('oid'):
            return self.meta.get('OID')

        # If a level is supplied, use that, otherwise self.level
        level = level or self.level

        if level == DicomLevel.STUDIES:
            return orthanc_id(self.meta["PatientID"],
                              self.meta["StudyInstanceUID"])
        elif level == DicomLevel.SERIES:
            return orthanc_id(self.meta["PatientID"],
                              self.meta["StudyInstanceUID"],
                              self.meta["SeriesInstanceUID"])
        else:
            return orthanc_id(self.meta["PatientID"],
                              self.meta["StudyInstanceUID"],
                              self.meta["SeriesInstanceUID"],
                              self.meta["SOPInstanceUID"])


# Alias Dixel, Dx to DicomItem
Dixel = DicomItem
Dx = DicomItem