document.addEventListener('DOMContentLoaded', function() {
    var socket = io();


    var loginForm = document.getElementById('login-form');
    var registrationForm = document.getElementById('registration-form');
    var postForm = document.getElementById('post-form');
    var logoutButton = document.getElementById('logout-button');



    // User List and DM setup
    socket.on('update user list', function(users) {
        updateUserList(users);
    });

    socket.on('receive dm', function(data) {
        var messagesDiv = document.getElementById('posts');
        var messageDiv = document.createElement('div');
        messageDiv.classList.add('post');  // Ensure this class matches your posts for consistent styling
    
        // Format the message date
        var formattedDate = new Date().toLocaleDateString("en-US", {
            year: 'numeric', month: 'long', day: 'numeric',
            hour: '2-digit', minute: '2-digit', second: '2-digit'
        });
    
        // Display differently based on whether the message is to self or to the other user
        var displayContent = `<span>Sent on: ${formattedDate}</span>
            <p><strong>${data.sender}${data.to_self ? ' (DM ' + data.receiver + ')' : ' (DM you)'}</strong> : ${data.content}</p>`;
    
        messageDiv.innerHTML = displayContent;
        messagesDiv.prepend(messageDiv); // Adds the new DM to the top of the list
    });

    socket.on('connect', () => {
        console.log('Reconnected to the server');
        // Possibly emit an event to re-verify the user or request the current user list again.
        socket.emit('request_user_list');
    });

    function updateUserList(users) {
        var userList = document.getElementById('user-list');
        userList.innerHTML = ''; // Clear existing user list entries
        users.forEach(user => {
            let userItem = document.createElement('li');
            userItem.textContent = user;
            const currentUsername = document.body.getAttribute('data-username');
            if (currentUsername !== 'Guest') {
                let dmButton = document.createElement('button');
                dmButton.textContent = 'DM';
                dmButton.onclick = function() {
                    let message = prompt(`Send DM to ${user}:`);
                    if (message) {
                        socket.emit('send dm', {receiver: user, message: message});
                    }
                };
                userItem.appendChild(dmButton);
            }
            userList.appendChild(userItem);
        });
    }



    //Helper function to handle form submissions w/ fetch request
    function handleFormSubmission(form, url, redirectOnSuccess) {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            var messageType = document.getElementById('message-type-selector').value;
            var message = document.querySelector('.chat-textbox').value.trim();
    
            if (messageType === 'chat' || messageType === 'dm') {
                socket.emit('send chat message', { content: message, messageType: messageType });
                document.querySelector('.chat-textbox').value = '';  // Clear the chat input field
            } else {
                var formData = new FormData(form);
                formData.append('messageType', messageType);
    
                fetch(url, {
                    method: 'POST',
                    body: formData
                }).then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log('Post successfully created');
                        if (redirectOnSuccess) window.location.href = redirectOnSuccess;
                    } else {
                        console.error('Failed to create post:', data.message);
                    }
                }).catch(error => {
                    console.error('Error:', error);
                });
            }
        });
    }
    
    function formatEasternTime(date) {
        return date.toLocaleString('en-US', {
            timeZone: 'America/New_York',
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit', 
            hour12: true
        });
    }
    
    socket.on('new content', function(data) {
        var postsDiv = document.getElementById('posts');
        var postDiv = document.createElement('div');
        postDiv.className = 'post';
        var displayDate = data.created_at ? data.created_at : formatEasternTime(new Date());
        postDiv.innerHTML = `<span>Posted on: ${displayDate}</span>
            <p><strong>${data.username}</strong> : ${data.content}</p>`;
    
        if (data.image) {
            postDiv.innerHTML += `<img src="static/image/${data.image}" alt="User uploaded image">`;
        }
        // postsDiv.appendChild(postDiv); // Adds the new content to the top of the list
        postsDiv.insertBefore(postDiv, postsDiv.firstChild);
    });
    function RegisterLogin_FormSubmission(form, url, redirectOnSuccess) {
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
        RegisterLogin_FormSubmission(loginForm, '/login', '/'); // Redirect to '/' instead of '/home'
    }
    if (registrationForm) {
        RegisterLogin_FormSubmission(registrationForm, '/register', '/'); // Redirect to '/' instead of '/home'
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

    // Reload the page when requested by the server
    socket.on('reload_page', function() {
        location.reload();
    });

    socket.on('update_scheduled_post', function(data) {
        var timeRemaining = data.time_remaining;
        var postId = data.post_id;
    
        var remainingTimeElement = document.getElementById(postId + '_remaining');
        if (remainingTimeElement) {
            remainingTimeElement.innerText = 'Time remaining: ' + timeRemaining + ' seconds';
        } else {
            var newPostElement = document.createElement('div');
            newPostElement.id = postId + '_remaining';
            newPostElement.innerText = 'Time remaining: ' + timeRemaining + ' seconds';
            document.getElementById('scheduledPosts').appendChild(newPostElement);
        }
    });
});
