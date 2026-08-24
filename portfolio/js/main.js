document.addEventListener('DOMContentLoaded', () => {
  initMobileNav();
  highlightActiveLink();
  initCopyButtons();
  initContactForm();
});


function initMobileNav() {
  const hamburger = document.querySelector('.hamburger');
  const navLinks = document.querySelector('.nav-links');

  if (!hamburger || !navLinks) return;

  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navLinks.classList.toggle('active');
  });

  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      hamburger.classList.remove('active');
      navLinks.classList.remove('active');
    });
  });
}


function highlightActiveLink() {
  let currentFile = window.location.pathname.split('/').pop();

  if (!currentFile) {
    currentFile = 'index.html';
  }

  const onProjectSubpage =
    window.location.pathname.includes('/projects/');

  const navLinks = document.querySelectorAll('.nav-links a');

  navLinks.forEach(link => {
    const href = link.getAttribute('href');

    if (!href) return;

    const linkFile = href.split('/').pop();

    const isMatch =
      linkFile === currentFile ||
      (onProjectSubpage && linkFile === 'projects.html');

    link.classList.toggle('active', isMatch);
  });
}


function initCopyButtons() {
  const terminals = document.querySelectorAll('.terminal');

  terminals.forEach(terminal => {
    const copyBtn = document.createElement('button');

    copyBtn.className = 'terminal-copy';

    copyBtn.innerHTML = `
      <svg
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <rect
          x="9"
          y="9"
          width="13"
          height="13"
          rx="2"
        />
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
      </svg>
    `;

    copyBtn.title = 'Copy to clipboard';
    copyBtn.setAttribute('aria-label', 'Copy code to clipboard');

    copyBtn.style.cssText = `
      position: absolute;
      top: 8px;
      right: 12px;
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      padding: 4px;
      border-radius: 4px;
      transition: color 0.2s ease, background 0.2s ease;
      opacity: 0;
    `;

    terminal.style.position = 'relative';
    terminal.appendChild(copyBtn);

    terminal.addEventListener('mouseenter', () => {
      copyBtn.style.opacity = '1';
    });

    terminal.addEventListener('mouseleave', () => {
      copyBtn.style.opacity = '0';
    });

    copyBtn.addEventListener('mouseenter', () => {
      copyBtn.style.color = 'var(--accent)';
      copyBtn.style.background = 'var(--bg-tertiary)';
    });

    copyBtn.addEventListener('mouseleave', () => {
      copyBtn.style.color = 'var(--text-muted)';
      copyBtn.style.background = 'transparent';
    });

    copyBtn.addEventListener('click', async () => {
      const body = terminal.querySelector('.terminal-body');

      if (!body) return;

      const text = body.innerText;

      try {
        await navigator.clipboard.writeText(text);

        copyBtn.innerHTML = `
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="var(--success)"
            stroke-width="2"
          >
            <polyline points="20 6 9 17 4 12" />
          </svg>
        `;

        setTimeout(() => {
          copyBtn.innerHTML = `
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <rect
                x="9"
                y="9"
                width="13"
                height="13"
                rx="2"
              />
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
            </svg>
          `;
        }, 1500);

      } catch (error) {
        console.error('Copy failed:', error);
      }
    });
  });
}

function initContactForm() {
  const form = document.getElementById('contact-form');
  const status = document.getElementById('status');

  // Nothing to do on pages without the contact form
  if (!form || !status) return;

  const submitButton = form.querySelector('button[type="submit"]');

  if (typeof emailjs === 'undefined') {
    status.textContent =
      'Contact service is temporarily unavailable. Please email me directly.';
    status.style.color = 'var(--warning)';
    return;
  }

  emailjs.init({
    publicKey: 'lsK6jIOL_by4JhlqX',
  });

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    const nameField = form.querySelector('[name="name"]');
    const messageField = form.querySelector('[name="message"]');

    if (
      !nameField ||
      !messageField ||
      !nameField.value.trim() ||
      !messageField.value.trim()
    ) {
      status.textContent = 'Please complete all fields.';
      status.style.color = 'var(--danger)';
      return;
    }

    if (submitButton) {
      submitButton.disabled = true;
      submitButton.setAttribute('aria-busy', 'true');
    }

    status.textContent = 'Sending...';
    status.style.color = 'var(--text-muted)';

    try {
      await emailjs.sendForm(
        'service_0efmmjl',
        'template_zel4e1f',
        form
      );

      status.textContent = 'Message sent successfully!';
      status.style.color = 'var(--success)';

      form.reset();

    } catch (error) {
      status.textContent =
        'Failed to send message. Please email me directly instead.';

      status.style.color = 'var(--danger)';

      console.error('EmailJS error:', error);

    } finally {

      if (submitButton) {
        submitButton.disabled = false;
        submitButton.removeAttribute('aria-busy');
      }
    }
  });
}