import frappe
import datetime 
import dateutil.relativedelta
from datetime import datetime, timedelta
from datetime import date
from frappe.utils.data import add_days, add_years, today,getdate
from frappe.utils.file_manager import get_file
from frappe.utils.csvutils import read_csv_content
from frappe.model.mapper import get_mapped_doc
from frappe.utils import date_diff, add_months, today,nowtime,nowdate,format_date
from frappe import throw,_

@frappe.whitelist()
def cron_job():
    job = frappe.db.exists('Scheduled Job Type', 'mark_att')
    if not job:
        sjt = frappe.new_doc("Scheduled Job Type")  
        sjt.update({
            "method" : 'johoku.mark_attendance.mark_att',
            "frequency" : 'Cron',
            "cron_format" : '*/11 * * * *'
        })
        sjt.save(ignore_permissions=True)

@frappe.whitelist()
def cron_job1():
    job = frappe.db.exists('Scheduled Job Type', 'push_punch')
    if not job:
        sjt = frappe.new_doc("Scheduled Job Type")  
        sjt.update({
            "method" : 'johoku.mark_attendance.push_punch',
            "frequency" : 'Cron',
            "cron_format" : '*/7 * * * *'
        })
        sjt.save(ignore_permissions=True)

@frappe.whitelist()
def cron_job2():
    job = frappe.db.exists('Scheduled Job Type', 'delete_urc_automatically')
    if not job:
        sjt = frappe.new_doc("Scheduled Job Type")  
        sjt.update({
            "method" : 'johoku.mark_attendance.delete_urc_automatically',
            "frequency" : 'Cron',
            "cron_format" : '30 00 * * *'
        })
        sjt.save(ignore_permissions=True)


@frappe.whitelist()
def get_approver(department, employee_id):
    user = frappe.db.get_value('Employee_id', employee_id, 'user_id')
    roles = frappe.get_roles(user)
    if 'GM' in roles:
        return frappe.db.get_value('Department', department, "ceo")
    elif 'HOD' in roles:
        return frappe.db.get_value('Department', department, "gm")
    else:
        return frappe.db.get_value('Department', department, "hod")  

@frappe.whitelist()
def get_day():
    today = getdate('2023-02-04')
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    print("Today: " + str(today))
    print("Start: " + str(start))
    print("End: " + str(end))

def get_year():
    today_day = date.today()
    previous_year = add_years(today_day,1)
    if today_day == today_day:
        print('hi')
    else:
        print('no')    
    print(today_day.year)
    print(previous_year.year)


@frappe.whitelist()
def department():
    result = frappe.db.sql("""SELECT employee_category, COUNT(*) AS count
                         FROM `tabShift Assignment`
                         WHERE start_date BETWEEN %s AND %s
                         AND department = %s
                         AND shift_type = %s
                         AND docstatus = 1
                         GROUP BY employee_category""",
                      ('2023-02-20', '2023-02-26', 'Production - JMPL', '1'),
                      as_dict=True)
    if result:
        for row in result:
            print("Employee Category:", row["employee_category"], "Count:", row["count"])
    else:
        print("No results found.")

def cancel_shift_assign():
    a = 0
    for i in range(1,6):
        a += i
    print(a)

@frappe.whitelist()
def get_urc_to_ec(from_date):
    print("HI")
    urc = frappe.db.sql("""select biometric_pin,biometric_time,log_type,locationdevice_id,name from `tabUnregistered Employee Checkin` where date(biometric_time) = '%s'"""%(from_date),as_dict=True)
    for uc in urc:
        pin = uc.biometric_pin
        time = uc.biometric_time
        dev = uc.locationdevice_id
        typ = uc.log_type
        nam = uc.name
        if time != "":
            if frappe.db.exists('Employee',{'name':pin}):
                if frappe.db.exists('Employee Checkin',{'name':pin,"time":time}):
                    print("HI")
                else:
                    print("HII")
                    ec = frappe.new_doc('Employee Checkin')
                    ec.biometric_pin = pin
                    ec.employee = frappe.db.get_value('Employee',{'name':pin},['employee_number'])
                    ec.time = time
                    ec.device_id = dev
                    ec.log_type = typ
                    ec.save(ignore_permissions=True)
                    frappe.db.commit()
                    print("Created")
                    attendance = frappe.db.sql(""" delete from `tabUnregistered Employee Checkin` where name = '%s' """%(nam))
                    print("Deleted")       
            else:				
                print("hello")	
    return "ok"


from frappe.utils.background_jobs import enqueue
@frappe.whitelist()
def process_push_punch(from_date):
    enqueue(push_punch, queue='default', timeout=6000, event='enqueue_submit_schedule',from_date=from_date)


@frappe.whitelist()
def push_punch(from_date):
    from cgi import print_environ
    import mysql.connector
    import requests,json
    from datetime import date
    from datetime import time,datetime

    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="Pa55w0rd@",
    database="easytimepro"
    )

    # from_date = "2023-06-21"
    # to_date = "2023-07-26"

    # pre_date = add_days(from_date(),-1)  

    mycursor = mydb.cursor(dictionary=True)
    query = "SELECT  * FROM iclock_transaction where date(punch_time) = '%s' "%(from_date)
    mycursor.execute(query)
    attlog = mycursor.fetchall()
    if attlog:
        for a in attlog:
            print(len(attlog))
            url = "http://157.245.101.198/api/method/johoku.biometric_checkin.mark_checkin?employee=%s&time=%s&device_id=%s" % (a['emp_code'],a['punch_time'],a['terminal_alias'])
            headers = { 'Content-Type': 'application/json','Authorization': 'token b3df19e9615e0dc:b499d47b3041f94'}
            response = requests.request('GET',url,headers=headers,verify=False)
            res = json.loads(response.text)
            print(res)
            if res:
                if res['message'] == 'Checkin Marked':
                    mycursor = mydb.cursor()
                    sql = "UPDATE iclock_transaction SET checkin_marked = 1 WHERE id = %s " % a['id']
                    mycursor.execute(sql)
                    mydb.commit()  
    return 'ok' 


from frappe import _

# from frappe import _

# @frappe.whitelist()
# def validate_leave_application(doc, method):
# 	today = frappe.utils.getdate(frappe.utils.today())
# 	current_month = today.month
# 	current_year = today.year
                                                                                                                                       
# 	# Calculate payroll start and end dates based on the current month
# 	if current_month == 12:
# 		payroll_start_date = frappe.utils.getdate(f"21-12-{current_year}")
# 		payroll_end_date = frappe.utils.getdate(f"20-01-{current_year + 1}")
# 	else:
# 		payroll_start_date = frappe.utils.getdate(f"21-{current_month}-{current_year}")
# 		payroll_end_date = frappe.utils.getdate(f"20-{current_month + 1}-{current_year}")

# 	application_from_date = frappe.utils.getdate(doc.from_date)
# 	application_to_date = frappe.utils.getdate(doc.to_date)
    

# 	if (
# 		(payroll_start_date <= application_from_date <= payroll_end_date)
# 		and (application_from_date.day > 23 or application_to_date.day > 23)
# 	):
# 		frappe.throw(_(Permission Request on the 23rd of the month is not allowed."))

# 	if application_from_date > application_to_date:
# 		frappe.throw(_("From date should be before or equal to To date"))

# from frappe import _

# def validate_leave_application(doc, method):
# 	import datetime
    
# 	today = datetime.date.today()
# 	start_date = datetime.datetime.strptime(doc.from_date, "%Y-%m-%d").date()
    
# 	if today.day > 22 and start_date <= today:
# 		frappe.throw(_("Leave application is not allowed after the 22nd of the month."))




@frappe.whitelist()
def update_designation_from_staffing_plan(staffing):
    staff = frappe.get_all("Staffing Plan Detail",{'parent':staffing},['*'])
    return staff


@frappe.whitelist()
def delete_urc():
    urc = frappe.db.sql("""delete from `tabUnregistered Employee Checkin` """,as_dict = True)
    print(urc)
    
@frappe.whitelist()
def salary():
    emp=frappe.db.sql("""select * from `tabEmployee` where status='Active'""",as_dict=True)
    for e in emp:
        if not frappe.db.exists("""select * from `tabSalary Structure Assignment` where employee=%s"""%(e.name)):
            print(e.name)

@frappe.whitelist()
def inactive_employee(doc,method):
    if doc.status=="Active":
        if doc.relieving_date:
            throw(_("Please remove the relieving date for the Active Employee."))

@frappe.whitelist()
def update_employee_no(name,employee_number):
    emp = frappe.get_doc("Employee",name)
    emps=frappe.get_all("Employee",{"status":"Active"},['*'])
    for i in emps:
        if emp.employee_number == employee_number:
            pass
        elif i.employee_number == employee_number:
            frappe.throw(f"Employee Number already exists for {i.name}")
        else:
            frappe.db.set_value("Employee",name,"employee_number",employee_number)
            frappe.rename_doc("Employee", name, employee_number, force=1)
            return employee_number

