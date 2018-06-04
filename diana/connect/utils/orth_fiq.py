# import logging
# from pprint import pformat
from diana.utils.dicom import DicomLevel


def find_item_query(item):
    """
    Have some information about the dixel, want to find the STUID, SERUID, INSTUID
    Returns a _list_ of dictionaries with matches, retrieves any if "retrieve" flag
    """

    q = {}
    keys = {}

    # All levels have these
    keys[DicomLevel.STUDIES] = ['PatientID',
                          'PatientName',
                          'PatientBirthDate',
                          'PatientSex',
                          'StudyInstanceUID',
                          'StudyDate',
                          'StudyTime',
                          'AccessionNumber']

    # Series level has these
    keys[DicomLevel.SERIES] = keys[DicomLevel.STUDIES] + \
                          ['SeriesInstanceUID',
                          'SeriesDescription',
                          'ProtocolName',
                          'SeriesNumber',
                          'NumberOfSeriesRelatedInstances',
                          'Modality']

    # For instance level, use the minimum
    keys[DicomLevel.INSTANCES] = ['SOPInstanceUID', 'SeriesInstanceUID']

    def add_key(q, key, dixel):
        q[key] = dixel.meta.get(key, '')
        return q

    for k in keys[item.level]:
        q = add_key(q, k, item)

    if item.level == DicomLevel.STUDIES and item.meta.get('Modality'):
        q['ModalitiesInStudy'] = item.meta.get('Modality')

    # logging.debug(pformat(q))

    query = {'Level': str(item.level),
            'Query': q}

    return query