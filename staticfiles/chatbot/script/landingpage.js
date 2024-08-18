
function toggleTheme() {
    const body = document.body;
    const themeButton = document.getElementById('toggle-theme');
    const sunIcon = '<i class="fas fa-sun"></i>';
    const moonIcon = '<i class="fas fa-moon"></i>';
    
    if (body.classList.contains('dark-mode')) {
        body.classList.remove('dark-mode');
        body.classList.add('light-mode');
        themeButton.innerHTML = moonIcon;
    } else {
        body.classList.remove('light-mode');
        body.classList.add('dark-mode');
        themeButton.innerHTML = sunIcon;
    }
}
function DashboardPage() {
    window.location.href = "/chatbot/dashboard";
}
function CreateBot() {
    window.location.href = "/chatbot/create_bot/";
}
