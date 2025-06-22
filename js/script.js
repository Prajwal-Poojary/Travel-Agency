/*-- SHOW MENU --*/
const navMenu = document.getElementById('nav-menu'),
      navToggle = document.getElementById('nav-toggle'),
      navClose = document.getElementById('nav-close');

if(navToggle){
    navToggle.addEventListener('click', () =>{
        navMenu.classList.add('show-menu');
    });
}

if(navClose){
    navClose.addEventListener('click', () =>{
        navMenu.classList.remove('show-menu');
    });
}

/*-- REMOVE MENU MOBILE --*/
const navLink = document.querySelectorAll('.nav__link');

function linkAction(){
    const navMenu = document.getElementById('nav-menu');
    navMenu.classList.remove('show-menu');
}
navLink.forEach(n => n.addEventListener('click', linkAction));


/*-- CHANGE BACKGROUND HEADER --*/
function scrollHeader(){
    const header = document.getElementById('header');
    if(this.scrollY >= 100) header.classList.add('scroll-header'); else header.classList.remove('scroll-header');
}
window.addEventListener('scroll', scrollHeader);


/*-- SEARCH FORM --*/
let searchForm = document.querySelector('.search-form');

document.querySelector('#search-btn').onclick = () =>{
    searchForm.classList.add('active');
};

document.querySelector('#close-search').onclick = () =>{
    searchForm.classList.remove('active');
};


/*-- SHOW SCROLL UP --*/ 
function scrollUp(){
    const scrollUp = document.getElementById('scroll-up');
    if(this.scrollY >= 200) scrollUp.classList.add('show-scroll'); else scrollUp.classList.remove('show-scroll');
}
window.addEventListener('scroll', scrollUp);


/*-- SCROLL SECTIONS ACTIVE LINK --*/
const sections = document.querySelectorAll('section[id]');

function scrollActive(){
    const scrollY = window.pageYOffset;

    sections.forEach(current =>{
        const sectionHeight = current.offsetHeight;
        const sectionTop = current.offsetTop - 50;
        sectionId = current.getAttribute('id');

        if(scrollY > sectionTop && scrollY <= sectionTop + sectionHeight){
            document.querySelector('.nav__menu a[href*=' + sectionId + ']').classList.add('active-link');
        }else{
            document.querySelector('.nav__menu a[href*=' + sectionId + ']').classList.remove('active-link');
        }
    });
}
window.addEventListener('scroll', scrollActive);

/*-- Contact Form Submission --*/
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".contact-form form");
    if (!form) return;
    const submitButton = form.querySelector("button[type='submit']");
    
    form.addEventListener("submit", function (event) {
        event.preventDefault(); 
        
        const name = form.querySelector("input[name='name']").value.trim();
        const email = form.querySelector("input[name='email']").value.trim();
        const phone = form.querySelector("input[name='phone']").value.trim();
        const subject = form.querySelector("input[name='subject']").value.trim();
        const message = form.querySelector("textarea[name='message']").value.trim();
        
        if (!name || !email || !phone || !subject || !message) {
            alert("Please fill in all fields.");
            return;
        }
        
        const originalButtonText = submitButton.innerHTML;
        submitButton.innerHTML = "Sending...";
        submitButton.disabled = true;
        
        setTimeout(() => {
            alert("Your message has been sent successfully!");
            form.reset();
            submitButton.innerHTML = originalButtonText;
            submitButton.disabled = false;
        }, 2000);
    });
});

function reveal() {
    var reveals = document.querySelectorAll('.fade-in, .box-container');

    for(var i = 0; i < reveals.length; i++){

        var windowHeight = window.innerHeight;
        var revealtop = reveals[i].getBoundingClientRect().top;
        var revealpoint = 50;

        if(revealtop < windowHeight - revealpoint){
            reveals[i].classList.add('active');
        }
    }
}

window.addEventListener('scroll', reveal);
reveal();
