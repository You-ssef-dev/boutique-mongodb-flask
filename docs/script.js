document.addEventListener('DOMContentLoaded', () => {
    // --- Smooth Scroll for TOC ---
    const links = document.querySelectorAll('.docs-nav a');

    links.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);

            if (targetSection) {
                // Offset for fixed header
                const headerOffset = 100;
                const elementPosition = targetSection.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: "smooth"
                });

                // Update active state manually immediately
                links.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            }
        });
    });

    // --- Active Link on Scroll (ScrollSpy) ---
    const sections = document.querySelectorAll('.doc-section');
    const navItems = document.querySelectorAll('.docs-nav a');

    const observerOptions = {
        root: null,
        rootMargin: '-20% 0px -60% 0px', // Trigger when section is in the upper middle
        threshold: 0
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.getAttribute('id');
                navItems.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${id}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }, observerOptions);

    sections.forEach(section => observer.observe(section));

    // --- Copy Code Feature ---
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const codeBlock = btn.closest('.code-block-wrapper').querySelector('code');
            const code = codeBlock.innerText;

            navigator.clipboard.writeText(code).then(() => {
                const icon = btn.querySelector('i');
                const originalClass = icon.className;

                icon.className = 'bx bx-check';
                setTimeout(() => {
                    icon.className = originalClass;
                }, 2000);
            });
        });
    });
});