@frappe.whitelist()
def leave_application_notify():
    staff = """
        <div style="text-align: center;">
            <h2 style="font-size: 16px;">Leave Application Report</h2>
        </div>
        <table style="border-collapse: collapse; width: 100%; border: 1px solid black; font-size: 10px;">
            <tr style="border: 1px solid black;">
                <th style="padding: 4px; border: 1px solid black;">S.No</th>
                <th style="padding: 4px; border: 1px solid black;">Employee</th>
                <th style="padding: 4px; border: 1px solid black;">Employee Name</th>
                <th style="padding: 4px; border: 1px solid black;">Department</th>
                <th style="padding: 4px; border: 1px solid black;">Document ID</th>
                <th style="padding: 4px; border: 1px solid black;">From date</th>
                <th style="padding: 4px; border: 1px solid black;">To Date</th>
                <th style="padding: 4px; border: 1px solid black;">Leave Type</th>
            </tr>
    """
    staff_hod = staff
    staff_md = staff
    staff_department = staff
    staff_director = staff


    hr = frappe.db.sql_list(
                """select distinct hr_approval from `tabEmployee`
                where status = 'Active' """,
            )
    
    count = frappe.db.count('Leave Application',{'workflow_state':'HR Pending','docstatus':0})
    if count != 0:
        for i in hr:
            hr_approver = frappe.get_all("Employee",{'status':'Active','hr_approval':i},['name'])
            for j in hr_approver:
                hr_app = frappe.get_all("Leave Application",{'employee':j.name},['employee','employee_name','department','name','from_date','to_date','leave_type','workflow_state'])
                for leave in hr_app:
                    idx = 1
                    if leave.workflow_state == 'HR Pending':
                        
                        if leave:
                            staff += """
                                <tr style="border: 1px solid black;">
                                    <td style="padding: 4px; border: 1px solid black;">{0}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{1}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{2}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{3}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{4}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{5}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{6}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{7}</td>
                                </tr>
                            """.format(idx, leave.employee, leave.employee_name, leave.department, leave.name or ' ',format_date(leave.from_date),format_date(leave.to_date), leave.leave_type or '')
                            idx += 1

        frappe.sendmail(
                        recipients=['jothi.m@groupteampro.com'],
                        subject='Leave Application Report',
                        message="""Dear Sir,<br><br>
                                Kindly Find the list of Leave Application waiting for your Approval:<br>{0}
                                """.format(staff)
                    )
            
    # hr = frappe.db.sql_list(
    #             """select distinct department_approval from `tabEmployee`
    #             where status = 'Active' """,
    #         )
    count1 = frappe.db.count('Leave Application',{'workflow_state':'Department Pending','docstatus':0})
    if count1 != 0:
        hr_app = frappe.get_all(
        "Leave Application",
        filters={'docstatus': ['!=', 2]},
        fields=['employee', 'employee_name', 'department', 'name', 'from_date', 'to_date', 'leave_type', 'workflow_state']
    )
        # for i in hr:
            # hr_approver = frappe.get_all("Employee",{'status':'Active','department_approval':i},['name'])
            # for j in hr_approver:
                # hr_app = frappe.get_all("Leave Application",{'employee':j.name},['employee','employee_name','department','name','from_date','to_date','leave_type','workflow_state'])
        for leave in hr_app:
            idx = 1
            if leave.workflow_state == 'Department Pending':
                # idx = 1
                if leave:
                    staff_department += """
                        <tr style="border: 1px solid black;">
                            <td style="padding: 4px; border: 1px solid black;">{0}</td>
                            <td style="padding: 4px; border: 1px solid black;">{1}</td>
                            <td style="padding: 4px; border: 1px solid black;">{2}</td>
                            <td style="padding: 4px; border: 1px solid black;">{3}</td>
                            <td style="padding: 4px; border: 1px solid black;">{4}</td>
                            <td style="padding: 4px; border: 1px solid black;">{5}</td>
                            <td style="padding: 4px; border: 1px solid black;">{6}</td>
                            <td style="padding: 4px; border: 1px solid black;">{7}</td>
                        </tr>
                    """.format(idx, leave.employee, leave.employee_name, leave.department, leave.name or ' ',format_date(leave.from_date),format_date(leave.to_date), leave.leave_type or '')
                    idx += 1

        frappe.sendmail(
                recipients=['jothi.m@groupteampro.com'],
                subject='Leave Application Report',
                message="""Dear Sir,<br><br>
                        Kindly Find the list of Leave Application waiting for your Approval:<br>{0}
                        """.format(staff_department)
            )
    # hr = frappe.db.sql_list(
    #             """select distinct md_approval from `tabEmployee`
    #             where status = 'Active' """,
    #         )
    count2 = frappe.db.count('Leave Application',{'workflow_state':'MD Pending','docstatus':0})
    if count2 != 0:
        # for i in hr:
            # if i:
                # hr_approver = frappe.get_all("Employee",{'status':'Active','md_approval':i},['name'])
                # for j in hr_approver:
                #     hr_app = frappe.get_all("Leave Application",{'employee':j.name},['employee','employee_name','department','name','from_date','to_date','leave_type','workflow_state'])
        hr_app = frappe.get_all(
        "Leave Application",
        filters={'docstatus': ['!=', 2]},
        fields=['employee', 'employee_name', 'department', 'name', 'from_date', 'to_date', 'leave_type', 'workflow_state']
    )
        for leave in hr_app:
            idx = 1
            if leave.workflow_state == 'MD Pending':
                
                staff_md += """
                    <tr style="border: 1px solid black;">
                        <td style="padding: 4px; border: 1px solid black;">{0}</td>
                        <td style="padding: 4px; border: 1px solid black;">{1}</td>
                        <td style="padding: 4px; border: 1px solid black;">{2}</td>
                        <td style="padding: 4px; border: 1px solid black;">{3}</td>
                        <td style="padding: 4px; border: 1px solid black;">{4}</td>
                        <td style="padding: 4px; border: 1px solid black;">{5}</td>
                        <td style="padding: 4px; border: 1px solid black;">{6}</td>
                        <td style="padding: 4px; border: 1px solid black;">{7}</td>
                    </tr>
                """.format(idx, leave.employee, leave.employee_name, leave.department, leave.name or ' ',format_date(leave.from_date),format_date(leave.to_date), leave.leave_type or '')
                idx += 1

        frappe.sendmail(
                    recipients=['jothi.m@groupteampro.com'],
                    subject='Leave Application Report',
                    message="""Dear Sir,<br><br>
                            Kindly Find the list of Leave Application waiting for your Approval:<br>{0}
                            """.format(staff_md)
                )
    hr_app = frappe.get_all("Leave Application",
                        filters={'docstatus': ['!=', 2]},
                        fields=['employee', 'employee_name', 'department', 'name', 'from_date', 'to_date', 'leave_type', 'workflow_state'])

    # hr_app = frappe.get_all("Leave Application",{'docstatus', '!=', 2},['employee','employee_name','department','name','from_date','to_date','leave_type','workflow_status'])
    count3 = frappe.db.count('Leave Application',{'workflow_state':'Director Pending','docstatus':0})
    if count3 != 0:
        for leave in hr_app:
            if leave.workflow_state == 'Director Pending':
                idx = 1
                staff_director += """
                    <tr style="border: 1px solid black;">
                        <td style="padding: 4px; border: 1px solid black;">{0}</td>
                        <td style="padding: 4px; border: 1px solid black;">{1}</td>
                        <td style="padding: 4px; border: 1px solid black;">{2}</td>
                        <td style="padding: 4px; border: 1px solid black;">{3}</td>
                        <td style="padding: 4px; border: 1px solid black;">{4}</td>
                        <td style="padding: 4px; border: 1px solid black;">{5}</td>
                        <td style="padding: 4px; border: 1px solid black;">{6}</td>
                        <td style="padding: 4px; border: 1px solid black;">{7}</td>
                    </tr>
                """.format(idx, leave.employee, leave.employee_name, leave.department, leave.name or ' ',format_date(leave.from_date),format_date(leave.to_date), leave.leave_type or '')
                idx += 1

        frappe.sendmail(
            recipients=['jothi.m@groupteampro.com'],
            subject='Leave Application Report',
            message="""Dear Sir,<br><br>
                    Kindly Find the list of Leave Application waiting for your Approval:<br>{0}
                    """.format(staff_director)
        )
    hr_app = frappe.get_all(
        "Leave Application",
        filters={'docstatus': ['!=', 2]},
        fields=['employee', 'employee_name', 'department', 'name', 'from_date', 'to_date', 'leave_type', 'workflow_state']
    )

    count5 = frappe.db.count('Leave Application', {'workflow_state': 'HOD Pending', 'docstatus': 0})
    hod_list_1, hod_list_2, hod_list_3, hod_list_4 = "", "", "", ""
    idx = 1
    if count5 != 0:
        for leave in hr_app:
            if leave.workflow_state == 'HOD Pending':
                row = """
                    <tr style="border: 1px solid black;">
                        <td style="padding: 4px; border: 1px solid black;">{0}</td>
                        <td style="padding: 4px; border: 1px solid black;">{1}</td>
                        <td style="padding: 4px; border: 1px solid black;">{2}</td>
                        <td style="padding: 4px; border: 1px solid black;">{3}</td>
                        <td style="padding: 4px; border: 1px solid black;">{4}</td>
                        <td style="padding: 4px; border: 1px solid black;">{5}</td>
                        <td style="padding: 4px; border: 1px solid black;">{6}</td>
                        <td style="padding: 4px; border: 1px solid black;">{7}</td>
                    </tr>
                """.format(idx, leave.employee, leave.employee_name, leave.department, leave.name or ' ',
                        format_date(leave.from_date), format_date(leave.to_date), leave.leave_type or '')

                if leave.department in ['PPC - JMPL', 'Purchase - JMPL', 'Sales - JMPL']:
                    hod_list_1 += row
                elif leave.department in ['Finance - JMPL', 'HR and GA - JMPL']:
                    hod_list_2 += row
                elif leave.department in ['Technical - JMPL', 'QUALITY - JMPL']:
                    hod_list_3 += row
                elif leave.department in ['Stores - JMPL', 'Dispatch - JMPL', 'Assembly Shop - JMPL', 'Machine Shop - JMPL', 'MAINTENANCE - JMPL', 'Utility - JMPL']:
                    hod_list_4 += row
                idx += 1
        multiple_hod_list = [hod_list_1, hod_list_2, hod_list_3, hod_list_4]
        for l in multiple_hod_list:
            if l: 
                frappe.sendmail(
                    recipients=['jothi.m@groupteampro.com'],
                    subject='Leave Application Report',
                    message="""Dear Sir,<br><br>
                            Kindly Find the list of Leave Applications waiting for your Approval:<br>{0}{1}""".format(staff_hod,l)
                )

    
    

