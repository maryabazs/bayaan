function showModal(message) {
    let modal = document.createElement("div");
    modal.classList.add("modal");
    modal.style.display = "flex";
    
    modal.innerHTML = `
        <div class="modal-content">
            <p>${message}</p>
            <div class="modal-buttons">
                <button class="okButton">OK</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    modal.querySelector(".okButton").addEventListener("click", function() {
        modal.style.display = "none";
        document.body.removeChild(modal);
    });
}

function sendMail() {
    let name = document.getElementById("name").value;
    let email = document.getElementById("email").value;
    let subject = document.getElementById("subject").value;
    let message = document.getElementById("message").value;
    
    // التحقق من أن جميع الحقول ممتلئة
    if (name.trim() === "" || email.trim() === "" || subject.trim() === "" || message.trim() === "") {
        showModal("Please fill out all fields before sending the message!");
        return;
    }
    
    let parms = {
        name: name,
        email: email,
        subject: subject,
        message: message
    };

    emailjs.send("service_tuo511f", "template_7qe6e9m", parms)
    .then(function(response) {
        showModal("Message sent successfully!");
    }, function(error) {
        showModal("Failed to send: " + error.text);
    });
}
