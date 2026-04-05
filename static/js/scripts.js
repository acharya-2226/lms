document.addEventListener("DOMContentLoaded", function () {
	var currentPath = window.location.pathname;
	var navLinks = document.querySelectorAll('.navbar .nav-link[href]');

	navLinks.forEach(function (link) {
		var linkPath = new URL(link.href).pathname;
		if (linkPath === currentPath) {
			link.classList.add('active');
			link.setAttribute('aria-current', 'page');
		}
	});
});
