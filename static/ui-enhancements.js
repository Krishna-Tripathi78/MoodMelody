document.addEventListener('DOMContentLoaded', function() {
    animateElements();
    enhanceButtons();
    addScrollAnimations();
    enhanceMessages();
});

function animateElements() {
    const sidebarElements = document.querySelectorAll('.sidebar > div');
    if (sidebarElements) {
        sidebarElements.forEach((el, index) => {
            el.classList.add('animate__animated', 'animate__fadeInUp');
            el.style.animationDelay = `${index * 0.1}s`;
        });
    }
    
    const logo = document.querySelector('.logo');
    if (logo) {
        logo.addEventListener('mouseenter', () => {
            logo.classList.add('animate__animated', 'animate__pulse');
            setTimeout(() => {
                logo.classList.remove('animate__animated', 'animate__pulse');
            }, 1000);
        });
    }
}

function enhanceButtons() {
    const buttons = document.querySelectorAll('button');
    if (buttons) {
        buttons.forEach(button => {
            button.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
            });
            
            button.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });
    }
    
    const musicBtn = document.getElementById('getson');
    if (musicBtn) {
        musicBtn.addEventListener('click', function() {
            this.classList.add('animate__animated', 'animate__rubberBand');
            setTimeout(() => {
                this.classList.remove('animate__animated', 'animate__rubberBand');
            }, 1000);
        });
    }
}

function addScrollAnimations() {
    const chatbox = document.getElementById('chatbox');
    if (chatbox) {
        const scrollToBottom = () => {
            chatbox.scrollTop = chatbox.scrollHeight;
        };
        
        const observer = new MutationObserver(scrollToBottom);
        observer.observe(chatbox, { childList: true });
    }
}

function enhanceMessages() {
    const chatbox = document.getElementById('chatbox');
    if (chatbox) {
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                if (mutation.addedNodes.length) {
                    mutation.addedNodes.forEach(node => {
                        if (node.classList && node.classList.contains('bot-message') && 
                            !node.classList.contains('typing')) {
                            const content = node.querySelector('.message-content p');
                            if (content && content.textContent.length > 0) {
                                const text = content.textContent;
                                content.textContent = '';
                                typeText(content, text);
                            }
                        }
                    });
                }
            });
        });
        
        observer.observe(chatbox, { childList: true });
    }
}

function typeText(element, text, speed = 30) {
    if (!element || !text) return;
    
    let i = 0;
    const timer = setInterval(() => {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
        } else {
            clearInterval(timer);
        }
    }, speed);
}