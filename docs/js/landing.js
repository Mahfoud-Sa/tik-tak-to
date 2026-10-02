/**
 * XO Game - Landing Page Interactions, Theme Engine & Release Hydration
 */

(function () {
  'use strict';

  // Cached latest release data
  let cachedLatestRelease = null;

  // Hydrate latest stable version from shared updates/releases.json
  async function hydrateLatestRelease() {
    try {
      let latestStable = null;
      let resp = await fetch('updates/releases.json', { cache: 'no-cache' });
      if (resp.ok) {
        const data = await resp.json();
        if (data.releases && data.releases.length > 0) {
          latestStable = data.releases.find(r => r.channel === 'stable') || data.releases[0];
        }
      } else {
        // Fallback to version.json
        resp = await fetch('updates/version.json', { cache: 'no-cache' });
        if (resp.ok) {
          latestStable = await resp.json();
        }
      }

      if (!latestStable) return;
      cachedLatestRelease = latestStable;
      renderReleaseData(latestStable);
    } catch (e) {
      console.warn('Could not hydrate latest release info:', e);
    }
  }

  function renderReleaseData(release) {
    if (!release) return;

    const tag = release.tag_name || `v${release.version}`;
    const pubDate = window.XOI18n 
      ? window.XOI18n.formatDate(release.published_at)
      : (release.published_at ? new Date(release.published_at).toLocaleDateString() : '');
    const downloadUrl = release.platforms?.windows?.download_url || 
      `https://github.com/Mahfoud-Sa/tik-tak-to/releases/download/${tag}/XO_Game-${tag}-windows-x64.zip`;
    const fileName = release.platforms?.windows?.file_name || `XO_Game-${tag}-windows-x64.zip`;
    const sha256 = release.platforms?.windows?.sha256 || '';

    // 1. Hero Version Pill
    const heroPill = document.getElementById('hero-version-pill');
    if (heroPill) {
      const prefix = window.XOI18n ? window.XOI18n.t('heroPillPrefix') : 'Latest Stable: ';
      heroPill.innerHTML = `
        <span class="badge badge-stable"><span class="badge-dot"></span> <span class="pill-prefix">${prefix}</span><strong>${tag}</strong></span>
        <span class="pill-date">${pubDate}</span>
        <i class="fas fa-chevron-right icon-flip-rtl" style="font-size: 0.75rem;" aria-hidden="true"></i>
      `;
      heroPill.setAttribute('href', `versions/#${tag}`);
    }

    // 2. Latest Release Highlight Card
    const relTagTitle = document.getElementById('latest-release-tag');
    if (relTagTitle) {
      relTagTitle.textContent = release.name || `XO Game ${tag}`;
    }

    const relDate = document.getElementById('latest-release-date');
    if (relDate) {
      relDate.textContent = pubDate;
      if (release.published_at) {
        relDate.setAttribute('datetime', release.published_at);
      }
    }

    const relLinkNotes = document.getElementById('latest-release-notes-link');
    if (relLinkNotes) {
      relLinkNotes.setAttribute('href', `versions/#${tag}`);
    }

    const relDownloadBtn = document.getElementById('btn-download-latest');
    if (relDownloadBtn) {
      relDownloadBtn.setAttribute('href', downloadUrl);
      relDownloadBtn.setAttribute('download', fileName);
    }

    const relFileName = document.getElementById('latest-release-filename');
    if (relFileName) {
      relFileName.innerHTML = `<i class="fas fa-file-archive" aria-hidden="true"></i> <span>${fileName}</span>`;
    }

    const relSha = document.getElementById('latest-release-sha');
    if (relSha) {
      if (sha256) {
        relSha.innerHTML = `<i class="fas fa-shield-alt" aria-hidden="true"></i> <span>SHA-256: ${sha256.substring(0, 10)}...</span>`;
        relSha.setAttribute('title', `SHA-256: ${sha256}`);
        relSha.style.display = 'inline-flex';
      } else {
        relSha.style.display = 'none';
      }
    }
  }

  // Connect "Play Now" primary buttons to the actual playable game
  function initPlayNowTriggers() {
    const playButtons = document.querySelectorAll('.trigger-play-now');
    const gameSection = document.getElementById('play-arena');

    playButtons.forEach(btn => {
      btn.addEventListener('click', e => {
        e.preventDefault();
        if (gameSection) {
          gameSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
          if (window.XOGame && typeof window.XOGame.focusBoard === 'function') {
            setTimeout(() => {
              window.XOGame.focusBoard();
            }, 400);
          }
        }
      });
    });
  }

  // Mobile navigation hamburger toggle
  function initMobileMenu() {
    const btn = document.getElementById('mobile-menu-btn');
    const menu = document.getElementById('nav-links');
    if (!btn || !menu) return;

    btn.addEventListener('click', () => {
      const isOpen = menu.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      btn.innerHTML = isOpen
        ? '<i class="fas fa-times" aria-hidden="true"></i>'
        : '<i class="fas fa-bars" aria-hidden="true"></i>';
    });

    // Close when clicking a link
    menu.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        menu.classList.remove('is-open');
        btn.setAttribute('aria-expanded', 'false');
        btn.innerHTML = '<i class="fas fa-bars" aria-hidden="true"></i>';
      });
    });
  }

  // Playful Interactive Hero Grid
  function initHeroPreviewGrid() {
    const cells = document.querySelectorAll('.preview-cell');
    let turn = 'X';

    cells.forEach(cell => {
      cell.addEventListener('click', () => {
        if (!cell.textContent.trim()) {
          cell.textContent = turn;
          cell.className = `preview-cell cell-${turn.toLowerCase()}`;
          turn = turn === 'X' ? 'O' : 'X';
        } else {
          cell.textContent = '';
          cell.className = 'preview-cell';
        }
      });
    });
  }

  // Theme Switcher (Light / Dark)
  function initTheme() {
    const themeBtn = document.getElementById('theme-toggle-btn');
    if (!themeBtn) return;

    function applyTheme(theme) {
      const isDark = theme === 'dark';
      document.documentElement.setAttribute('data-theme', theme);
      try {
        localStorage.setItem('xo_theme', theme);
      } catch (e) {}

      // Update button icon & tooltip
      const title = window.XOI18n 
        ? window.XOI18n.t(isDark ? 'themeToggleLight' : 'themeToggleDark')
        : (isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode');
      themeBtn.setAttribute('title', title);
      themeBtn.setAttribute('aria-label', title);
      themeBtn.setAttribute('aria-pressed', isDark ? 'true' : 'false');
      themeBtn.innerHTML = isDark
        ? '<i class="fas fa-sun" aria-hidden="true"></i>'
        : '<i class="fas fa-moon" aria-hidden="true"></i>';
    }

    // Determine initial theme: saved in localStorage or system preference
    let saved = null;
    try {
      saved = localStorage.getItem('xo_theme');
    } catch (e) {}

    const preferredTheme = saved || (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    applyTheme(preferredTheme);

    // Listen for system theme changes if user hasn't explicitly set one
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        try {
          if (!localStorage.getItem('xo_theme')) {
            applyTheme(e.matches ? 'dark' : 'light');
          }
        } catch (err) {}
      });
    }

    themeBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      applyTheme(next);
    });
  }

  // Clone command copy button with localized feedback
  function initCloneCopy() {
    const copyBtn = document.getElementById('btn-copy-clone');
    const commandText = document.getElementById('clone-command-text');
    if (!copyBtn || !commandText) return;

    copyBtn.addEventListener('click', async () => {
      const textToCopy = commandText.textContent.trim();
      const defaultText = window.XOI18n ? window.XOI18n.t('osCopyBtn') : 'Copy';
      const successText = window.XOI18n ? window.XOI18n.t('osCopiedFeedback') : 'Copied!';
      const errorText = window.XOI18n ? window.XOI18n.t('osCopyError') : 'Failed to copy';

      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(textToCopy);
        } else {
          // Fallback textarea method
          const ta = document.createElement('textarea');
          ta.value = textToCopy;
          ta.style.position = 'fixed';
          ta.style.left = '-9999px';
          ta.style.top = '-9999px';
          document.body.appendChild(ta);
          ta.focus();
          ta.select();
          document.execCommand('copy');
          ta.remove();
        }

        // Success visual feedback
        copyBtn.classList.add('btn-copy-success');
        copyBtn.innerHTML = `<i class="fas fa-check" aria-hidden="true"></i> <span>${successText}</span>`;
        copyBtn.setAttribute('aria-live', 'polite');

        setTimeout(() => {
          copyBtn.classList.remove('btn-copy-success');
          copyBtn.innerHTML = `<i class="fas fa-copy" aria-hidden="true"></i> <span>${defaultText}</span>`;
        }, 2200);
      } catch (err) {
        copyBtn.classList.add('btn-copy-error');
        copyBtn.innerHTML = `<i class="fas fa-exclamation-triangle" aria-hidden="true"></i> <span>${errorText}</span>`;
        setTimeout(() => {
          copyBtn.classList.remove('btn-copy-error');
          copyBtn.innerHTML = `<i class="fas fa-copy" aria-hidden="true"></i> <span>${defaultText}</span>`;
        }, 2200);
      }
    });
  }

  // Hook into language change events to re-render dynamic release dates and copy button state
  if (window.XOI18n && typeof window.XOI18n.onLanguageChange === 'function') {
    window.XOI18n.onLanguageChange(() => {
      if (cachedLatestRelease) {
        renderReleaseData(cachedLatestRelease);
      }
      const copyBtn = document.getElementById('btn-copy-clone');
      if (copyBtn && !copyBtn.classList.contains('btn-copy-success')) {
        const defaultText = window.XOI18n.t('osCopyBtn');
        copyBtn.innerHTML = `<i class="fas fa-copy" aria-hidden="true"></i> <span>${defaultText}</span>`;
      }
    });
  }

  // Initialize all landing interactions
  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initPlayNowTriggers();
    initMobileMenu();
    initHeroPreviewGrid();
    initCloneCopy();
    hydrateLatestRelease();
  });
})();
