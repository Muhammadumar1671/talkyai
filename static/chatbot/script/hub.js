
document.addEventListener("DOMContentLoaded", async function () {
    try {
        const url = new URL(window.location.href);
        let pathnames = url.pathname.split('/');
        let urlKey = pathnames[pathnames.length - 2];


        const promptTemplates = {
            open: "Answer the user's query as openly and informatively as possible. Feel free to provide additional relevant information.",
            strict: "Be very strict with your response. Don't add anything that is not in the text.",
            creative: "Use the information provided to answer the user's query in a creative and engaging manner. Feel free to include interesting facts or anecdotes."
        };
        const dropdown = document.getElementById('unique-edit-bot-id');

        // Fetch keys and populate the dropdown
        const data = await fetchKeys();

        // Determine the selected key based on the URL or default to the first one
        const selectedKey = urlKey && data.some(item => item.hash_key === urlKey)
            ? urlKey
            : data[0]?.hash_key;

        if (!selectedKey) {
            console.error('No valid bot keys found.');
            return;
        }

        console.log('Selected key:', selectedKey);

        // Set the dropdown value to the selected key and update content
        dropdown.value = selectedKey;
        updateContent(selectedKey);
        updateSidebarLinks(selectedKey);

        // Handle container clicks to send prompt data
        document.querySelectorAll('.containers').forEach(container => {
            container.addEventListener('click', () => {
                const promptType = container.getAttribute('data-prompt');
                const prompt = promptTemplates[promptType];

                console.log('Selected prompt:', prompt);

                fetch('/chatbot/save-prompt/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        prompt: prompt,
                        key: dropdown.value  // Always use the latest key from the dropdown
                    })
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message || data.error);
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            });
        });

    } catch (error) {
        console.error('Error initializing the document list:', error);
    }
});

// Function to fetch keys and populate the dropdown
async function fetchKeys() {
    const response = await fetch('/chatbot/list-keys/');
    if (!response.ok) throw new Error('Error fetching keys');

    const data = await response.json();
    const dropdown = document.getElementById('unique-edit-bot-id');
    dropdown.innerHTML = '';  // Clear existing options

    if (data.length > 0) {
        data.forEach(item => {
            const option = document.createElement('option');
            option.value = item.hash_key;
            option.textContent = item.model_name;
            dropdown.appendChild(option);
        });

        dropdown.addEventListener('change', function () {
            const selectedKey = this.value;
            updateContent(selectedKey);
            updateSidebarLinks(selectedKey);
        });
    } else {
        dropdown.style.display = 'none';  // Hide the dropdown if no keys are available
    }

    return data;
}

// Function to update content and refresh the URL
function updateContent(key) {
    // Always replace the URL state to avoid adding to the history stack
    history.replaceState(null, '', `/chatbot/hub/${key}/`);
    console.log(`Content updated for bot key: ${key}`);
}

// Function to update sidebar links
function updateSidebarLinks(key) {
    document.getElementById('chat-link').href = `/chatbot/start-bot/${key}/`;
    document.getElementById('file-link').href = `/chatbot/edit_bot/${key}/`;
    document.getElementById('setting-link').href = `/chatbot/hub/${key}/`;
    console.log(`Sidebar links updated with bot key: ${key}`);
}

// Function to get CSRF token
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

  document.querySelectorAll('input[name="email"]').forEach(function(radio) {
    radio.addEventListener('change', function() {
        const frequency = {
            'daily': 1,
            'weekly': 7,
            'monthly': 30
        };

        const selectedValue = frequency[this.value];


        fetch('/chatbot/email-frequency', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')

            },
            body: JSON.stringify({
                email_frequency: selectedValue
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            alert(data.message || data.error);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
});