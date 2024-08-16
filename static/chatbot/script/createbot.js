document.addEventListener('DOMContentLoaded', async () => {
try {
const response = await fetch('/chatbot/list-keys/');
if (!response.ok) throw new Error('Error fetching keys');

const data = await response.json();
const containerParent = document.querySelector('.containers-starters');
const svgFiles = ['prompt1.svg', 'prompt2.svg', 'prompt3.svg'];

if (data.length > 0) {
    data.forEach(item => {
        // Create the container div
        const containerDiv = document.createElement('div');
        containerDiv.className = 'containers';
        containerDiv.setAttribute('data-prompt', item.model_name);

        // Create the delete icon using Font Awesome
        const deleteIcon = document.createElement('i');
        console.log(deleteIcon);

        deleteIcon.className = "fas fa-trash-alt delete-icon"
        ; // Font Awesome 'times' icon

        // Add delete functionality
        deleteIcon.addEventListener('click', async (event) => {
            event.stopPropagation(); // Prevent triggering the container click event
            const confirmDelete = confirm('Are you sure you want to delete this bot?');
            if (confirmDelete) {
                try {
                    const deleteResponse = await fetch(`/chatbot/delete-key/${item.hash_key}/`, {
                        method: 'DELETE',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    });

                    if (deleteResponse.ok) {
                        alert('Bot deleted successfully.');
                        containerDiv.remove(); // Remove the container from the DOM
                    } else {
                        alert('Failed to delete bot.');
                    }
                } catch (error) {
                    console.error('Error deleting bot:', error);
                    alert('An unexpected error occurred.');
                }
            }
        });

        // Select a random SVG
        const randomSvg = svgFiles[Math.floor(Math.random() * svgFiles.length)];

        // Create the img element
        const imgElement = document.createElement('img');
        imgElement.src = `/static/chatbot/img-create-bot/${randomSvg}`;
        imgElement.alt = `Prompt for ${item.model_name}`;

        // Create the paragraph element
        const paragraphElement = document.createElement('p');
        paragraphElement.textContent = item.model_name;

        // Append delete icon, img, and paragraph to the container
        containerDiv.appendChild(deleteIcon);
        containerDiv.appendChild(imgElement);
        containerDiv.appendChild(paragraphElement);

        // Add click event to redirect to the start bot page
        containerDiv.addEventListener('click', () => {
            window.location.href = `/chatbot/start-bot/${item.hash_key}`;
        });

        // Append the container to the parent div
        containerParent.appendChild(containerDiv);
    });
} else {
    console.log('No keys available.');
}
} catch (error) {
console.error('Error fetching keys:', error);
}
});
document.getElementById('createAgentButton').addEventListener('click', () => {
    const headerContent = document.getElementById('header-content');
    const formContent = document.getElementById('form-content');
    document.querySelector('.form-container').classList.toggle('active');
    headerContent.style.display = 'none';
    formContent.style.display = 'block';

});

document.getElementById('hubButton').addEventListener('click', () => {
    window.location.href = '/chatbot/hub/';
});
document.getElementById('igcse').addEventListener('click', () => {
    window.location.href = '/chatbot/igcse/';
});
document.getElementById('cancelButton').addEventListener('click', () => {
    const headerContent = document.getElementById('header-content');
    const formContent = document.getElementById('form-content');
    document.querySelector('.form-container').classList.remove('active');
    formContent.style.display = 'none';
    headerContent.style.display = 'block';
});

document.getElementById('createAgentForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const botName = document.getElementById('botName').value.trim();
    const botPurpose = document.getElementById('botPurpose').value.trim();
    const botData = document.getElementById('botData').value.trim();

    if (!botName || !botPurpose || !botData) {
        alert('All fields are required!');
        return;
    }

    try {
const storeKeyResponse = await fetch('/chatbot/create_agent/', {
method: 'POST',
headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken')
},
body: JSON.stringify({ name: botName, purpose: botPurpose, data: botData })
});

if (storeKeyResponse.ok) {
const responseData = await storeKeyResponse.json();

// Show success message
alert(responseData.message);

// Redirect to the next screen
window.location.href = `/chatbot/edit_bot/${responseData.id}`;
} else {
const errorData = await storeKeyResponse.json(); // Parse the error response
alert('Error creating agent: ' + errorData.error); // Alert the exact error message
}
} catch (error) {
console.error('Fetch Error:', error);
alert('An unexpected error occurred.');
}
});


function getCookie(name) {
const cookies = document.cookie ? document.cookie.split(';') : [];
for (const cookie of cookies) {
const trimmedCookie = cookie.trim();
if (trimmedCookie.startsWith(`${name}=`)) {
    return decodeURIComponent(trimmedCookie.substring(name.length + 1));
}
}
return null;
}
document.getElementById('tech_realm').addEventListener('click', () => {
    window.location.href = '/chatbot/create_bot/';
  });
  if (window.innerWidth <= 768) {
      const logo = document.querySelector('.logo-text');
      logo.style.cursor = 'pointer';
      
      logo.addEventListener('click', () => {
        window.location.href = '/chatbot/'; // Replace with your URL
      });
    }