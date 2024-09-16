from email import message
import json
from operator import le
from re import M
import requests
import frappe
from frappe.utils import today, add_days, date_diff,cint
from time import strptime
from datetime import datetime
import pandas as pd
from frappe import _


@frappe.whitelist()
def get_server_date():
    return today()

def application_allowed_from(date):
    return ''

@frappe.whitelist()
def salary_amount_update(grade):
    datalist = []
    data = {}
    emp_grade = frappe.db.get_value('Employee Grade',{'name':grade},['basic','hra','pf'])
    data.update({
        'basic':emp_grade[0],
        'hra':emp_grade[1],
        'pf':emp_grade[2],
    })
    datalist.append(data.copy())
    return datalist

@frappe.whitelist()
def leave_type_validation(emp,leave_type):
    data = []
    if leave_type == 'Maternity Leave':
        emp = frappe.db.get_value('Employee',{'name':emp,'status':'Active'},['gender'])
        if emp == 'Male':
            data.append("Maternity Leave")
    return data 
    
