import os


def get_path_components(folder_path):
    path = os.path.normpath(folder_path)
    return path.split(os.sep)


def get_traceability_link(document_name):
    return "{} - Traceability.html".format(document_name)


def get_traceability_deep_link(document_name):
    return "{} - Traceability Deep.html".format(document_name)
