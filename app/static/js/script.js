document.addEventListener('DOMContentLoaded', function() {
    var loginForm = document.getElementById('login-form');
    var registrationForm = document.getElementById('registration-form');
    var postForm = document.getElementById('post-form');
    var logoutButton = document.getElementById('logout-button');

    //Helper function to handle form submissions w/ fetch request
    function handleFormSubmission(form, url, redirectOnSuccess) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            var formData = new FormData(form);
            fetch(url, {
                method: 'POST',
                body: formData
            }).then(response => {
                if (response.ok) {
                    window.location.href = redirectOnSuccess;
                } else {
                    alert(`Action failed: ${form.getAttribute('id')}`);
                }
            }).catch(error => {
                console.error('Error:', error);
            });
        });
    }

    //Toggle image display
    var toggleButton = document.getElementById('toggleButton');
    var toggleImage = document.getElementById('toggleImage');

    //set image to be hidden when the page loads
    toggleImage.style.display = 'none';
    toggleButton.addEventListener('click', function() 
    {
        if (toggleImage.style.display === 'none') {
            toggleImage.style.display = 'block';
        } else {
            toggleImage.style.display = 'none';
        }

    });

    //handle form submissions
    if (loginForm) {
        handleFormSubmission(loginForm, '/login', '/'); // Redirect to '/' instead of '/home'
    }
    if (registrationForm) {
        handleFormSubmission(registrationForm, '/register', '/'); // Redirect to '/' instead of '/home'
    }
    if (postForm) {
        handleFormSubmission(postForm, '/posts', '/'); // Redirect to '/' instead of '/home' after posting
    }

    // Logout Button Click
    if (logoutButton) {
        logoutButton.addEventListener('click', function(event) {
            event.preventDefault();
            fetch('/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                    
                }
            }).then(response => {
                if (response.ok) {
                    window.location.href = '/'; // Redirect to '/' after logout
                } else {
                    alert('Logout failed.');
                }
            }).catch(error => {
                console.error('Error:', error);
                alert('Logout failed.');
            });
        });
    }
});
