document.addEventListener('DOMContentLoaded', function() {

    var button = document.getElementById('toggleButton');
    var image = document.getElementById('toggleImage');
    
    image.style.display = 'none';
    
    button.addEventListener('click', function() {
        if (image.style.display === 'none') {
            image.style.display = 'block';
        } else {
            image.style.display = 'none';
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    var loggedIn = false;

    if (loggedIn === true) {
        document.getElementById('home-page').style.display = 'block';
        document.getElementById('username').textContent = 'test Username';
        document.getElementById('registration-form').style.display = 'none';
        document.getElementById('login-form').style.display = 'none';
    } else {
        document.getElementById('registration-form').style.display = 'block';
        document.getElementById('login-form').style.display = 'block';
        document.getElementById('home-page').style.display = 'none';
    }
});

function logout() {
    // idk how to log out rn back to youtube videos ig

    fetch('/logout', {
        method: 'POST',
    })
    .then(response => {
        if (response.ok) {
            document.getElementById('home-page').style.display = 'none';
            document.getElementById('login-form').style.display = 'block';
            document.getElementById('registration-form').style.display = 'block';
        }
    })
    
    console.log('user logged out');
}
