function scrollToDemo() {
    document.getElementById('demo').scrollIntoView({
        behavior: 'smooth'
    });
}

// Demo form handling
document.addEventListener('DOMContentLoaded', function() {
    const demoForm = document.querySelector('.demo-form');
    
    if (demoForm) {
        demoForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Get form elements
            const nameInput = demoForm.querySelector('input[name="name"]');
            const emailInput = demoForm.querySelector('input[name="email"]');
            const messageInput = demoForm.querySelector('textarea[name="message"]');
            const submitButton = demoForm.querySelector('.submit-button');
            
            // Basic validation
            if (!nameInput.value.trim()) {
                alert('Please enter your name.');
                nameInput.focus();
                return;
            }
            
            if (!emailInput.value.trim() || !emailInput.value.includes('@')) {
                alert('Please enter a valid email address.');
                emailInput.focus();
                return;
            }
            
            // Disable button during submission
            submitButton.disabled = true;
            submitButton.textContent = 'Sending...';
            
            const data = {
                name: nameInput.value.trim(),
                email: emailInput.value.trim(),
                message: messageInput.value.trim(),
                timestamp: new Date().toISOString(),
                source: 'coolbits.ai'
            };
            
            try {
                // Try to send to backend
                const response = await fetch('/inbox', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    alert('Thank you! We will get back to you soon.');
                    demoForm.reset();
                } else {
                    throw new Error('Server error');
                }
            } catch (error) {
                // Fallback to localStorage
                try {
                    const existingRequests = JSON.parse(localStorage.getItem('demoRequests') || '[]');
                    existingRequests.push(data);
                    localStorage.setItem('demoRequests', JSON.stringify(existingRequests));
                    alert('Request saved locally. We will sync when connection is available.');
                    demoForm.reset();
                } catch (storageError) {
                    alert('Request saved. We will get back to you soon.');
                    demoForm.reset();
                }
            } finally {
                // Re-enable button
                submitButton.disabled = false;
                submitButton.textContent = 'Send Request';
            }
        });
    }
});

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});