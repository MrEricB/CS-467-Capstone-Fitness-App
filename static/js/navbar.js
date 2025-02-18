// Active class JS referenced from https://www.youtube.com/watch?v=ThSaI0kuez8
// Switches the active class to the current nav-link page
const navLinks = document.querySelectorAll('.nav-link');
const windowPathName = window.location.pathname;

navLinks.forEach(navLinks => {
  const linkPathName = new URL(navLinks.href).pathname;

  if ((windowPathName === linkPathName)) {
    navLinks.classList.add('active');
  }
})