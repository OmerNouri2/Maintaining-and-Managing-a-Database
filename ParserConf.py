from Dto import Vaccine
from Dto import Supplier
from Dto import Logistic
from Dto import Clinic
from GenericDao import GenericDao
from Repository import repo


class ParserConf:
    def __init__(self, path):
        self._path = path
        # new lists for all type ot tables in db
        self.vaccines_entries = []
        self.suppliers_entries = []
        self.clinics_entries = []
        self.logistics_entries = []
        self.inventory = 0
        self.demand_start = 0  # quantity of demand arrived from conf file
        self.max_vaccine_id = 0

    def parse(self):
        # The following shows how to read all texts from the readme.txt file into a string:
        # with - closes the file automatically
        with open(self._path) as f:
            # readlines() – read all the lines of the text file and return them as a list of strings.
            lines = f.readlines()
            firstLine = lines[0]  # take the first line from the config file
            numOfEntries = firstLine.split(',')
            lines.pop(0)  # after retrieving the first line we remove it from the list given in the conf file
            vaccines_num = int(numOfEntries[0])
            suppliers_num = int(numOfEntries[1])
            clinics_num = int(numOfEntries[2])
            logistics_num = int(numOfEntries[3])

            # insert all vaccines arrived from conf.txt to the vaccines table
            vacc_dao = GenericDao(Vaccine, repo._conn)
            for i in range(0, vaccines_num):  # from start until vaccines_num, excluding vaccines_num
                self.vaccines_entries = (lines.pop(0)).split(',')  # each time we removes the first line from lines
                vaccine_id = int(self.vaccines_entries[0])
                self.max_vaccine_id = max(vaccine_id, self.max_vaccine_id)
                vaccine_date = self.vaccines_entries[1].strip()
                if len(vaccine_date) == 9:  # make sure the date is in the format - year-month-day which day is 2 chars
                    vaccine_date = vaccine_date[:8] + '0' + vaccine_date[8:]
                vaccine_supplier = int(self.vaccines_entries[2])
                vaccine_quantity = int(self.vaccines_entries[3])
                vaccine_dto = Vaccine(vaccine_id, vaccine_date, vaccine_supplier, vaccine_quantity)
                vacc_dao.insert(vaccine_dto)  # insert to the vaccines table new vaccine
                self.inventory += vaccine_quantity

            # insert all suppliers arrived from conf.txt to the suppliers table
            supp_dao = GenericDao(Supplier, repo._conn)
            for i in range(0, suppliers_num):  # from start until suppliers_num, excluding suppliers_num
                self.suppliers_entries = (lines.pop(0)).split(',')  # each time we removes the first line from lines
                supp_id = int(self.suppliers_entries[0])
                supp_name = self.suppliers_entries[1]
                supp_logistic = int(self.suppliers_entries[2])
                supp_dto = Supplier(supp_id, supp_name, supp_logistic)
                supp_dao.insert(supp_dto)  # insert to the table new supplier

            # insert all clinics arrived from conf.txt to the clinics table
            clinic_dao = GenericDao(Clinic, repo._conn)
            for i in range(0, clinics_num):  # from start until clinics_num, excluding clinics_num
                self.clinics_entries = (lines.pop(0)).split(',')  # each time we removes the first line from lines
                clinic_id = int(self.clinics_entries[0])
                clinic_location = self.clinics_entries[1]
                clinic_demand = int(self.clinics_entries[2])
                clinic_logistic = int(self.clinics_entries[3])
                clinic_dto = Clinic(clinic_id, clinic_location, clinic_demand, clinic_logistic)
                clinic_dao.insert(clinic_dto)  # insert to the table new clinic
                self.demand_start += clinic_demand

            # insert all logistics arrived from conf.txt to the logistics table
            logistic_dao = GenericDao(Logistic, repo._conn)
            for i in range(0, logistics_num):  # from start until logistics_num, excluding logistics_num
                self.logistics_entries = (lines.pop(0)).split(',')  # each time we removes the first line from lines
                log_id = self.logistics_entries[0]
                log_name = self.logistics_entries[1]
                log_count_sent = self.logistics_entries[2]
                log_count_received = self.logistics_entries[3]
                logistic_dto = Logistic(log_id, log_name, log_count_sent, log_count_received)
                logistic_dao.insert(logistic_dto)  # insert to the table new clinic