@frappe.whitelist()
# def miss_punch_application_notify():
#     staff = """
#         <div style="text-align: center;">
#             <h2 style="font-size: 16px;">Miss Punch Application Report</h2>
#         </div>
#         <table style="border-collapse: collapse; width: 100%; border: 1px solid black; font-size: 10px;">
#             <tr style="border: 1px solid black;">
#                 <th style="padding: 4px; border: 1px solid black;">S.No</th>
#                 <th style="padding: 4px; border: 1px solid black;">Employee</th>
#                 <th style="padding: 4px; border: 1px solid black;">Date</th>
#                 <th style="padding: 4px; border: 1px solid black;">Department</th>
#                 <th style="padding: 4px; border: 1px solid black;">Document ID</th>
#                 <th style="padding: 4px; border: 1px solid black;">IN Time</th>
#                 <th style="padding: 4px; border: 1px solid black;">OUT Time</th>
#                 <th style="padding: 4px; border: 1px solid black;">Shift</th>
#             </tr>
#     """
#     hr = frappe.db.sql_list(
#                 """select distinct hr_approval from `tabEmployee`
#                 where status = 'Active' """,
#             )
#     count = frappe.db.count('Miss Punch Application', {'workflow_state': 'HR Pending','docstatus':0})
#     if count != 0:
#         for i in hr:
#             hr_approver = frappe.get_all("Employee",{'status':'Active','hr_approval':i},['name'])
#             for j in hr_approver:
#                 hr_app = frappe.get_all("Miss Punch Application",{'employee':j.name},['employee','date','department','name','in_tme','out_time','shift','workflow_state'])
#                 for leave in hr_app:
#                     if leave.workflow_state == 'HR Pending':
#                         idx = 1
#                         staff += """
#                             <tr style="border: 1px solid black;">
#                                 <td style="padding: 4px; border: 1px solid black;">{0}</td>
#                                 <td style="padding: 4px; border: 1px solid black;">{1}</td>
#                                 <td style="padding: 4px; border: 1px solid black;">{2}</td>
#                                 <td style="padding: 4px; border: 1px solid black;">{3}</td>
#                                 <td style="padding: 4px; border: 1px solid black;">{4}</td>
#                                 <td style="padding: 4px; border: 1px solid black;">{5}</td>
#                                 <td style="padding: 4px; border: 1px solid black;">{6}</td>
#                                 <td style="padding: 4px; border: 1px solid black;">{7}</td>
#                             </tr>
#                         """.format(idx, leave.employee, format_date(leave.date), leave.department, leave.name or ' ',leave.in_tme or ' ',leave.out_time or ' ', leave.shift_type or '')
#                         idx += 1

#         frappe.sendmail(
#                     recipients=['jothi.m@groupteampro.com'],
#                     subject='Miss Punch Application Report',
#                     message="""Dear Sir,<br><br>
#                             Kindly Find the list of Miss Punch Application waiting for your Approval:<br>{0}
#                             """.format(staff)
#                 )
    
#     hr = frappe.db.sql_list(
#                 """select distinct department_approval from `tabEmployee`
#                 where status = 'Active' """,
#             )
#     count1 = frappe.db.count('Miss Punch Application', {'workflow_state': 'Department Pending','docstatus':0})
#     if count1 != 0:
#         for i in hr:
#             hr_approver = frappe.get_all("Employee",{'status':'Active','department_approval':i},['name'])
#             for j in hr_approver:
#                 hr_app = frappe.get_all("Miss Punch Application",{'employee':j.name},['employee','date','department','name','in_tme','out_time','shift','workflow_state'])
#                 for leave in hr_app:
#                     if leave.workflow_state == 'Department Pending':
#                         idx = 1
#                         staff += """
#                             <tr style="border: 1px solid black;">
#                                 <td style="padding: 4px; border: 1px solid black;">{0}</td>
#                                 <td style="padding: 4px; border: 1px solid black;">{1}</td>
#                                 <td style="padding: 4px; border: 1px solid black;">{2}</td>
#                                 <td style="padding: 4px; border: 1px solid black;">{3}</td>
#                                 <td style="padding: 4px; border: 1px solid black;">{4}</td>
#                                 <td style="padding: 4px; border: 1px solid black;">{5}</td>
#                                 <td style="padding: 4px; border: 1px solid black;">{6}</td>
#                                 <td style="padding: 4px; border: 1px solid black;">{7}</td>
#                             </tr>
#                         """.format(idx, leave.employee, format_date(leave.date), leave.department, leave.name or ' ',leave.in_tme or ' ',leave.out_time or ' ', leave.shift_type or '')
#                         idx += 1

#         frappe.sendmail(
#                         recipients=['jothi.m@groupteampro.com'],
#                         subject='Miss Punch Application Report',
#                         message="""Dear Sir,<br><br>
#                                 Kindly Find the list of Miss Punch Application waiting for your Approval:<br>{0}
#                                 """.format(staff)
#                     )
#     hr = frappe.db.sql_list(
#                 """select distinct department_approval from `tabEmployee`
#                 where status = 'Active' """,
#             )
#     count2 = frappe.db.count('Miss Punch Application', {'workflow_state': 'Department Pending','docstatus':0})
#     if count2 != 0:
#         for i in hr:
#             hr_approver = frappe.get_all("Employee",{'status':'Active','department_approval':i},['name'])
#             for j in hr_approver:
#                 hr_app = frappe.get_all("Miss Punch Application",{'employee':j.name},['employee','date','department','name','in_tme','out_time','shift','workflow_state'])
#                 for leave in hr_app:
#                     if leave.workflow_state == 'Department Pending':
#                         idx = 1
#                         staff += """
#                                 <tr style="border: 1px solid black;">
#                                     <td style="padding: 4px; border: 1px solid black;">{0}</td>
#                                     <td style="padding: 4px; border: 1px solid black;">{1}</td>
#                                     <td style="padding: 4px; border: 1px solid black;">{2}</td>
#                                     <td style="padding: 4px; border: 1px solid black;">{3}</td>
#                                     <td style="padding: 4px; border: 1px solid black;">{4}</td>
#                                     <td style="padding: 4px; border: 1px solid black;">{5}</td>
#                                     <td style="padding: 4px; border: 1px solid black;">{6}</td>
#                                     <td style="padding: 4px; border: 1px solid black;">{7}</td>
#                                 </tr>
#                         """.format(idx, leave.employee, format_date(leave.date), leave.department, leave.name or ' ',leave.in_tme or ' ',leave.out_time or ' ', leave.shift_type or '')
#                         idx += 1

#         frappe.sendmail(
#                 recipients=['jothi.m@groupteampro.com'],
#                 subject='Miss Punch Application Report',
#                 message="""Dear Sir,<br><br>
#                         Kindly Find the list of Miss Punch Application waiting for your Approval:<br>{0}
#                         """.format(staff)
#             )
    
#     hr_app = frappe.get_all("Miss Punch Application",
#                         filters={'docstatus': ['!=', 2]},
#                         fields=['employee', 'date', 'department', 'name', 'in_time', 'out_time', 'shift', 'workflow_state'])
#     count3 = frappe.db.count('Miss Punch Application', {'workflow_state': 'Department Pending','docstatus':0})
#     if count3 != 0:
#         for leave in hr_app:
#             if leave.workflow_state == 'Department Pending':
#                 idx = 1
#                 staff += """
#                     <tr style="border: 1px solid black;">
#                         <td style="padding: 4px; border: 1px solid black;">{0}</td>
#                         <td style="padding: 4px; border: 1px solid black;">{1}</td>
#                         <td style="padding: 4px; border: 1px solid black;">{2}</td>
#                         <td style="padding: 4px; border: 1px solid black;">{3}</td>
#                         <td style="padding: 4px; border: 1px solid black;">{4}</td>
#                         <td style="padding: 4px; border: 1px solid black;">{5}</td>
#                         <td style="padding: 4px; border: 1px solid black;">{6}</td>
#                         <td style="padding: 4px; border: 1px solid black;">{7}</td>
#                     </tr>
#                         """.format(idx, leave.employee, format_date(leave.date), leave.department, leave.name or ' ',leave.in_tme or ' ',leave.out_time or ' ', leave.shift_type or '')
#                 idx += 1

#         frappe.sendmail(
#             recipients=['jothi.m@groupteampro.com'],
#             subject='Miss Punch Application Report',
#             message="""Dear Sir,<br><br>
#                     Kindly Find the list of Miss Punch Application waiting for your Approval:<br>{0}
#                     """.format(staff)
#         )
#     hr_app = frappe.get_all("Miss Punch Application",
#                         filters={'docstatus': ['!=', 2]},
#                         fields=['employee', 'date', 'department', 'name', 'in_time', 'out_time', 'shift', 'workflow_state'])

#     # id = 1
#     # hr_app = frappe.get_all("Leave Application",{'docstatus', '!=', 2},['employee','employee_name','department','name','from_date','to_date','leave_type','workflow_status'])
#     count4 = frappe.db.count('Miss Punch Application', {'workflow_state': 'MD Pending','docstatus':0})
#     if count4 != 0:
#         for leave in hr_app:
#             if leave.workflow_state == 'MD Pending':
#                 idx = 1
#                 staff += """
#                     <tr style="border: 1px solid black;">
#                         <td style="padding: 4px; border: 1px solid black;">{0}</td>
#                         <td style="padding: 4px; border: 1px solid black;">{1}</td>
#                         <td style="padding: 4px; border: 1px solid black;">{2}</td>
#                         <td style="padding: 4px; border: 1px solid black;">{3}</td>
#                         <td style="padding: 4px; border: 1px solid black;">{4}</td>
#                         <td style="padding: 4px; border: 1px solid black;">{5}</td>
#                         <td style="padding: 4px; border: 1px solid black;">{6}</td>
#                         <td style="padding: 4px; border: 1px solid black;">{7}</td>
#                     </tr>
#                         """.format(idx, leave.employee, format_date(leave.date), leave.department, leave.name or ' ',leave.in_tme or ' ',leave.out_time or ' ', leave.shift_type or '')
#                 idx += 1
#         # if id !=0:
#         frappe.sendmail(
#                     recipients=['jothi.m@groupteampro.com'],
#                     subject='Miss Punch Application Report',
#                     message="""Dear Sir,<br><br>
#                             Kindly Find the list of Miss Punch Application waiting for your Approval:<br>{0}
#                             """.format(staff)
#                 )
    
   

