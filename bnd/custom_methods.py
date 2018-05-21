from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, time_diff_in_hours, get_datetime, getdate, today, cint, add_days 
from frappe import _
from frappe.utils import cint, cstr, date_diff, flt, formatdate, getdate, get_link_to_form, \
	comma_or, get_fullname
# from frappe.utils import (flt, getdate, get_first_day, get_last_day, date_diff,
# 	add_months, add_days, formatdate, cint)

@frappe.whitelist()
def salary_slip(doc,method):
	query="""Select sum(deduction_days), sum(deduction_amount)
	from `tabAttendance` where (attendance_date between '{0}' and '{1}') and employee='{2}'""".format(doc.start_date, doc.end_date, doc.employee)
	deduction_data = frappe.db.sql(query,as_list=1,debug=1)
	if deduction_data:
		deduction = deduction_data[0]
		doc.deduction_days = deduction[0]
		doc.deduction_amount = deduction[1]
		if doc.deduction_amount >= 1 or doc.deduction_days >=1 :
			frappe.msgprint('Deduction days:'+ str(doc.deduction_days) )
			frappe.msgprint('Deduction amount:'+ str(doc.deduction_amount) )

	flag = False
	for i in doc.deductions:
		if i.salary_component == "Attendance Violation":
			flag = True
			i.amount = doc.deduction_amount
	if flag:
		pass
	elif doc.deduction_amount >= 1:
		row = doc.append('deductions', {})
		row.salary_component = "Attendance Violation"
		row.amount =doc.deduction_amount

	present="""Select count(*)
	from `tabAttendance` where (status = 'Present' and attendance_date between '{0}' and '{1}') and employee='{2}' """.format(doc.start_date, doc.end_date, doc.employee)
	attendance_present = frappe.db.sql(present,as_list=1,debug=1)
	absent="""Select count(*)
	from `tabAttendance` where (status = 'Absent' and attendance_date between '{0}' and '{1}') and employee='{2}' """.format(doc.start_date, doc.end_date, doc.employee)
	attendance_absent = frappe.db.sql(absent,as_list=1,debug=1)
	present_count=attendance_present[0]
	absent_count=attendance_absent[0]
	doc.total_present_days= str(present_count[0])
	doc.total_absent_days = str(absent_count[0])

	ot_hours = """Select sum(ot_hours)
	from `tabAttendance` where (attendance_date between '{0}' and '{1}') and employee='{2}' """.format(doc.start_date, doc.end_date, doc.employee)
	ot_data = frappe.db.sql(ot_hours,as_list=1,debug=1)
	ot=ot_data[0]
	frappe.msgprint("OT Hours "+str(ot[0]))


@frappe.whitelist()
def create_attendance(doc,method):
	number_of_days = date_diff(doc.to_date, doc.from_date) + 1
	number_of_days = int(number_of_days)
	leave_type = doc.leave_type
	for i in range(number_of_days) :
		attendance_doc = frappe.new_doc("Attendance")
		attendance_doc.employee = doc.employee
		attendance_doc.attendance_date = doc.from_date
		if leave_type == "LWP":
	 		attendance_doc.status = "Absent"
		else:
			attendance_doc.status = "Present"
		attendance_doc.insert()
		attendance_doc.save()
		attendance_doc.submit()

