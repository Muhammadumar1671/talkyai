function logout() {
    fetch('/logout', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.status === 200) {
            document.cookie = 'csrftoken=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
            window.location.href = '/';
        } else {
            console.error('Logout failed');
        }
    })
    .catch(error => {
        console.error('An error occurred:', error);
    });
}