#     hr_app = frappe.get_all(
#     "Miss Punch Application",
#     filters={'docstatus': ['!=', 2]},  # Ensure that 2 correctly represents cancelled documents
#     fields=['employee', 'date', 'department', 'name', 'in_time', 'out_time', 'shift', 'workflow_state'])
#     count5 = frappe.db.count('Miss Punch Application', {'workflow_state': 'HOD Pending','docstatus':0})
#     if count5 != 0:
#         for leave in hr_app:
#             if leave.department == 'PPC - JMPL' or leave.department == 'Purchase - JMPL' or leave.department == 'Sales - JMPL':
#                 if leave.workflow_state == 'HOD Pending':
#                     idx = 1
#                     staff += """
#                         <tr style="border: 1px solid black;">
#                             <td style="padding: 4px; border: 1px solid black;">{0}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{1}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{2}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{3}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{4}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{5}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{6}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{7}</td>
#                         </tr>
#                         """.format(idx, leave.employee, format_date(leave.date), leave.department, leave.name or ' ',leave.in_tme or ' ',leave.out_time or ' ', leave.shift_type or '')
#                     idx += 1

#         frappe.sendmail(
#                 recipients=['jothi.m@groupteampro.com'],
#                 subject='Miss Punch Application Report',
#                 message="""Dear Sir,<br><br>
#                         Kindly Find the list of Miss Punch Application waiting for your Approval:<br>{0}
#                         """.format(staff)
#             )
#     hr_app = frappe.get_all("Miss Punch Application",
#                         filters={'docstatus': ['!=', 2]},
#                         fields=['employee', 'date', 'department', 'name', 'in_time', 'out_time', 'shift', 'workflow_state'])
#     count6 = frappe.db.count('Miss Punch Application', {'workflow_state': 'HOD Pending','docstatus':0})
#     if count6 != 0:
#         for leave in hr_app:
#             if leave.department == 'Finance - JMPL' or leave.department == 'HR and GA - JMPL':
#                 if leave.workflow_state == 'HOD Pending':
#                     idx = 1
#                     staff += """
#                         <tr style="border: 1px solid black;">
#                             <td style="padding: 4px; border: 1px solid black;">{0}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{1}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{2}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{3}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{4}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{5}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{6}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{7}</td>
#                         </tr>
#                         """.format(idx, leave.employee, format_date(leave.date), leave.department, leave.name or ' ',leave.in_tme or ' ',leave.out_time or ' ', leave.shift_type or '')
#                     idx += 1
#         frappe.sendmail(
#             recipients='jothi.m@groupteampro.com',
#             subject='Miss Punch Application Report',
#             message="""Dear Sir,<br><br>
#                     Kindly Find the list of Miss Punch Application waiting for your Approval:<br>{0}
#                     """.format(staff)
#         )
    
#     hr_app = frappe.get_all("Miss Punch Application",
#                         filters={'docstatus': ['!=', 2]},
#                         fields=['employee', 'date', 'department', 'name', 'in_time', 'out_time', 'shift', 'workflow_state'])
#     count7 = frappe.db.count('Miss Punch Application', {'workflow_state': 'HOD Pending','docstatus':0})
#     if count7 != 0:
#         for leave in hr_app:
#             if leave.department == 'Technical - JMPL' or leave.department == 'QUALITY - JMPL':
#                 if leave.workflow_state == 'HOD Pending':
#                     idx = 1
#                     staff += """
#                         <tr style="border: 1px solid black;">
#                             <td style="padding: 4px; border: 1px solid black;">{0}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{1}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{2}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{3}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{4}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{5}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{6}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{7}</td>
#                         </tr>
#                         """.format(idx, leave.employee, format_date(leave.date), leave.department, leave.name or ' ',leave.in_tme or ' ',leave.out_time or ' ', leave.shift_type or '')
#                     idx += 1
#         frappe.sendmail(
#             recipients='jothi.m@groupteampro.com',
#             subject='Leave Application Report',
#             message="""Dear Sir,<br><br>
#                     Kindly Find the list of Miss Punch Application waiting for your Approval:<br>{0}
#                     """.format(staff)
#         )
#     hr_app = frappe.get_all("Miss Punch Application",
#                         filters={'docstatus': ['!=', 2]},
#                         fields=['employee', 'date', 'department', 'name', 'in_time', 'out_time', 'shift', 'workflow_state'])
#     count8 = frappe.db.count('Miss Punch Application', {'workflow_state': 'HOD Pending','docstatus':0})
#     if count8 != 0:
#         for leave in hr_app:
#             if leave.department == 'Stores - JMPL' or leave.department == 'Dispatch - JMPL' or leave.department == 'Assembly Shop - JMPL' or leave.department == 'Machine Shop - JMPL' or leave.department == 'MAINTENANCE - JMPL' or leave.department == 'Utility - JMPL':
#                 if leave.workflow_state == 'HOD Pending':
#                     idx = 1
#                     staff += """
#                         <tr style="border: 1px solid black;">
#                             <td style="padding: 4px; border: 1px solid black;">{0}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{1}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{2}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{3}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{4}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{5}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{6}</td>
#                             <td style="padding: 4px; border: 1px solid black;">{7}</td>
#                         </tr>
#                         """.format(idx, leave.employee, format_date(leave.date), leave.department, leave.name or ' ',leave.in_tme or ' ',leave.out_time or ' ', leave.shift_type or '')
            
#                     idx += 1
#         frappe.sendmail(
#             subject='Miss Punch Application Report',
#             recipients='jothi.m@groupteampro.com',
#             message="""Dear Sir,<br><br>
#                     Kindly Find the list of Miss Punch Application waiting for your Approval:<br>{0}
#                     """.format(staff)
#         )	


