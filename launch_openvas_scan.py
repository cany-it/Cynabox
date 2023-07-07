from gvm.connections import UnixSocketConnection
from bs4 import BeautifulSoup
from gvm.protocols.gmp import Gmp
import io
import os
import xml.etree.ElementTree as ET

ov_user="admin"
ov_password="admin"
path_gvmsock = "/run/gvmd/gvmd.sock"
connection_gvm = UnixSocketConnection(path=path_gvmsock)
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
    
def get_task_id(gmp, tsk) :
    gmp.authenticate(ov_user, ov_password)
    #ICI C'EST UN PEU CHELOU PARCE QUE IL Y A LE FILTER_ID QUI CORRESPONND AU FILTRE DE LA PAGE WEB OPENVAS CA PERMET DE RECUPERER PLUS DE 10 ENTREES DE CVE (NOMBRE PAR DEFAUT DANS UNE PAGE)
    #"TaskFilter" c'est censé être le nom du filter mais il faut le créer en interface graphique pour qu'il le trouve ducoup
    all_tasks = gmp.get_tasks(filter_id=get_filter_id(gmp, "TaskFilter"))

    # analyser le contenu HTML avec BeautifulSoup
    task_soup = BeautifulSoup(all_tasks, "xml")
    tasks = task_soup.get_tasks_response.find_all("task")

    for task in tasks:
        # extraire le contenu des balises souhaitées
        name_task = task.find_all("name")[1].string
        if name_task == tsk :
            task_id = task.get("id")
    return task_id

with Gmp(connection=connection_gvm) as gmp:   
	gmp.authenticate(ov_user, ov_password)  
	task_id = get_task_id(gmp, scan_name)
	gmp.start_task(task_id)