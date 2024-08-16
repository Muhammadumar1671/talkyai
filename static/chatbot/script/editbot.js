document.addEventListener("DOMContentLoaded", async function () {
    const url = new URL(window.location.href);
    let pathnames = url.pathname.split('/');
    let urlKey = pathnames[pathnames.length - 2];
    
    console.log('URL key:', urlKey);
    
    try {
        // Fetch keys and populate the dropdown
        const data = await fetchKeys();
        
        // Set the dropdown to the current key from the URL or default to the first one
        const selectedKey = urlKey && urlKey !== '' && data.some(item => item.hash_key === urlKey) 
                            ? urlKey 
                            : data[0].hash_key;

        console.log('Selected key:', selectedKey);
        
        // Set the dropdown value to the selected key and update content
        document.getElementById('unique-edit-bot-id').value = selectedKey;
        updateContent(selectedKey, true);
        updateSidebarLinks(selectedKey);


        
        // Set up file upload and deletion functionality
        setupFileManagement();
        
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

    if (data.length > 0) {
        data.forEach(item => {
            const option = document.createElement('option');
            option.value = item.hash_key;
            option.textContent = item.model_name;
            dropdown.appendChild(option);
        });
    } else {
        dropdown.style.display = 'none'; // Hide the dropdown if no keys are available
    }

    dropdown.addEventListener('change', function () {
        const selectedKey = this.value;
        updateContent(selectedKey, true);
        updateSidebarLinks(selectedKey);
    });
    
    return data;
}

// Function to fetch and display documents based on the selected key
async function fetchAndDisplayDocuments(key) {
    try {
        const response = await fetch(`/chatbot/list-documents/${key}`);
        if (!response.ok) throw new Error('Failed to fetch documents');

        const data = await response.json();
        const fileList = document.getElementById('fileList');
        fileList.innerHTML = '';

        if (data.pdfs && data.pdfs.length > 0) {
            data.pdfs.forEach(file => {
                addFileToList(file);
            });
        } else {
            console.warn('No PDFs found for the selected key.');
            fileList.innerHTML = '<p>No documents found for this bot.</p>'; // Display a message if no PDFs
        }
    } catch (error) {
        console.error('Error fetching or displaying documents:', error);
        const fileList = document.getElementById('fileList');
        fileList.innerHTML = `<p>No documents found for this bot.</p>`; // Display an error message
    }
}

// Function to add file to the list
function addFileToList(fileName) {
    const filePost = document.createElement('div');
    filePost.className = 'file-post';
    filePost.id = 'file-' + fileName;

    const fileContent = document.createElement('div');
    fileContent.className = 'file-content2';
    fileContent.innerHTML = `<p><b>${fileName}</b></p>`;

    const deleteIcon = document.createElement('div');
    deleteIcon.className = 'delete-icon';
    deleteIcon.innerHTML = '<i class="fa-solid fa-trash"></i>';
    deleteIcon.addEventListener('click', function () {
        deleteFile(fileName);
    });

    filePost.appendChild(fileContent);
    filePost.appendChild(deleteIcon);
    document.getElementById('fileList').appendChild(filePost);
}

// Function to delete file from the list
async function deleteFile(fileName) {
  key = document.getElementById('unique-edit-bot-id').value;
  console.log(key);
    const fileElement = document.getElementById('file-' + fileName);
    if (fileElement) {
        fileElement.remove();
    }
    try{
      const csrf = getCookie('csrftoken');
        const response = await fetch(`/chatbot/delete-document/${key}/${fileName}`, {
            method: 'DELETE',
            headers: {
              'X-CSRFToken': csrf
            }
        }); 
        if (!response.ok) throw new Error('Failed to delete document');
        console.log('Document deleted successfully:', fileName);
    }
    catch (error) {
        console.error('Error deleting document:', error);
    }
  
       
}

// Function to handle file upload
async function uploadDocument(file) {
    const key = document.getElementById('unique-edit-bot-id').value; // Always get the current key
    try {
        const formData = new FormData();
        formData.append('document', file);
        formData.append('key', key);
        const csrf = getCookie('csrftoken');
        const response = await fetch('/chatbot/add-document/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrf
            }
        });

        if (!response.ok) throw new Error('Failed to upload document');

        const result = await response.json();
        console.log('Document uploaded successfully:', result);

        addFileToList(file.name);

    } catch (error) {
        console.error('Error uploading document:', error);
    }
}

// Function to update content and refresh the document list
function updateContent(key, replace = true) {
    // Always replace the URL state to avoid adding to the history stack
    history.replaceState(null, '', `/chatbot/edit_bot/${key}`);
    console.log(`Content updated for bot key: ${key}`);
    fetchAndDisplayDocuments(key);
}

// Function to manage file uploads and deletions
function setupFileManagement() {
    const addPdfButton = document.getElementById('addPdfButton');
    const pdfInput = document.getElementById('pdfInput');

    addPdfButton.addEventListener('click', function () {
        pdfInput.click();
    });

    pdfInput.addEventListener('change', async function (event) {
        const file = event.target.files[0];
        if (file && (file.name.endsWith('.pdf') || file.name.endsWith('.csv'))) {
            await uploadDocument(file);
        }
    });
}

function updateSidebarLinks(key) {
    document.getElementById('chat-link').href = `/chatbot/start-bot/${key}`;
    document.getElementById('file-link').href = `/chatbot/edit_bot/${key}`;
    document.getElementById('setting-link').href = `/chatbot/hub/${key}`;
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