@frappe.whitelist()
def permission_request_notify():
    staff = """
        <div style="text-align: center;">
            <h2 style="font-size: 16px;"Permission Request Report</h2>
        </div>
        <table style="border-collapse: collapse; width: 100%; border: 1px solid black; font-size: 10px;">
            <tr style="border: 1px solid black;">
                <th style="padding: 4px; border: 1px solid black;">S.No</th>
                <th style="padding: 4px; border: 1px solid black;">Employee</th>
                <th style="padding: 4px; border: 1px solid black;">Employee Name</th>
                <th style="padding: 4px; border: 1px solid black;">Department</th>
                <th style="padding: 4px; border: 1px solid black;">Document ID</th>
                <th style="padding: 4px; border: 1px solid black;">Permissions Date</th>
                <th style="padding: 4px; border: 1px solid black;">Session</th>
                <th style="padding: 4px; border: 1px solid black;">Permission hour</th>
            </tr>
    """
    staff_hod = staff
    staff_md = staff
    staff_department = staff
    staff_director = staff


    hr = frappe.db.sql_list(
                """select distinct hr_approval from `tabEmployee`
                where status = 'Active' """,
            )
    
    count = frappe.db.count('Permission Request',{'workflow_state':'HR Pending','docstatus':0})
    if count != 0:
        for i in hr:
            hr_approver = frappe.get_all("Employee",{'status':'Active','hr_approval':i},['name'])
            for j in hr_approver:
                hr_app = frappe.get_all("Permission Request",{'employee_id':j.name},['employee_id','employee_name','department','name','permission_date','session','permission_hour','workflow_state'])
                for leave in hr_app:
                    idx = 1
                    if leave.workflow_state == 'HR Pending':
                        
                        if leave:
                            staff += """
                                <tr style="border: 1px solid black;">
                                    <td style="padding: 4px; border: 1px solid black;">{0}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{1}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{2}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{3}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{4}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{5}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{6}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{7}</td>
                                </tr>
                            """.format(idx, leave.employee_id, leave.employee_name, leave.department, leave.name or ' ',
                        format_date(leave.attendance_date), leave.session, leave.permission_hour or '')
                            idx += 1

        frappe.sendmail(
                        recipients=['jothi.m@groupteampro.com'],
                        subject='Permission Request Report',
                        message="""Dear Sir,<br><br>
                                Kindly Find the list of Permission Request waiting for your Approval:<br>{0}
                                """.format(staff)
                    )
            
    # hr = frappe.db.sql_list(
    #             """select distinct department_approval from `tabEmployee`
    #             where status = 'Active' """,
    #         )
    count1 = frappe.db.count('Permission Request',{'workflow_state':'Department Pending','docstatus':0})
    if count1 != 0:
        hr_app = frappe.get_all(
        "Permission Request",
        filters={'docstatus': ['!=', 2]},
        fields=['employee_id', 'employee_name', 'department', 'name', 'permission_date', 'session', 'permission_hour', 'workflow_state']
    )
        # for i in hr:
            # hr_approver = frappe.get_all("Employee",{'status':'Active','department_approval':i},['name'])
            # for j in hr_approver:
                # hr_app = frappe.get_all(Permission Request",{'employee':j.name},['employee','employee_name','department','name','from_date','to_date','leave_type','workflow_state'])
        for leave in hr_app:
            idx = 1
            if leave.workflow_state == 'Department Pending':
                # idx = 1
                if leave:
                    staff_department += """
                        <tr style="border: 1px solid black;">
                            <td style="padding: 4px; border: 1px solid black;">{0}</td>
                            <td style="padding: 4px; border: 1px solid black;">{1}</td>
                            <td style="padding: 4px; border: 1px solid black;">{2}</td>
                            <td style="padding: 4px; border: 1px solid black;">{3}</td>
                            <td style="padding: 4px; border: 1px solid black;">{4}</td>
                            <td style="padding: 4px; border: 1px solid black;">{5}</td>
                            <td style="padding: 4px; border: 1px solid black;">{6}</td>
                            <td style="padding: 4px; border: 1px solid black;">{7}</td>
                        </tr>
                    """.format(idx, leave.employee_id, leave.employee_name, leave.department, leave.name or ' ',
                        format_date(leave.attendance_date), leave.session, leave.permission_hour or '')
                    idx += 1

        frappe.sendmail(
                recipients=['jothi.m@groupteampro.com'],
                subject='Permission Request Report',
                message="""Dear Sir,<br><br>
                        Kindly Find the list of Permission Request waiting for your Approval:<br>{0}
                        """.format(staff_department)
            )
    # hr = frappe.db.sql_list(
    #             """select distinct md_approval from `tabEmployee`
    #             where status = 'Active' """,
    #         )
    count2 = frappe.db.count('Permission Request',{'workflow_state':'MD Pending','docstatus':0})
    if count2 != 0:
        # for i in hr:
            # if i:
                # hr_approver = frappe.get_all("Employee",{'status':'Active','md_approval':i},['name'])
                # for j in hr_approver:
                #     hr_app = frappe.get_all(Permission Request",{'employee':j.name},['employee','employee_name','department','name','from_date','to_date','leave_type','workflow_state'])
        hr_app = frappe.get_all(
        "Permission Request",
        filters={'docstatus': ['!=', 2]},
        fields=['employee_id', 'employee_name', 'department', 'name', 'permission_date', 'session', 'permission_hour', 'workflow_state']
    )
        for leave in hr_app:
            idx = 1
            if leave.workflow_state == 'MD Pending':
                
                staff_md += """
                    <tr style="border: 1px solid black;">
                        <td style="padding: 4px; border: 1px solid black;">{0}</td>
                        <td style="padding: 4px; border: 1px solid black;">{1}</td>
                        <td style="padding: 4px; border: 1px solid black;">{2}</td>
                        <td style="padding: 4px; border: 1px solid black;">{3}</td>
                        <td style="padding: 4px; border: 1px solid black;">{4}</td>
                        <td style="padding: 4px; border: 1px solid black;">{5}</td>
                        <td style="padding: 4px; border: 1px solid black;">{6}</td>
                        <td style="padding: 4px; border: 1px solid black;">{7}</td>
                    </tr>
                """.format(idx, leave.employee_id, leave.employee_name, leave.department, leave.name or ' ',
                        format_date(leave.attendance_date), leave.session, leave.permission_hour or '')
                idx += 1

        frappe.sendmail(
                    recipients=['jothi.m@groupteampro.com'],
                    subject='Permission Request Report',
                    message="""Dear Sir,<br><br>
                            Kindly Find the list ofPermission Request waiting for your Approval:<br>{0}
                            """.format(staff_md)
                )
    hr_app = frappe.get_all("Permission Request",
                        filters={'docstatus': ['!=', 2]},
                        fields=['employee_id', 'employee_name', 'department', 'name', 'permission_date', 'session', 'permission_hour', 'workflow_state'])

    # hr_app = frappe.get_all(Permission Request",{'docstatus', '!=', 2},['employee','employee_name','department','name','from_date','to_date','leave_type','workflow_status'])
    count3 = frappe.db.count('Permission Request',{'workflow_state':'Director Pending','docstatus':0})
    if count3 != 0:
        for leave in hr_app:
            idx = 1
            if leave.workflow_state == 'Director Pending':
                # idx = 1
                staff_director += """
                    <tr style="border: 1px solid black;">
                        <td style="padding: 4px; border: 1px solid black;">{0}</td>
                        <td style="padding: 4px; border: 1px solid black;">{1}</td>
                        <td style="padding: 4px; border: 1px solid black;">{2}</td>
                        <td style="padding: 4px; border: 1px solid black;">{3}</td>
                        <td style="padding: 4px; border: 1px solid black;">{4}</td>
                        <td style="padding: 4px; border: 1px solid black;">{5}</td>
                        <td style="padding: 4px; border: 1px solid black;">{6}</td>
                        <td style="padding: 4px; border: 1px solid black;">{7}</td>
                    </tr>
                """.format(idx, leave.employee_id, leave.employee_name, leave.department, leave.name or ' ',
                        format_date(leave.attendance_date), leave.session, leave.permission_hour or '')
                idx += 1

        frappe.sendmail(
            recipients=['jothi.m@groupteampro.com'],
            subject='Permission Request Report',
            message="""Dear Sir,<br><br>
                    Kindly Find the list ofPermission Request waiting for your Approval:<br>{0}
                    """.format(staff_director)
        )
    hr_app = frappe.get_all(
        "Permission Request",
        filters={'docstatus': ['!=', 2]},
        fields=['employee_id', 'employee_name', 'department', 'name', 'permission_date', 'session', 'permission_hour', 'workflow_state']
    )

    count5 = frappe.db.count('Permission Request', {'workflow_state': 'HOD Pending', 'docstatus': 0})
    hod_list_1, hod_list_2, hod_list_3, hod_list_4 = "", "", "", ""
    idx = 1
    if count5 != 0:
        for leave in hr_app:
            if leave.workflow_state == 'HOD Pending':
                row = """
                    <tr style="border: 1px solid black;">
                        <td style="padding: 4px; border: 1px solid black;">{0}</td>
                        <td style="padding: 4px; border: 1px solid black;">{1}</td>
                        <td style="padding: 4px; border: 1px solid black;">{2}</td>
                        <td style="padding: 4px; border: 1px solid black;">{3}</td>
                        <td style="padding: 4px; border: 1px solid black;">{4}</td>
                        <td style="padding: 4px; border: 1px solid black;">{5}</td>
                        <td style="padding: 4px; border: 1px solid black;">{6}</td>
                        <td style="padding: 4px; border: 1px solid black;">{7}</td>
                    </tr>
                """.format(idx, leave.employee_id, leave.employee_name, leave.department, leave.name or ' ',
                        format_date(leave.attendance_date), leave.session, leave.permission_hour or '')

                if leave.department in ['PPC - JMPL', 'Purchase - JMPL', 'Sales - JMPL']:
                    hod_list_1 += row
                elif leave.department in ['Finance - JMPL', 'HR and GA - JMPL']:
                    hod_list_2 += row
                elif leave.department in ['Technical - JMPL', 'QUALITY - JMPL']:
                    hod_list_3 += row
                # elif leave.department in ['Stores - JMPL', 'Dispatch - JMPL', 'Assembly Shop - JMPL', 'Machine Shop - JMPL', 'MAINTENANCE - JMPL', 'Utility - JMPL']:
                else:
                    hod_list_4 += row
                idx += 1
        multiple_hod_list = [hod_list_1, hod_list_2, hod_list_3, hod_list_4]
        for l in multiple_hod_list:
            if l: 
                frappe.sendmail(
                    recipients=['jothi.m@groupteampro.com'],
                    subject='Permission Request Report',
                    message="""Dear Sir,<br><br>
                            Kindly Find the list of Permission Request waiting for your Approval:<br>{0}{1}""".format(staff_hod,l)
                )
        
        
