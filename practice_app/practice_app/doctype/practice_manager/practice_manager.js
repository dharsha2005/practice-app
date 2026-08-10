frappe.ui.form.on('practice-manager', {
    refresh(frm) {
        frm.add_custom_button(__('Run Assignment API'), () => {
            frappe.call({
                method: 'practice_app.api.assignment_api',
                callback: function (r) {
                    if (r.message) {
                        let records = r.message;
                        let msg = `<p><strong>API successfully run! Found ${records.length} records.</strong></p>`;
                        msg += '<table class="table table-bordered" style="margin-top: 10px;">';
                        msg += '<thead><tr><th>Doc Name</th><th>Student Name</th><th>Age</th><th>Subject</th><th>Marks</th></tr></thead>';
                        msg += '<tbody>';
                        records.forEach(row => {
                            msg += `<tr>
                                <td>${row.name}</td>
                                <td>${row.student_name}</td>
                                <td>${row.age}</td>
                                <td>${row.subject}</td>
                                <td>${row.marks}</td>
                            </tr>`;
                        });
                        msg += '</tbody></table>';

                        frappe.msgprint({
                            title: __('Assignment API Records'),
                            message: msg,
                            indicator: 'green',
                            wide: true
                        });

                        frm.reload_doc();
                    } else {
                        frappe.msgprint(__('No records returned or API returned empty.'));
                    }
                }
            });
        });
    }
});
