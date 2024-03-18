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