@frappe.whitelist()
def overtime_request_notify():
    staff = """
        <div style="text-align: center;">
            <h2 style="font-size: 16px;"Overtime Request Report</h2>
        </div>
        <table style="border-collapse: collapse; width: 100%; border: 1px solid black; font-size: 10px;">
            <tr style="border: 1px solid black;">
                <th style="padding: 4px; border: 1px solid black;">S.No</th>
                <th style="padding: 4px; border: 1px solid black;">Employee</th>
                <th style="padding: 4px; border: 1px solid black;">Employee Name</th>
                <th style="padding: 4px; border: 1px solid black;">Department</th>
                <th style="padding: 4px; border: 1px solid black;">Document ID</th>
                <th style="padding: 4px; border: 1px solid black;">OT Date</th>
                <th style="padding: 4px; border: 1px solid black;">From Time</th>
                <th style="padding: 4px; border: 1px solid black;">To Time</th>
                <th style="padding: 4px; border: 1px solid black;">Overtime Hours</th>
            </tr>
    """
    staff_hod = staff
    staff_md = staff
    staff_department = staff
    staff_director = staff


    hr = frappe.db.sql_list(
                """select distinct hr_approval from `tabEmployee`
                where status = 'Active' """,
            )
    
    count = frappe.db.count('Overtime Request',{'workflow_state':'HR Pending','docstatus':0})
    if count != 0:
        for i in hr:
            hr_approver = frappe.get_all("Employee",{'status':'Active','hr_approval':i},['name'])
            for j in hr_approver:
                hr_app = frappe.get_all("Overtime Request",{'employee':j.name},['employee','employee_name','department','name','ot_date','from_time','to_time','workflow_state','ot_hours'])
                for leave in hr_app:
                    idx = 1
                    if leave.workflow_state == 'HR Pending':
                        
                        if leave:
                            staff += """
                                <tr style="border: 1px solid black;">
                                    <td style="padding: 4px; border: 1px solid black;">{0}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{1}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{2}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{3}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{4}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{5}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{6}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{7}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{9}</td>
                                </tr>
                            """.format(idx, leave.employee_id, leave.employee_name, leave.department, leave.name or ' ',
                        format_date(leave.ot_date), leave.from_time, leave.to_time or '')
                            idx += 1

        frappe.sendmail(
                        recipients=['jothi.m@groupteampro.com'],
                        subject='Overtime Request Report',
                        message="""Dear Sir,<br><br>
                                Kindly Find the list of Overtime Request waiting for your Approval:<br>{0}
                                """.format(staff)
                    )
            
    # hr = frappe.db.sql_list(
    #             """select distinct department_approval from `tabEmployee`
    #             where status = 'Active' """,
    #         )
    count1 = frappe.db.count('Overtime Request',{'workflow_state':'Department Pending','docstatus':0})
    if count1 != 0:
        hr_app = frappe.get_all(
        "Overtime Request",
        filters={'docstatus': ['!=', 2]},
        fields=['employee', 'employee_name', 'department', 'name', 'ot_date', 'from_time', 'to_time', 'workflow_state','ot_hours']
    )
        # for i in hr:
            # hr_approver = frappe.get_all("Employee",{'status':'Active','department_approval':i},['name'])
            # for j in hr_approver:
                # hr_app = frappe.get_all(Overtime Request",{'employee':j.name},['employee','employee_name','department','name','from_date','to_date','leave_type','workflow_state'])
        for leave in hr_app:
            idx = 1
            if leave.workflow_state == 'Department Pending':
                # idx = 1
                if leave:
                    staff_department += """
                        <tr style="border: 1px solid black;">
                            <td style="padding: 4px; border: 1px solid black;">{0}</td>
                            <td style="padding: 4px; border: 1px solid black;">{1}</td>
                            <td style="padding: 4px; border: 1px solid black;">{2}</td>
                            <td style="padding: 4px; border: 1px solid black;">{3}</td>
                            <td style="padding: 4px; border: 1px solid black;">{4}</td>
                            <td style="padding: 4px; border: 1px solid black;">{5}</td>
                            <td style="padding: 4px; border: 1px solid black;">{6}</td>
                            <td style="padding: 4px; border: 1px solid black;">{7}</td>
                            <td style="padding: 4px; border: 1px solid black;">{9}</td>
                        </tr>
                    """.format(idx, leave.employee, leave.employee_name, leave.department, leave.name or ' ',
                        format_date(leave.ot_date), leave.from_time, leave.to_time or '')
                    idx += 1

        frappe.sendmail(
                recipients=['jothi.m@groupteampro.com'],
                subject='Overtime Request Report',
                message="""Dear Sir,<br><br>
                        Kindly Find the list of Overtime Request waiting for your Approval:<br>{0}
                        """.format(staff_department)
            )
    # hr = frappe.db.sql_list(
    #             """select distinct md_approval from `tabEmployee`
    #             where status = 'Active' """,
    #         )
    count2 = frappe.db.count('Overtime Request',{'workflow_state':'MD Pending','docstatus':0})
    if count2 != 0:
        # for i in hr:
            # if i:
                # hr_approver = frappe.get_all("Employee",{'status':'Active','md_approval':i},['name'])
                # for j in hr_approver:
                #     hr_app = frappe.get_all(Permission Request",{'employee':j.name},['employee','employee_name','department','name','from_date','to_date','leave_type','workflow_state'])
        hr_app = frappe.get_all(
        "Overtime Request",
        filters={'docstatus': ['!=', 2]},
        fields=['employee', 'employee_name', 'department', 'name', 'ot_date', 'from_time', 'to_time', 'workflow_state','ot_hours']
    )
        for leave in hr_app:
            idx = 1
            if leave.workflow_state == 'MD Pending':
                
                staff_md += """
                    <tr style="border: 1px solid black;">
                        <td style="padding: 4px; border: 1px solid black;">{0}</td>
                        <td style="padding: 4px; border: 1px solid black;">{1}</td>
                        <td style="padding: 4px; border: 1px solid black;">{2}</td>
                        <td style="padding: 4px; border: 1px solid black;">{3}</td>
                        <td style="padding: 4px; border: 1px solid black;">{4}</td>
                        <td style="padding: 4px; border: 1px solid black;">{5}</td>
                        <td style="padding: 4px; border: 1px solid black;">{6}</td>
                        <td style="padding: 4px; border: 1px solid black;">{7}</td>
                        <td style="padding: 4px; border: 1px solid black;">{9}</td>
                    </tr>
                """.format(idx, leave.employee, leave.employee_name, leave.department, leave.name or ' ',
                        format_date(leave.ot_date), leave.from_time, leave.to_time or '')
                idx += 1

        frappe.sendmail(
                    recipients=['jothi.m@groupteampro.com'],
                    subject='Overtime Request Report',
                    message="""Dear Sir,<br><br>
                            Kindly Find the list of Overtime Request waiting for your Approval:<br>{0}
                            """.format(staff_md)
                )
    hr_app = frappe.get_all("Overtime Request",
                        filters={'docstatus': ['!=', 2]},
                        fields=['employee', 'employee_name', 'department', 'name', 'ot_date', 'from_time', 'to_time', 'workflow_state','ot_hours'])

    # hr_app = frappe.get_all("Overtime Request",{'docstatus', '!=', 2},['employee','employee_name','department','name','from_date','to_date','leave_type','workflow_status'])
    count3 = frappe.db.count('Overtime Request',{'workflow_state':'Director Pending','docstatus':0})
    if count3 != 0:
        for leave in hr_app:
            idx = 1
            if leave.workflow_state == 'Director Pending':
                # idx = 1
                staff_director += """
                    <tr style="border: 1px solid black;">
                        <td style="padding: 4px; border: 1px solid black;">{0}</td>
                        <td style="padding: 4px; border: 1px solid black;">{1}</td>
                        <td style="padding: 4px; border: 1px solid black;">{2}</td>
                        <td style="padding: 4px; border: 1px solid black;">{3}</td>
                        <td style="padding: 4px; border: 1px solid black;">{4}</td>
                        <td style="padding: 4px; border: 1px solid black;">{5}</td>
                        <td style="padding: 4px; border: 1px solid black;">{6}</td>
                        <td style="padding: 4px; border: 1px solid black;">{7}</td>
                        <td style="padding: 4px; border: 1px solid black;">{9}</td>
                    </tr>
               """.format(idx, leave.employee, leave.employee_name, leave.department, leave.name or ' ',
                        format_date(leave.ot_date), leave.from_time, leave.to_time or '')
                idx += 1

        frappe.sendmail(
            recipients=['jothi.m@groupteampro.com'],
            subject='Overtime Request Report',
            message="""Dear Sir,<br><br>
                    Kindly Find the list of Overtime Request waiting for your Approval:<br>{0}
                    """.format(staff_director)
        )
    hr_app = frappe.get_all(
        "Overtime Request",
        filters={'docstatus': ['!=', 2]},
        fields=['employee', 'employee_name', 'department', 'name', 'ot_date', 'from_time', 'to_time', 'workflow_state','ot_hours']
    )

    count5 = frappe.db.count('Overtime Request', {'workflow_state': 'HOD Pending', 'docstatus': 0})
    hod_list_1, hod_list_2, hod_list_3, hod_list_4 = "", "", "", ""
    idx = 1
    if count5 != 0:
        for leave in hr_app:
            if leave.workflow_state == 'HOD Pending':
                row = """
                    <tr style="border: 1px solid black;">
                        <td style="padding: 4px; border: 1px solid black;">{0}</td>
                        <td style="padding: 4px; border: 1px solid black;">{1}</td>
                        <td style="padding: 4px; border: 1px solid black;">{2}</td>
                        <td style="padding: 4px; border: 1px solid black;">{3}</td>
                        <td style="padding: 4px; border: 1px solid black;">{4}</td>
                        <td style="padding: 4px; border: 1px solid black;">{5}</td>
                        <td style="padding: 4px; border: 1px solid black;">{6}</td>
                        <td style="padding: 4px; border: 1px solid black;">{7}</td>
                        <td style="padding: 4px; border: 1px solid black;">{9}</td>
                    </tr>
                """.format(idx, leave.employee, leave.employee_name, leave.department, leave.name or ' ',
                        format_date(leave.ot_date), leave.from_time, leave.to_time or '')
                if leave.department in ['PPC - JMPL', 'Purchase - JMPL', 'Sales - JMPL']:
                    hod_list_1 += row
                elif leave.department in ['Finance - JMPL', 'HR and GA - JMPL']:
                    hod_list_2 += row
                elif leave.department in ['Technical - JMPL', 'QUALITY - JMPL']:
                    hod_list_3 += row
                # elif leave.department in ['Stores - JMPL', 'Dispatch - JMPL', 'Assembly Shop - JMPL', 'Machine Shop - JMPL', 'MAINTENANCE - JMPL', 'Utility - JMPL']:
                else:
                    hod_list_4 += row
                idx += 1
        multiple_hod_list = [hod_list_1, hod_list_2, hod_list_3, hod_list_4]
        for l in multiple_hod_list:
            if l: 
                frappe.sendmail(
                    recipients=['jothi.m@groupteampro.com'],
                    subject='Overtime Request Report',
                    message="""Dear Sir,<br><br>
                            Kindly Find the list of Overtime Request waiting for your Approval:<br>{0}{1}""".format(staff_hod,l)
                )

