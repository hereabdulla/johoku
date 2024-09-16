frappe.listview_settings['On Duty Application'] = {
	onload(listview) {
		frappe.breadcrumbs.add('On Duty Application','Home');
	listview.page.actions.find('[data-label="Edit"],[data-label="Assign To"],[data-label="Apply Assignment Rule"],[data-label="Add Tags"],[data-label="Print"]').parent().parent().remove()
	listview.page.fields_dict.workflow_state.get_query = function() {
		return {
			"filters": {
				"name": ["in", ["Pending for HOD","Pending for HR","Pending for GM","Pending for CEO","Approved","Rejected"]],
			}
		};
	}
	},
}