const hamMenu = document.getElementsByClassName('.hamburger');
const navbar = document.getElementsByClassName('.navlist');

hamMenu.addEventListener('click', () => {
    console.log("hello")
    navbar.classList.toggle('active');
})