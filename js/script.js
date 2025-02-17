document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".contact-form form");
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

        
        submitButton.textContent = "Sending...";
        submitButton.disabled = true;
        
        setTimeout(() => {
            alert("Your message has been sent successfully!");
            form.reset();
            submitButton.textContent = "Send";
            submitButton.disabled = false;
        }, 2000);
    });
});
