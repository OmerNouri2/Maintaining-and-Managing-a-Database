from ParserConf import ParserConf  # from file with the name 'ParserConf' import the class 'ParserConf'
import Dto
from Dto import Logistic
from Dto import Supplier
from Dto import Clinic
from Dto import Vaccine
from GenericDao import GenericDao
from Repository import repo


class Orders:
    def __init__(self, conf_path, out_path):
        self.pc = ParserConf(conf_path)
        self.pc.parse()  # read from config.txt & insert to the tables
        self.count_vaccine_id = self.pc.max_vaccine_id  # the last id that was inserted
        self.total_received = 0
        self.total_sent = 0
        self.total_inventory = self.pc.inventory
        self.total_demand = self.pc.demand_start
        self.logistic_dao = repo.logistic_dao  # dao from type Logistic
        self.vacc_dao = repo.vaccine_dao  # dao from type Vaccine
        self.supp_dao = repo.supp_dao  # dao from type Supplier
        self.dao_clinic = repo.dao_clinic  # dao from type Clinic
        self.output_path = out_path

    def parse(self, order_path):
        # read all texts from the 'orders.txt' file into a string:
        # with - closes the file automatically
        with open(order_path) as f:
            # readlines() – read all the lines of the text file and return them as a list of strings.
            lines = f.readlines()
            for line in lines:
                line_arr = line.split(',')
                param_num = len(line_arr)
                if param_num == 3:
                    self.receive_shipment(line_arr[0], int(line_arr[1]), line_arr[2])
                else:
                    self.send_shipment(line_arr[0], int(line_arr[1]))  # if param_num == 2 --> send_shipment

    def receive_shipment(self, name, amount, date):
        # create new vaccine
        supplier = self.supp_dao.find(name=name)[0]
        self.count_vaccine_id += 1  # increase by 1 the id of the vaccine in order to insert new record
        # add < amount > vaccines from < name > on < date >
        vaccine_date = date.strip()
        if len(vaccine_date) == 9:  # make sure the date is in the format - year-month-day which day is 2 chars
            vaccine_date = vaccine_date[:8] + '0' + vaccine_date[8:]
        vaccine = Dto.Vaccine(self.count_vaccine_id, vaccine_date, supplier.id, amount)
        self.vacc_dao.insert(vaccine)  # insert to the vaccines table new vaccine
        # update count_received of the relevant logistic which arrive from supplier
        logistic = self.logistic_dao.find(id=supplier.logistic)[0]  # get logistic of supplier
        count_received_old = logistic.count_received  # get old value of count_received
        new_count_received_dict = amount + count_received_old
        set_values_dict_count_received = {'count_received': new_count_received_dict}
        cond_dict_count_received = {'id': logistic.id}
        self.logistic_dao.update(set_values_dict_count_received, cond_dict_count_received)  # update the count_received
        self.total_received += amount  # update the total_receives according to the arrived order
        self.total_inventory += amount
        self.summery()

    def send_shipment(self, location, amount):  # send a shipment from the distribution center to one of the clinics
        # reduce the demand in <location> by <amount>
        clinic = self.dao_clinic.find(location=location)[0]
        demand_old = clinic.demand  # get old value of count_received

        # update the demand on the relevant clinic which arrive from file
        new_demand = demand_old - amount
        set_values_dict_clinic = {'demand': new_demand}
        cond_dict_clinic = {'id': clinic.id}
        self.dao_clinic.update(set_values_dict_clinic, cond_dict_clinic)

        # update count_sent of the relevant logistic which arrive from supplier
        logistic = self.logistic_dao.find(id=clinic.logistic)[0]  # get logistic of clinic
        count_sent_old = logistic.count_sent  # get old value of count_sent
        # increase count_sent by <amount>
        new_count_sent = amount + count_sent_old
        set_values_dict_logistic = {'count_sent': new_count_sent}
        cond_dict_logistic = {'id': logistic.id}
        self.logistic_dao.update(set_values_dict_logistic, cond_dict_logistic)

        # update params for summery
        self.total_inventory -= amount # reduce total_inventory by the amount that was sent
        self.total_sent += amount  # update the total_sent according to the arrived order
        self.total_demand -= amount

        # reduce amount from the quantity of vaccines
        vaccs_ordered_by_date = self.vacc_dao.asc_ordered_by('date')
        for vaccine in vaccs_ordered_by_date:
            if amount >= vaccine.quantity:
                amount -= vaccine.quantity  # reduce the quantity of the current vaccine from amount
                # if the quantity of an entry in the Vaccines table reduce to zero, that entry
                # should be removed from the table
                self.vacc_dao.delete(id=vaccine.id)
            else:  # amount < vaccine
                new_quantity = vaccine.quantity - amount
                set_values_dict_quantity = {'quantity': new_quantity}
                cond_dict_quantity_vacc = {'id': vaccine.id}
                self.vacc_dao.update(set_values_dict_quantity, cond_dict_quantity_vacc)
                break  # exit for loop
        self.summery()

    def summery(self):
        with open(self.output_path, 'a') as file:
            file.write(
                '{},{},{},{}\n'.format(self.total_inventory, self.total_demand, self.total_received, self.total_sent))
