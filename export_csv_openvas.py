from gvm.connections import UnixSocketConnection
from bs4 import BeautifulSoup
from gvm.protocols.gmp import Gmp
import io
import os
import xml.etree.ElementTree as ET
import gvm.protocols.gmpv224 as en

ov_user="admin"
ov_password="admin"
path_gvmsock = "/run/gvmd/gvmd.sock"
connection_gvm = UnixSocketConnection(path=path_gvmsock)
report_format_id = en.ReportFormatType.XML
scan_name = "scan_openvas"

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

def get_report_id(gmp, rp):
    gmp.authenticate(ov_user, ov_password)
	#ICI C'EST UN PEU CHELOU PARCE QUE IL Y A LE FILTER_ID QUI CORRESPONND AU FILTRE DE LA PAGE WEB OPENVAS CA PERMET DE RECUPERER PLUS DE 10 ENTREES DE CVE (NOMBRE PAR DEFAUT DANS UNE PAGE)
    #"ReportFilter" c'est censé être le nom du filter mais il faut le créer en interface graphique pour qu'il le trouve ducoup
    all_reports = gmp.get_reports(filter_id=get_filter_id(gmp, "ReportFilter"))

    # analyser le contenu HTML avec BeautifulSoup
    report_soup = BeautifulSoup(all_reports, "xml")
    reports = report_soup.get_reports_response.find_all("report")
    
    for report in reports:
        # extraire le contenu des balises souhaitées
        name_report = report.find_all("name")[0].string
        if name_report == rp :
            report_id = report.get("id")
    return report_id

with Gmp(connection=connection_gvm) as gmp:   
    gmp.authenticate(ov_user, ov_password)  
    report_id=get_report_id(gmp, scan_name)

    report = gmp.get_report(report_id=report_id, report_format_id=report_format_id)
    report_xml = ET.CSV(report)
    report_stream = ET.tostring(report_xml)
    
    # Écrire le flux de données dans un fichier
    with open(f"./OVreport_{scan_name}.csv", "wb") as file:
        file.write(report_stream)