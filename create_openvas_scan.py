from gvm.connections import UnixSocketConnection
from bs4 import BeautifulSoup
from gvm.protocols.gmp import Gmp
import io
import os
import sys
import xml.etree.ElementTree as ET
import export_csv_openvas as eo
import launch_openvas_scan as lo

ov_user="admin"
ov_password="admin"
path_gvmsock = "/run/gvmd/gvmd.sock"
connection_gvm = UnixSocketConnection(path=path_gvmsock)
scan_name = "scan_openvas" #Nom du scan
target = sys.argv[1].split(',')# IP à intégrer

def get_scan_config_id(gmp, config):
    all_configs = gmp.get_scan_configs()

    # analyser le contenu HTML avec BeautifulSoup
    config_soup = BeautifulSoup(all_configs, "xml")
    scan_configs = config_soup.get_configs_response.find_all("config")

    for scan_config in scan_configs:
        # extraire le contenu des balises souhaitées
        name_config = scan_config.find_all("name")[1].string
        if name_config == config :
            scan_config_id = scan_config.get("id")
    return scan_config_id

def get_filter_id(gmp, flt):
    all_filters = gmp.get_filters()

    # analyser le contenu HTML avec BeautifulSoup
    filter_soup = BeautifulSoup(all_filters, "xml")
    filters = filter_soup.get_filters_response.find_all("filter")

    for filter in filters:
        # extraire le contenu des balises souhaitées
        name_filter = filter.find_all("name")[1].string
        if name_filter == flt :
            filter_id = filter.get("id")
    return filter_id

def get_target_id(gmp, targ):
    all_targets = gmp.get_targets(filter_id=get_filter_id(gmp, "TargetFilter"))

    # analyser le contenu HTML avec BeautifulSoup
    target_soup = BeautifulSoup(all_targets, "xml")
    targets = target_soup.get_targets_response.find_all("target")

    for target in targets:
        # extraire le contenu des balises souhaitées
        name_target = target.find_all("name")[1].string
        if name_target == targ :
            target_id = target.get("id")
    return target_id

def get_scanner_id(gmp, sc):
    gmp.authenticate(ov_user, ov_password)
    all_scanners = gmp.get_scanners()

    # analyser le contenu HTML avec BeautifulSoup
    scanner_soup = BeautifulSoup(all_scanners, "xml")
    scanners = scanner_soup.get_scanners_response.find_all("scanner")

    for scanner in scanners:
        # extraire le contenu des balises souhaitées
        name_scanner = scanner.find_all("name")[1].string
        if name_scanner == sc :
            scanner_id = scanner.get("id")
    return scanner_id
    
with Gmp(connection=connection_gvm) as gmp:  
    gmp.authenticate(ov_user, ov_password)		
    scan_config_id = get_scan_config_id(gmp, "Full and Fast")
    target_id = get_target_id(gmp, target)
    scanner_id = get_scanner_id(gmp, "OpenVAS Default")
    gmp.create_task(scan_name, scan_config_id, target_id, scanner_id)

with Gmp(connection=connection_gvm) as gmp:   
    gmp.authenticate(ov_user, ov_password)  
    report_id=eo.get_report_id(gmp, scan_name)

    report = gmp.get_report(report_id=report_id, report_format_id=eo.report_format_id)
    report_xml = ET.CSV(report)
    report_stream = ET.tostring(report_xml)

# Écrire le flux de données dans un fichier
with open(f"./OVreport_{scan_name}.csv", "wb") as file:
    file.write(report_stream)

with Gmp(connection=connection_gvm) as gmp:   
	gmp.authenticate(ov_user, ov_password)  
	task_id = lo.get_task_id(gmp, scan_name)
	gmp.start_task(task_id)
