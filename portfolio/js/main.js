   document.addEventListener('DOMContentLoaded', () => {
     initMobileNav();
     highlightActiveLink();
     initCopyButtons();
   });
   
   /* ---- Mobile Nav Toggle ---- */
   function initMobileNav() {
     const hamburger = document.querySelector('.hamburger');
     const navLinks = document.querySelector('.nav-links');
   
     if (!hamburger || !navLinks) return;
   
     hamburger.addEventListener('click', () => {
       hamburger.classList.toggle('active');
       navLinks.classList.toggle('active');
     });
   
     // Close nav when a link is clicked
     navLinks.querySelectorAll('a').forEach(link => {
       link.addEventListener('click', () => {
         hamburger.classList.remove('active');
         navLinks.classList.remove('active');
       });
     });
   }
   
   /* ---- Active Link Highlighting ---- */
   function highlightActiveLink() {
     let currentFile = window.location.pathname.split('/').pop();
     if (!currentFile) currentFile = 'index.html';

     const onProjectSubpage = window.location.pathname.includes('/projects/');

     const navLinks = document.querySelectorAll('.nav-links a');

     navLinks.forEach(link => {
       const linkFile = link.getAttribute('href').split('/').pop();

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
       copyBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`;
       copyBtn.title = 'Copy to clipboard';
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
           copyBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--success)" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>`;
           setTimeout(() => {
             copyBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`;
           }, 1500);
         } catch (err) {
           console.error('Copy failed:', err);
         }
       });
     });
   }