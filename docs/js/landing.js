/**
 * XO Game - Landing Page Interactions & Shared Release Data Hydration
 */

(function () {
  'use strict';

  // Format Date Helper
  function formatDate(isoStr) {
    if (!isoStr) return '';
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch (e) {
      return isoStr;
    }
  }

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

      const tag = latestStable.tag_name || `v${latestStable.version}`;
      const versionNumber = latestStable.version;
      const pubDate = formatDate(latestStable.published_at);
      const downloadUrl = latestStable.platforms?.windows?.download_url || 
        `https://github.com/Mahfoud-Sa/tik-tak-to/releases/download/${tag}/XO_Game-${tag}-windows-x64.zip`;
      const fileName = latestStable.platforms?.windows?.file_name || `XO_Game-${tag}-windows-x64.zip`;
      const sha256 = latestStable.platforms?.windows?.sha256 || '';

      // 1. Hero Version Pill
      const heroPill = document.getElementById('hero-version-pill');
      if (heroPill) {
        heroPill.innerHTML = `
          <span class="badge badge-stable"><span class="badge-dot"></span> Latest Stable: ${tag}</span>
          <span class="pill-date">${pubDate}</span>
          <i class="fas fa-chevron-right" style="font-size: 0.75rem;" aria-hidden="true"></i>
        `;
        heroPill.setAttribute('href', `versions/#${tag}`);
      }

      // 2. Latest Release Highlight Card
      const relTagTitle = document.getElementById('latest-release-tag');
      if (relTagTitle) relTagTitle.textContent = latestStable.name || `XO Game ${tag}`;

      const relDate = document.getElementById('latest-release-date');
      if (relDate) relDate.textContent = pubDate;

      const relLinkNotes = document.getElementById('latest-release-notes-link');
      if (relLinkNotes) relLinkNotes.setAttribute('href', `versions/#${tag}`);

      const relDownloadBtn = document.getElementById('btn-download-latest');
      if (relDownloadBtn) {
        relDownloadBtn.setAttribute('href', downloadUrl);
        relDownloadBtn.setAttribute('download', fileName);
      }

      const relFileName = document.getElementById('latest-release-filename');
      if (relFileName) relFileName.textContent = fileName;

      const relSha = document.getElementById('latest-release-sha');
      if (relSha && sha256) {
        relSha.textContent = `SHA-256: ${sha256.substring(0, 12)}...`;
        relSha.style.display = 'inline-block';
      }
    } catch (e) {
      console.warn('Could not hydrate latest release info:', e);
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
            }, 450);
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
        if (!cell.textContent) {
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

  // Initialize
  document.addEventListener('DOMContentLoaded', () => {
    initPlayNowTriggers();
    initMobileMenu();
    initHeroPreviewGrid();
    hydrateLatestRelease();
  });
})();
