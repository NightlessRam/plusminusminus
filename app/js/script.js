document.addEventListener('DOMContentLoaded', function() {

    
    var toggleButton = document.getElementById('toggleButton');
    var toggleImage = document.getElementById('toggleImage');
    

    var loginForm = document.getElementById('login-form-element');
    var registrationForm = document.getElementById('registration-form-element');
    var logoutButton = document.getElementById('logout-button');


    toggleButton.addEventListener('click', function() 
    {
        if (toggleImage.style.display === 'none') {
            toggleImage.style.display = 'block';
        } else {
            toggleImage.style.display = 'none';
        }

    });

    
    loginForm.addEventListener('submit', function() {
        var formData = new FormData(loginForm);
        fetch('/login', {
            method: 'POST',
            body: formData
        }).then(data => {

            document.getElementById('username').textContent = data.username;
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('registration-form').style.display = 'none';
            document.getElementById('home-page').style.display = 'block';

        })
    });

    registrationForm.addEventListener('submit', function() {
        var formData = new FormData(registrationForm);
        fetch('/register', {
            method: 'POST',
            body: formData
        }).then(data => {

            document.getElementById('username').textContent = data.username;
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('registration-form').style.display = 'none';
            document.getElementById('home-page').style.display = 'block';

        })
    });

    if (logoutButton) {
        logoutButton.addEventListener('click', function() {
            // idk how to log out rn back to youtube videos ig

            fetch('/logout', {
                method: 'POST',
            }).then(response => {
                if (response.ok) {

                    document.getElementById('home-page').style.display = 'none';
                    document.getElementById('login-form').style.display = 'block';
                    document.getElementById('registration-form').style.display = 'block';

                }
            });
        });
    }
});
