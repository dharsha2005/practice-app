app_name = "practice_app"
app_title = "Practice App"
app_publisher = "Dharshan"
app_description = "Simple Student Practice Application"
app_email = "admin@example.com"
app_license = "mit"

website_route_rules = [
	{"from_route": "/student", "to_route": "student"},
    {"from_route": "/courses", "to_route": "courses"}
]

doc_events={
    "Student-form":{
        "after_insert": "practice_app.api.student_saved"
    }
}
on_login = "practice_app.api.redirect_after_login"