@frappe.whitelist()
def on_duty_application_notify():
    staff = """
        <div style="text-align: center;">
            <h2 style="font-size: 16px;"On Duty Application Report</h2>
        </div>
        <table style="border-collapse: collapse; width: 100%; border: 1px solid black; font-size: 10px;">
            <tr style="border: 1px solid black;">
                <th style="padding: 4px; border: 1px solid black;">S.No</th>
                <th style="padding: 4px; border: 1px solid black;">Employee</th>
                <th style="padding: 4px; border: 1px solid black;">Employee Name</th>
                <th style="padding: 4px; border: 1px solid black;">Department</th>
                <th style="padding: 4px; border: 1px solid black;">Document ID</th>
                <th style="padding: 4px; border: 1px solid black;">On Duty Date</th>
                <th style="padding: 4px; border: 1px solid black;">From Time</th>
                <th style="padding: 4px; border: 1px solid black;">To Time</th>
            </tr>
    """
    staff_hod = staff
    staff_md = staff
    staff_department = staff
    staff_director = staff


    hr = frappe.db.sql_list(
                """select distinct hr_approval from `tabEmployee`
                where status = 'Active' """,
            )
    
    count = frappe.db.count('On Duty Application',{'workflow_state':'HR Pending','docstatus':0})
    if count != 0:
        for i in hr:
            hr_approver = frappe.get_all("Employee",{'status':'Active','hr_approval':i},['name'])
            for j in hr_approver:
                hr_app = frappe.get_all("On Duty Application",{'employee':j.name},['employee','employee_name','department','name','od_date','from_time','to_time','workflow_state'])
                for leave in hr_app:
                    idx = 1
                    if leave.workflow_state == 'HR Pending':
                        
                        if leave:
                            staff += """
                                <tr style="border: 1px solid black;">
                                    <td style="padding: 4px; border: 1px solid black;">{0}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{1}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{2}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{3}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{4}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{5}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{6}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{7}</td>
                                </tr>
                            """.format(idx, leave.employee_id, leave.employee_name or '', leave.department, leave.name or ' ',
                        format_date(leave.od_date), leave.from_time, leave.to_time)
                            idx += 1

        frappe.sendmail(
                        recipients=['jothi.m@groupteampro.com'],
                        subject='On Duty Applicationt Report',
                        message="""Dear Sir,<br><br>
                                Kindly Find the list of On Duty Application waiting for your Approval:<br>{0}
                                """.format(staff)
                    )
            
    # hr = frappe.db.sql_list(
    #             """select distinct department_approval from `tabEmployee`
    #             where status = 'Active' """,
    #         )
    count1 = frappe.db.count('On Duty Application',{'workflow_state':'Department Pending','docstatus':0})
    if count1 != 0:
        hr_app = frappe.get_all(
        "On Duty Application",
        filters={'docstatus': ['!=', 2]},
        fields=['employee', 'employee_name', 'department', 'name', 'od_date', 'from_time', 'to_time', 'workflow_state']
    )
        # for i in hr:
            # hr_approver = frappe.get_all("Employee",{'status':'Active','department_approval':i},['name'])
            # for j in hr_approver:
                # hr_app = frappe.get_all(On Duty Application",{'employee':j.name},['employee','employee_name','department','name','from_date','to_date','leave_type','workflow_state'])
        for leave in hr_app:
            idx = 1
            if leave.workflow_state == 'Department Pending':
                # idx = 1
                if leave:
                    staff_department += """
                        <tr style="border: 1px solid black;">
                            <td style="padding: 4px; border: 1px solid black;">{0}</td>
                            <td style="padding: 4px; border: 1px solid black;">{1}</td>
                            <td style="padding: 4px; border: 1px solid black;">{2}</td>
                            <td style="padding: 4px; border: 1px solid black;">{3}</td>
                            <td style="padding: 4px; border: 1px solid black;">{4}</td>
                            <td style="padding: 4px; border: 1px solid black;">{5}</td>
                            <td style="padding: 4px; border: 1px solid black;">{6}</td>
                            <td style="padding: 4px; border: 1px solid black;">{7}</td>
                        </tr>
                    """.format(idx, leave.employee, leave.employee_name or '', leave.department, leave.name or ' ',
                        format_date(leave.od_date), leave.from_time, leave.to_time)
                    idx += 1

        frappe.sendmail(
                recipients=['jothi.m@groupteampro.com'],
                subject='On Duty Application Report',
                message="""Dear Sir,<br><br>
                        Kindly Find the list of On Duty Application waiting for your Approval:<br>{0}
                        """.format(staff_department)
            )
    # hr = frappe.db.sql_list(
    #             """select distinct md_approval from `tabEmployee`
    #             where status = 'Active' """,
    #         )
    count2 = frappe.db.count('On Duty Application',{'workflow_state':'MD Pending','docstatus':0})
    if count2 != 0:
        # for i in hr:
            # if i:
                # hr_approver = frappe.get_all("Employee",{'status':'Active','md_approval':i},['name'])
                # for j in hr_approver:
                #     hr_app = frappe.get_all(Permission Request",{'employee':j.name},['employee','employee_name','department','name','from_date','to_date','leave_type','workflow_state'])
        hr_app = frappe.get_all(
        "On Duty Application",
        filters={'docstatus': ['!=', 2]},
        fields=['employee', 'employee_name', 'department', 'name', 'od_date', 'from_time', 'to_time', 'workflow_state']
    )
        for leave in hr_app:
            idx = 1
            if leave.workflow_state == 'MD Pending':
                
                staff_md += """
                    <tr style="border: 1px solid black;">
                        <td style="padding: 4px; border: 1px solid black;">{0}</td>
                        <td style="padding: 4px; border: 1px solid black;">{1}</td>
                        <td style="padding: 4px; border: 1px solid black;">{2}</td>
                        <td style="padding: 4px; border: 1px solid black;">{3}</td>
                        <td style="padding: 4px; border: 1px solid black;">{4}</td>
                        <td style="padding: 4px; border: 1px solid black;">{5}</td>
                        <td style="padding: 4px; border: 1px solid black;">{6}</td>
                        <td style="padding: 4px; border: 1px solid black;">{7}</td>
                    </tr>
                """.format(idx, leave.employee, leave.employee_name, leave.department, leave.name or ' ',
                        format_date(leave.od_date), leave.from_time, leave.to_time or '')
                idx += 1

        frappe.sendmail(
                    recipients=['jothi.m@groupteampro.com'],
                    subject='On Duty Application Report',
                    message="""Dear Sir,<br><br>
                            Kindly Find the list of On Duty Application waiting for your Approval:<br>{0}
                            """.format(staff_md)
                )
    hr_app = frappe.get_all("On Duty Application",
                        filters={'docstatus': ['!=', 2]},
                        fields=['employee', 'employee_name', 'department', 'name', 'od_date', 'from_time', 'to_time', 'workflow_state'])

    # hr_app = frappe.get_all("On Duty Application",{'docstatus', '!=', 2},['employee','employee_name','department','name','from_date','to_date','leave_type','workflow_status'])
    count3 = frappe.db.count('On Duty Application',{'workflow_state':'Director Pending','docstatus':0})
    if count3 != 0:
        for leave in hr_app:
            idx = 1
            if leave.workflow_state == 'Director Pending':
                # idx = 1
                staff_director += """
                    <tr style="border: 1px solid black;">
                        <td style="padding: 4px; border: 1px solid black;">{0}</td>
                        <td style="padding: 4px; border: 1px solid black;">{1}</td>
                        <td style="padding: 4px; border: 1px solid black;">{2}</td>
                        <td style="padding: 4px; border: 1px solid black;">{3}</td>
                        <td style="padding: 4px; border: 1px solid black;">{4}</td>
                        <td style="padding: 4px; border: 1px solid black;">{5}</td>
                        <td style="padding: 4px; border: 1px solid black;">{6}</td>
                        <td style="padding: 4px; border: 1px solid black;">{7}</td>
                    </tr>
               """.format(idx, leave.employee, leave.employee_name, leave.department, leave.name or ' ',
                        format_date(leave.od_date), leave.from_time, leave.to_time or '')
                idx += 1

        frappe.sendmail(
            recipients=['jothi.m@groupteampro.com'],
            subject='On Duty Application Report',
            message="""Dear Sir,<br><br>
                    Kindly Find the list of On Duty Application waiting for your Approval:<br>{0}
                    """.format(staff_director)
        )
    hr_app = frappe.get_all(
        "On Duty Application",
        filters={'docstatus': ['!=', 2]},
        fields=['employee', 'employee_name', 'department', 'name', 'od_date', 'from_time', 'to_time', 'workflow_state']
    )

    count5 = frappe.db.count('On Duty Application', {'workflow_state': 'HOD Pending', 'docstatus': 0})
    hod_list_1, hod_list_2, hod_list_3, hod_list_4 = "", "", "", ""
    idx = 1
    if count5 != 0:
        for leave in hr_app:
            if leave.workflow_state == 'HOD Pending':
                row = """
                    <tr style="border: 1px solid black;">
                        <td style="padding: 4px; border: 1px solid black;">{0}</td>
                        <td style="padding: 4px; border: 1px solid black;">{1}</td>
                        <td style="padding: 4px; border: 1px solid black;">{2}</td>
                        <td style="padding: 4px; border: 1px solid black;">{3}</td>
                        <td style="padding: 4px; border: 1px solid black;">{4}</td>
                        <td style="padding: 4px; border: 1px solid black;">{5}</td>
                        <td style="padding: 4px; border: 1px solid black;">{6}</td>
                        <td style="padding: 4px; border: 1px solid black;">{7}</td>
                    </tr>
                """.format(idx, leave.employee, leave.employee_name, leave.department, leave.name or ' ',
                        format_date(leave.od_date), leave.from_time, leave.to_time or '')
                if leave.department in ['PPC - JMPL', 'Purchase - JMPL', 'Sales - JMPL']:
                    hod_list_1 += row
                elif leave.department in ['Finance - JMPL', 'HR and GA - JMPL']:
                    hod_list_2 += row
                elif leave.department in ['Technical - JMPL', 'QUALITY - JMPL']:
                    hod_list_3 += row
                # elif leave.department in ['Stores - JMPL', 'Dispatch - JMPL', 'Assembly Shop - JMPL', 'Machine Shop - JMPL', 'MAINTENANCE - JMPL', 'Utility - JMPL']:
                else:
                    hod_list_4 += row
                idx += 1
        multiple_hod_list = [hod_list_1, hod_list_2, hod_list_3, hod_list_4]
        for l in multiple_hod_list:
            if l: 
                frappe.sendmail(
                    recipients=['jothi.m@groupteampro.com'],
                    subject='On Duty Application Report',
                    message="""Dear Sir,<br><br>
                            Kindly Find the list of On Duty Application waiting for your Approval:<br>{0}{1}""".format(staff_hod,l)
                )

