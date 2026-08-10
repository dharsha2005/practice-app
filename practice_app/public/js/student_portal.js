/* Student Management Portal - Client-Side JS */

if (typeof window.frappe === "undefined") {
	window.frappe = {};
}

if (typeof window.frappe.call === "undefined") {
	window.frappe.call = function (opts) {
		const method = opts.method;
		const args = opts.args || {};
		const formData = new FormData();
		for (const key in args) {
			if (args.hasOwnProperty(key)) {
				formData.append(key, typeof args[key] === "object" ? JSON.stringify(args[key]) : args[key]);
			}
		}

		fetch("/api/method/" + method, {
			method: "POST",
			body: formData,
			headers: {
				"Accept": "application/json"
			}
		})
		.then(res => {
			if (!res.ok) throw new Error("HTTP error " + res.status);
			return res.json();
		})
		.then(data => {
			if (typeof opts.callback === "function") {
				opts.callback(data);
			}
		})
		.catch(err => {
			if (typeof opts.error === "function") {
				opts.error(err);
			}
		});
	};
}

window.frappe.logout = function () {
	if (typeof frappe.call === "function") {
		frappe.call({
			method: "logout",
			type: "POST",
			callback: function () {
				window.location.href = "/login";
			},
			error: function () {
				window.location.href = "/login";
			}
		});
	} else {
		window.location.href = "/login";
	}
};

document.addEventListener("DOMContentLoaded", function () {
	
	const contactForm = document.getElementById("portal-contact-form");
	if (contactForm) {
		contactForm.addEventListener("submit", function (e) {
			e.preventDefault();
			const submitBtn = contactForm.querySelector('button[type="submit"]');
			const responseAlert = document.getElementById("contact-form-response");
			
			submitBtn.disabled = true;
			submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Sending...';

			const formData = {
				name: document.getElementById("contact-name").value,
				email: document.getElementById("contact-email").value,
				phone: document.getElementById("contact-phone").value,
				subject: document.getElementById("contact-subject").value,
				message: document.getElementById("contact-message").value
			};

			frappe.call({
				method: "practice_app.api.submit_contact_form",
				args: formData,
				callback: function (r) {
					submitBtn.disabled = false;
					submitBtn.innerHTML = 'Send Message <i class="bi bi-send ms-1"></i>';
					if (r.message && r.message.status === "success") {
						responseAlert.className = "alert alert-success mt-3 animate-fade-in";
						responseAlert.textContent = r.message.message;
						responseAlert.classList.remove("d-none");
						contactForm.reset();
					} else {
						responseAlert.className = "alert alert-danger mt-3 animate-fade-in";
						responseAlert.textContent = "An error occurred. Please try again.";
						responseAlert.classList.remove("d-none");
					}
				},
				error: function () {
					submitBtn.disabled = false;
					submitBtn.innerHTML = 'Send Message <i class="bi bi-send ms-1"></i>';
					responseAlert.className = "alert alert-danger mt-3 animate-fade-in";
					responseAlert.textContent = "Failed to submit request. Please check your connection.";
					responseAlert.classList.remove("d-none");
				}
			});
		});
	}

	// Theme Toggle Logic
	const themeToggleBtn = document.getElementById("theme-toggle-btn");
	if (themeToggleBtn) {
		themeToggleBtn.addEventListener("click", function () {
			const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
			const newTheme = currentTheme === "light" ? "dark" : "light";
			document.documentElement.setAttribute("data-theme", newTheme);
			localStorage.setItem("portal_theme", newTheme);
			updateThemeIcon(newTheme);
		});

		const savedTheme = localStorage.getItem("portal_theme") || "light";
		document.documentElement.setAttribute("data-theme", savedTheme);
		updateThemeIcon(savedTheme);
	}

	function updateThemeIcon(theme) {
		const icon = themeToggleBtn.querySelector("i");
		if (icon) {
			if (theme === "dark") {
				icon.className = "bi bi-sun-fill text-warning";
			} else {
				icon.className = "bi bi-moon-stars-fill text-secondary";
			}
		}
	}
});
