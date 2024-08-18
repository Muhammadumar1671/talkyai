function DashboardPage() {
    window.location.href = "/chatbot/";
}


document.addEventListener('DOMContentLoaded', async () => {
    fetchData();


    async function fetchData() {
        const response = await fetch('/chatbot/analytics', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
    
        const data = await response.json();
        console.log(data);
    
        // Populate the containers with the received data
        animateCounter('userCount', data.user_count);
        animateCounter('totalQuestions', data.total_question);
        animateCounter('totalResponses', data.total_response);
    }

    function animateCounter(id, finalValue) {
        const element = document.getElementById(id);
        let currentValue = 0;
        const duration = 1000; // 1 second
        const intervalTime = 50; // Update every 50ms
        const increment = Math.ceil(finalValue / (duration / intervalTime));
    
        const counter = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                currentValue = finalValue;
                clearInterval(counter);
            }
            element.innerText = currentValue;
        }, intervalTime);
    }
    
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
});