@frappe.whitelist()
def compensatory_application_notify():
    staff = """
        <div style="text-align: center;">
            <h2 style="font-size: 16px;">Compensatory Leave Request Report</h2>
        </div>
        <table style="border-collapse: collapse; width: 100%; border: 1px solid black; font-size: 10px;">
            <tr style="border: 1px solid black;">
                <th style="padding: 4px; border: 1px solid black;">S.No</th>
                <th style="padding: 4px; border: 1px solid black;">Employee</th>
                <th style="padding: 4px; border: 1px solid black;">Employee Name</th>
                <th style="padding: 4px; border: 1px solid black;">Department</th>
                <th style="padding: 4px; border: 1px solid black;">Document ID</th>
                <th style="padding: 4px; border: 1px solid black;">From date</th>
                <th style="padding: 4px; border: 1px solid black;">To Date</th>
                <th style="padding: 4px; border: 1px solid black;">Leave Type</th>
            </tr>
    """
    staff_hod = staff
    staff_md = staff
    staff_department = staff
    staff_director = staff


    hr = frappe.db.sql_list(
                """select distinct hr_approval from `tabEmployee`
                where status = 'Active' """,
            )
    
    count = frappe.db.count('Compensatory Leave Request',{'workflow_state':'HR Pending','docstatus':0})
    if count != 0:
        for i in hr:
            hr_approver = frappe.get_all("Employee",{'status':'Active','hr_approval':i},['name'])
            for j in hr_approver:
                hr_app = frappe.get_all("Compensatory Leave Request",{'employee':j.name},['employee','employee_name','department','name','work_from_date','work_end_date','leave_type','workflow_state'])
                for leave in hr_app:
                    idx = 1
                    if leave.workflow_state == 'HR Pending':
                        
                        if leave:
                            staff += """
                                <tr style="border: 1px solid black;">
                                    <td style="padding: 4px; border: 1px solid black;">{0}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{1}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{2}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{3}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{4}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{5}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{6}</td>
                                    <td style="padding: 4px; border: 1px solid black;">{7}</td>
                                </tr>
                hr_app = frappe.get_all("Compensatory Leave Request",{'employee':j.name},['employee','employee_name','department','name','work_from_date','work_end_date','leave_type','workflow_state'])
                            """.format(idx, leave.employee, leave.employee_name, leave.department, leave.name or ' ',format_date(leave.work_from_date),format_date(leave.work_end_date), leave.leave_type or '')
                            idx += 1

        frappe.sendmail(
                        recipients=['jothi.m@groupteampro.com'],
                        subject='Compensatory Leave Request Report',
                        message="""Dear Sir,<br><br>
                                Kindly Find the list of Compensatory Leave Request waiting for your Approval:<br>{0}
                                """.format(staff)
                    )
            
    # hr = frappe.db.sql_list(
    #             """select distinct department_approval from `tabEmployee`
    #             where status = 'Active' """,
    #         )
    count1 = frappe.db.count('Compensatory Leave Request',{'workflow_state':'Department Pending','docstatus':0})
    if count1 != 0:
        hr_app = frappe.get_all(
        "Compensatory Leave Request",
        filters={'docstatus': ['!=', 2]},
        fields=['employee', 'employee_name', 'department', 'name', 'work_from_date', 'work_end_date', 'leave_type', 'workflow_state']
    )
        # for i in hr:
            # hr_approver = frappe.get_all("Employee",{'status':'Active','department_approval':i},['name'])
            # for j in hr_approver:
                # hr_app = frappe.get_all("Compensatory Leave Request",{'employee':j.name},['employee','employee_name','department','name','from_date','to_date','leave_type','workflow_state'])
        for leave in hr_app:
            idx = 1
            if leave.workflow_state == 'Department Pending':
                # idx = 1
                if leave:
                    staff_department += """
                        <tr style="border: 1px solid black;">
                            <td style="padding: 4px; border: 1px solid black;">{0}</td>
                            <td style="padding: 4px; border: 1px solid black;">{1}</td>
                            <td style="padding: 4px; border: 1px solid black;">{2}</td>
                            <td style="padding: 4px; border: 1px solid black;">{3}</td>
                            <td style="padding: 4px; border: 1px solid black;">{4}</td>
                            <td style="padding: 4px; border: 1px solid black;">{5}</td>
                            <td style="padding: 4px; border: 1px solid black;">{6}</td>
                            <td style="padding: 4px; border: 1px solid black;">{7}</td>
                        </tr>
                hr_app = frappe.get_all("Compensatory Leave Request",{'employee':j.name},['employee','employee_name','department','name','work_from_date','work_end_date','leave_type','workflow_state'])
                    """.format(idx, leave.employee, leave.employee_name, leave.department, leave.name or ' ',format_date(leave.work_from_date),format_date(leave.work_end_date), leave.leave_type or '')
                    idx += 1

        frappe.sendmail(
                recipients=['jothi.m@groupteampro.com'],
                subject='Compensatory Leave Request Report',
                message="""Dear Sir,<br><br>
                        Kindly Find the list of Compensatory Leave Request waiting for your Approval:<br>{0}
                        """.format(staff_department)
            )
    # hr = frappe.db.sql_list(
    #             """select distinct md_approval from `tabEmployee`
    #             where status = 'Active' """,
    #         )
    count2 = frappe.db.count('Compensatory Leave Request',{'workflow_state':'MD Pending','docstatus':0})
    if count2 != 0:
        # for i in hr:
            # if i:
                # hr_approver = frappe.get_all("Employee",{'status':'Active','md_approval':i},['name'])
                # for j in hr_approver:
                #     hr_app = frappe.get_all("Compensatory Leave Request",{'employee':j.name},['employee','employee_name','department','name','from_date','to_date','leave_type','workflow_state'])
        hr_app = frappe.get_all(
        "Compensatory Leave Request",
        filters={'docstatus': ['!=', 2]},
        fields=['employee', 'employee_name', 'department', 'name', 'work_from_date', 'work_end_date', 'leave_type', 'workflow_state']
    )
        for leave in hr_app:
            idx = 1
            if leave.workflow_state == 'MD Pending':
                
                staff_md += """
                    <tr style="border: 1px solid black;">
                        <td style="padding: 4px; border: 1px solid black;">{0}</td>
                        <td style="padding: 4px; border: 1px solid black;">{1}</td>
                        <td style="padding: 4px; border: 1px solid black;">{2}</td>
                        <td style="padding: 4px; border: 1px solid black;">{3}</td>
                        <td style="padding: 4px; border: 1px solid black;">{4}</td>
                        <td style="padding: 4px; border: 1px solid black;">{5}</td>
                        <td style="padding: 4px; border: 1px solid black;">{6}</td>
                        <td style="padding: 4px; border: 1px solid black;">{7}</td>
                    </tr>
                hr_app = frappe.get_all("Compensatory Leave Request",{'employee':j.name},['employee','employee_name','department','name','work_from_date','work_end_date','leave_type','workflow_state'])
                """.format(idx, leave.employee, leave.employee_name, leave.department, leave.name or ' ',format_date(leave.work_from_date),format_date(leave.work_end_date), leave.leave_type or '')
                idx += 1

        frappe.sendmail(
                    recipients=['jothi.m@groupteampro.com'],
                    subject='Compensatory Leave Request Report',
                    message="""Dear Sir,<br><br>
                            Kindly Find the list of Compensatory Leave Request waiting for your Approval:<br>{0}
                            """.format(staff_md)
                )
    hr_app = frappe.get_all("Compensatory Leave Request",
                        filters={'docstatus': ['!=', 2]},
                        fields=['employee', 'employee_name', 'department', 'name', 'work_from_date', 'work_end_date', 'leave_type', 'workflow_state'])

    # hr_app = frappe.get_all("Compensatory Leave Request",{'docstatus', '!=', 2},['employee','employee_name','department','name','from_date','to_date','leave_type','workflow_status'])
    count3 = frappe.db.count('Compensatory Leave Request',{'workflow_state':'Director Pending','docstatus':0})
    if count3 != 0:
        for leave in hr_app:
            if leave.workflow_state == 'Director Pending':
                idx = 1
                staff_director += """
                    <tr style="border: 1px solid black;">
                        <td style="padding: 4px; border: 1px solid black;">{0}</td>
                        <td style="padding: 4px; border: 1px solid black;">{1}</td>
                        <td style="padding: 4px; border: 1px solid black;">{2}</td>
                        <td style="padding: 4px; border: 1px solid black;">{3}</td>
                        <td style="padding: 4px; border: 1px solid black;">{4}</td>
                        <td style="padding: 4px; border: 1px solid black;">{5}</td>
                        <td style="padding: 4px; border: 1px solid black;">{6}</td>
                        <td style="padding: 4px; border: 1px solid black;">{7}</td>
                    </tr>
                hr_app = frappe.get_all("Compensatory Leave Request",{'employee':j.name},['employee','employee_name','department','name','work_from_date','work_end_date','leave_type','workflow_state'])
                """.format(idx, leave.employee, leave.employee_name, leave.department, leave.name or ' ',format_date(leave.work_from_date),format_date(leave.work_end_date), leave.leave_type or '')
                idx += 1

        frappe.sendmail(
            recipients=['jothi.m@groupteampro.com'],
            subject='Compensatory Leave Request Report',
            message="""Dear Sir,<br><br>
                    Kindly Find the list of Compensatory Leave Request waiting for your Approval:<br>{0}
                    """.format(staff_director)
        )
    hr_app = frappe.get_all(
        "Compensatory Leave Request",
        filters={'docstatus': ['!=', 2]},
        fields=['employee', 'employee_name', 'department', 'name', 'work_from_date', 'work_end_date', 'leave_type', 'workflow_state']
    )

    count5 = frappe.db.count('Compensatory Leave Request', {'workflow_state': 'HOD Pending', 'docstatus': 0})
    hod_list_1, hod_list_2, hod_list_3, hod_list_4 = "", "", "", ""
    idx = 1
    if count5 != 0:
        for leave in hr_app:
            if leave.workflow_state == 'HOD Pending':
                row = """
                    <tr style="border: 1px solid black;">
                        <td style="padding: 4px; border: 1px solid black;">{0}</td>
                        <td style="padding: 4px; border: 1px solid black;">{1}</td>
                        <td style="padding: 4px; border: 1px solid black;">{2}</td>
                        <td style="padding: 4px; border: 1px solid black;">{3}</td>
                        <td style="padding: 4px; border: 1px solid black;">{4}</td>
                        <td style="padding: 4px; border: 1px solid black;">{5}</td>
                        <td style="padding: 4px; border: 1px solid black;">{6}</td>
                        <td style="padding: 4px; border: 1px solid black;">{7}</td>
                    </tr>
                """.format(idx, leave.employee, leave.employee_name, leave.department, leave.name or ' ',
                        format_date(leave.work_from_date), format_date(leave.work_end_date), leave.leave_type or '')

                if leave.department in ['PPC - JMPL', 'Purchase - JMPL', 'Sales - JMPL']:
                    hod_list_1 += row
                elif leave.department in ['Finance - JMPL', 'HR and GA - JMPL']:
                    hod_list_2 += row
                elif leave.department in ['Technical - JMPL', 'QUALITY - JMPL']:
                    hod_list_3 += row
                else:
                # elif leave.department in ['Stores - JMPL', 'Dispatch - JMPL', 'Assembly Shop - JMPL', 'Machine Shop - JMPL', 'MAINTENANCE - JMPL', 'Utility - JMPL']:
                    hod_list_4 += row
                idx += 1
        multiple_hod_list = [hod_list_1, hod_list_2, hod_list_3, hod_list_4]
        for l in multiple_hod_list:
            if l: 
                frappe.sendmail(
                    recipients=['jothi.m@groupteampro.com'],
                    subject='Compensatory Leave Request Report',
                    message="""Dear Sir,<br><br>
                            Kindly Find the list of Compensatory Leave Requests waiting for your Approval:<br>{0}{1}""".format(staff_hod,l)
                )
        
            
        
        
            
        
        
            
        
        
            
        
        
        
            
        
        
            
        
        
            
        
        
            
        
        
