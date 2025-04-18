// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Sticky header
const header = document.querySelector('header');
const heroSection = document.querySelector('#hero');

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (!entry.isIntersecting) {
            header.classList.add('sticky');
        } else {
            header.classList.remove('sticky');
        }
    });
}, { threshold: 0 });

observer.observe(heroSection);

// Feature cards animation
const featureCards = document.querySelectorAll('.feature-card');

const featureObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate');
        }
    });
}, { threshold: 0.1 });

featureCards.forEach(card => {
    featureObserver.observe(card);
});

// Demo section instructions toggle
const demoInstructions = document.querySelector('.demo-instructions');
const demoWindow = document.querySelector('.demo-window');

function toggleDemoInstructions() {
    demoInstructions.classList.toggle('collapsed');
    demoWindow.classList.toggle('expanded');
}

// Add event listener for mobile view
if (window.innerWidth <= 768) {
    demoInstructions.addEventListener('click', toggleDemoInstructions);
}

// Code copy functionality
document.querySelectorAll('code').forEach(codeBlock => {
    codeBlock.addEventListener('click', () => {
        const text = codeBlock.textContent;
        navigator.clipboard.writeText(text).then(() => {
            const originalText = codeBlock.textContent;
            codeBlock.textContent = 'Copied!';
            setTimeout(() => {
                codeBlock.textContent = originalText;
            }, 2000);
        });
    });
});

// Add loading animation for demo iframe
const demoIframe = document.querySelector('.demo-window iframe');
if (demoIframe) {
    demoIframe.addEventListener('load', () => {
        demoIframe.style.opacity = '1';
    });
    demoIframe.style.opacity = '0';
    demoIframe.style.transition = 'opacity 0.5s ease-in-out';
} 