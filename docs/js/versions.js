/**
 * XO Game - Version History Management & Rendering
 * Shared release data consumer with category grouping (Added/Improved/Fixed),
 * bilingual localization (English / Arabic), dark/light theme support,
 * deep-linking (#v3.0.1), channel filtering, pagination, and safe HTML rendering.
 */

(function () {
  'use strict';

  // Configuration
  const PAGE_SIZE = 4;
  let allReleases = [];
  let currentFilter = 'all'; // 'all' | 'stable' | 'prerelease'
  let displayedCount = PAGE_SIZE;
  let targetTagFromUrl = '';

  // Utility: HTML Escaping
  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // Localized string helper
  function t(key, fallback) {
    if (window.XOI18n && typeof window.XOI18n.t === 'function') {
      const res = window.XOI18n.t(key);
      if (res && res !== key) return res;
    }
    return fallback !== undefined ? fallback : key;
  }

  // Format ISO Date localized
  function formatDate(isoStr) {
    if (!isoStr) return '';
    if (window.XOI18n && typeof window.XOI18n.formatDate === 'function') {
      return window.XOI18n.formatDate(isoStr);
    }
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

  // Parse Release Notes into structured categories
  function parseReleaseNotes(notesText) {
    if (!notesText) return { added: [], improved: [], fixed: [], general: [] };

    const categories = {
      added: [],
      improved: [],
      fixed: [],
      general: []
    };

    const lines = notesText.split('\n');
    let currentSection = 'general';

    for (let line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('## ') || trimmed.startsWith('# ')) {
        continue;
      }

      // Detect explicit markdown section headers
      if (trimmed.startsWith('### Added') || trimmed.startsWith('## Added')) {
        currentSection = 'added';
        continue;
      } else if (trimmed.startsWith('### Improved') || trimmed.startsWith('## Improved') || trimmed.startsWith('### Changed')) {
        currentSection = 'improved';
        continue;
      } else if (trimmed.startsWith('### Fixed') || trimmed.startsWith('## Fixed')) {
        currentSection = 'fixed';
        continue;
      } else if (trimmed.startsWith('### Changes') || trimmed.startsWith('### Notes')) {
        currentSection = 'general';
        continue;
      }

      // Check bullet items
      let content = trimmed;
      if (content.startsWith('* ') || content.startsWith('- ')) {
        content = content.substring(2).trim();
      }

      if (!content || content.startsWith('Changes since')) continue;

      // Classify conventional commit prefixes if present
      const lower = content.toLowerCase();
      if (lower.startsWith('feat:') || lower.startsWith('feat(') || lower.startsWith('add:')) {
        categories.added.push(cleanCommitPrefix(content));
      } else if (
        lower.startsWith('chore:') || lower.startsWith('chore(') ||
        lower.startsWith('ci:') || lower.startsWith('ci(') ||
        lower.startsWith('docs:') || lower.startsWith('docs(') ||
        lower.startsWith('refactor:') || lower.startsWith('perf:') || lower.startsWith('style:')
      ) {
        categories.improved.push(cleanCommitPrefix(content));
      } else if (lower.startsWith('fix:') || lower.startsWith('fix(') || lower.startsWith('bug:')) {
        categories.fixed.push(cleanCommitPrefix(content));
      } else {
        if (currentSection === 'added') {
          categories.added.push(cleanCommitPrefix(content));
        } else if (currentSection === 'improved') {
          categories.improved.push(cleanCommitPrefix(content));
        } else if (currentSection === 'fixed') {
          categories.fixed.push(cleanCommitPrefix(content));
        } else {
          categories.general.push(cleanCommitPrefix(content));
        }
      }
    }

    return categories;
  }

  function cleanCommitPrefix(line) {
    return line.replace(/^[0-9a-f]{7,8}\s+/, '');
  }

  function getDataUrls() {
    const isUnderVersions = window.location.pathname.includes('/versions');
    const prefix = isUnderVersions ? '../' : './';
    return {
      historyUrl: prefix + 'updates/releases.json',
      fallbackUrl: prefix + 'updates/version.json',
      rootUrl: prefix
    };
  }

  // Fetch release history
  async function loadReleaseData() {
    const urls = getDataUrls();
    const container = document.getElementById('releases-feed');
    if (!container) return;

    // Show loading skeleton
    container.innerHTML = `
      <div class="skeleton-card" aria-hidden="true">
        <div class="skeleton-line" style="width: 30%; height: 28px;"></div>
        <div class="skeleton-line" style="width: 50%;"></div>
        <div class="skeleton-line" style="width: 80%;"></div>
      </div>
      <div class="skeleton-card" aria-hidden="true">
        <div class="skeleton-line" style="width: 25%; height: 28px;"></div>
        <div class="skeleton-line" style="width: 60%;"></div>
        <div class="skeleton-line" style="width: 75%;"></div>
      </div>
    `;

    try {
      let data = null;
      let resp = await fetch(urls.historyUrl, { cache: 'no-cache' });
      if (resp.ok) {
        data = await resp.json();
      } else {
        // Try fallback to version.json
        resp = await fetch(urls.fallbackUrl, { cache: 'no-cache' });
        if (resp.ok) {
          const single = await resp.json();
          data = {
            schema_version: 1,
            latest_stable: single.channel === 'stable' ? single.version : '',
            releases: [single]
          };
        }
      }

      if (!data || !Array.isArray(data.releases) || data.releases.length === 0) {
        renderEmptyState();
        return;
      }

      allReleases = data.releases;
      extractTargetFromUrl();
      renderReleases();
    } catch (err) {
      console.error('Failed to load release data:', err);
      renderErrorState();
    }
  }

  function extractTargetFromUrl() {
    let hash = window.location.hash.trim().replace(/^#/, '');
    if (hash) {
      targetTagFromUrl = hash;
      return;
    }
    const params = new URLSearchParams(window.location.search);
    const v = params.get('v') || params.get('version');
    if (v) {
      targetTagFromUrl = v.startsWith('v') ? v : 'v' + v;
    }
  }

  function getFilteredReleases() {
    if (currentFilter === 'stable') {
      return allReleases.filter(r => r.channel === 'stable');
    } else if (currentFilter === 'prerelease') {
      return allReleases.filter(r => r.channel !== 'stable');
    }
    return allReleases;
  }

  // Render cards
  function renderReleases() {
    const container = document.getElementById('releases-feed');
    const paginationContainer = document.getElementById('pagination-container');
    if (!container) return;

    const filtered = getFilteredReleases();

    if (filtered.length === 0) {
      renderEmptyState();
      if (paginationContainer) paginationContainer.innerHTML = '';
      return;
    }

    if (targetTagFromUrl) {
      const targetIdx = filtered.findIndex(r => 
        r.tag_name === targetTagFromUrl || 
        r.version === targetTagFromUrl.replace(/^v/, '') ||
        'v' + r.version === targetTagFromUrl
      );
      if (targetIdx >= displayedCount) {
        displayedCount = targetIdx + 1;
      }
    }

    const toShow = filtered.slice(0, displayedCount);

    const latestStableEntry = allReleases.find(r => r.channel === 'stable');
    const latestStableTag = latestStableEntry ? latestStableEntry.tag_name : '';

    const htmlParts = toShow.map(release => {
      const isLatest = release.tag_name === latestStableTag;
      const isPrerelease = release.channel !== 'stable';
      const isTargeted = targetTagFromUrl && (
        release.tag_name === targetTagFromUrl || 
        release.version === targetTagFromUrl.replace(/^v/, '') ||
        'v' + release.version === targetTagFromUrl
      );

      const parsedNotes = parseReleaseNotes(release.release_notes);
      const downloadInfo = extractDownloadInfo(release);

      const stableLabel = t('badgeStable', 'Latest Stable');
      const prereleaseLabel = t('badgePrerelease', 'Prerelease');
      const linkLabel = t('copyPermalink', 'Link');
      const downloadLabel = t('downloadWindowsBtn', 'Download for Windows');
      const githubLabel = t('githubNotesBtn', 'GitHub Notes');

      return `
        <article 
          class="release-card ${isLatest ? 'is-latest-stable' : ''} ${isTargeted ? 'is-targeted' : ''}" 
          id="${escapeHtml(release.tag_name)}"
          data-version="${escapeHtml(release.version)}"
        >
          <header class="release-card-header">
            <div class="release-meta-main">
              <h2 class="release-version-heading">${escapeHtml(release.name || ('XO Game ' + release.tag_name))}</h2>
              ${isLatest ? `<span class="badge badge-stable"><span class="badge-dot"></span> ${escapeHtml(stableLabel)}</span>` : ''}
              ${isPrerelease ? `<span class="badge badge-prerelease"><span class="badge-dot"></span> ${escapeHtml(prereleaseLabel)}</span>` : ''}
              <time class="release-published-date" datetime="${escapeHtml(release.published_at)}">
                <i class="far fa-calendar-alt" aria-hidden="true"></i> ${formatDate(release.published_at)}
              </time>
            </div>
            <div class="release-header-actions">
              <button 
                class="copy-permalink-btn" 
                data-tag="${escapeHtml(release.tag_name)}"
                title="${escapeHtml(t('copyPermalinkAria', 'Copy direct link to this release'))}"
                aria-label="${escapeHtml(t('copyPermalinkAria', 'Copy direct link to this release'))}"
                type="button"
              >
                <i class="fas fa-link" aria-hidden="true"></i> <span class="btn-text">${escapeHtml(linkLabel)}</span>
              </button>
            </div>
          </header>

          <div class="release-notes-container">
            ${renderStructuredNotes(parsedNotes)}
          </div>

          <footer class="release-assets-bar">
            <div class="asset-details">
              ${downloadInfo.fileName ? `
                <span class="asset-pill" title="Package file name" dir="ltr">
                  <i class="fas fa-file-archive" aria-hidden="true"></i> ${escapeHtml(downloadInfo.fileName)}
                </span>
              ` : ''}
              ${downloadInfo.sha256 ? `
                <span class="asset-pill asset-sha256" title="SHA-256: ${escapeHtml(downloadInfo.sha256)}" dir="ltr">
                  <i class="fas fa-shield-alt" aria-hidden="true"></i> SHA-256: ${escapeHtml(downloadInfo.sha256.substring(0, 10))}...
                </span>
              ` : ''}
            </div>
            <div class="asset-actions">
              ${downloadInfo.downloadUrl ? `
                <a href="${escapeHtml(downloadInfo.downloadUrl)}" class="btn btn-primary btn-sm" download>
                  <i class="fas fa-download" aria-hidden="true"></i> <span>${escapeHtml(downloadLabel)}</span>
                </a>
              ` : ''}
              ${release.release_page_url ? `
                <a href="${escapeHtml(release.release_page_url)}" class="btn btn-secondary btn-sm" target="_blank" rel="noopener noreferrer">
                  <i class="fab fa-github" aria-hidden="true"></i> <span>${escapeHtml(githubLabel)}</span>
                </a>
              ` : ''}
            </div>
          </footer>
        </article>
      `;
    });

    container.innerHTML = htmlParts.join('');

    // Render Load More Pagination
    if (paginationContainer) {
      if (displayedCount < filtered.length) {
        const remaining = filtered.length - displayedCount;
        const loadMoreText = `${t('loadMoreBtn', 'Load More Releases')} (${remaining} ${t('remainingCount', 'remaining')})`;
        paginationContainer.innerHTML = `
          <button id="btn-load-more" class="btn btn-secondary" type="button">
            ${escapeHtml(loadMoreText)}
          </button>
        `;
        document.getElementById('btn-load-more').addEventListener('click', () => {
          displayedCount += PAGE_SIZE;
          renderReleases();
        });
      } else {
        paginationContainer.innerHTML = '';
      }
    }

    // Bind copy permalink buttons
    container.querySelectorAll('.copy-permalink-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const tag = btn.dataset.tag;
        const url = `${window.location.origin}${window.location.pathname}#${tag}`;
        const copiedText = t('copiedPermalink', 'Copied!');
        const defaultText = t('copyPermalink', 'Link');

        navigator.clipboard.writeText(url).then(() => {
          btn.classList.add('copied');
          btn.innerHTML = `<i class="fas fa-check" aria-hidden="true"></i> <span class="btn-text">${escapeHtml(copiedText)}</span>`;
          setTimeout(() => {
            btn.classList.remove('copied');
            btn.innerHTML = `<i class="fas fa-link" aria-hidden="true"></i> <span class="btn-text">${escapeHtml(defaultText)}</span>`;
          }, 2000);
        }).catch(() => {
          window.location.hash = tag;
        });
      });
    });

    // Scroll to targeted release if requested
    if (targetTagFromUrl) {
      const el = document.getElementById(targetTagFromUrl);
      if (el) {
        setTimeout(() => {
          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 120);
      }
    }
  }

  function extractDownloadInfo(release) {
    if (release.platforms && release.platforms.windows) {
      return {
        downloadUrl: release.platforms.windows.download_url || '',
        fileName: release.platforms.windows.file_name || '',
        sha256: release.platforms.windows.sha256 || ''
      };
    }
    return { downloadUrl: '', fileName: '', sha256: '' };
  }

  function renderStructuredNotes(parsed) {
    const hasStructured = parsed.added.length > 0 || parsed.improved.length > 0 || parsed.fixed.length > 0;

    if (!hasStructured && parsed.general.length === 0) {
      return `<p class="raw-notes-body">${escapeHtml(t('noNotes', 'No detailed release notes provided for this build.'))}</p>`;
    }

    let out = '';

    if (parsed.added.length > 0) {
      out += `
        <section class="release-category">
          <h3 class="category-header added"><i class="fas fa-plus-circle" aria-hidden="true"></i> ${escapeHtml(t('categoryAdded', 'Added'))}</h3>
          <ul class="category-list">
            ${parsed.added.map(item => `<li>${escapeHtml(item)}</li>`).join('')}
          </ul>
        </section>
      `;
    }

    if (parsed.improved.length > 0) {
      out += `
        <section class="release-category">
          <h3 class="category-header improved"><i class="fas fa-arrow-circle-up" aria-hidden="true"></i> ${escapeHtml(t('categoryImproved', 'Improved'))}</h3>
          <ul class="category-list">
            ${parsed.improved.map(item => `<li>${escapeHtml(item)}</li>`).join('')}
          </ul>
        </section>
      `;
    }

    if (parsed.fixed.length > 0) {
      out += `
        <section class="release-category">
          <h3 class="category-header fixed"><i class="fas fa-wrench" aria-hidden="true"></i> ${escapeHtml(t('categoryFixed', 'Fixed'))}</h3>
          <ul class="category-list">
            ${parsed.fixed.map(item => `<li>${escapeHtml(item)}</li>`).join('')}
          </ul>
        </section>
      `;
    }

    if (parsed.general.length > 0) {
      out += `
        <section class="release-category">
          <h3 class="category-header"><i class="fas fa-list-ul" aria-hidden="true"></i> ${escapeHtml(t('categoryChanges', 'Changes'))}</h3>
          <ul class="category-list">
            ${parsed.general.map(item => `<li>${escapeHtml(item)}</li>`).join('')}
          </ul>
        </section>
      `;
    }

    return out;
  }

  function renderEmptyState() {
    const container = document.getElementById('releases-feed');
    if (!container) return;
    container.innerHTML = `
      <div class="state-box">
        <div class="state-icon"><i class="fas fa-tag" aria-hidden="true"></i></div>
        <h3 class="state-title">${escapeHtml(t('emptyTitle', 'No Releases Found'))}</h3>
        <p class="state-desc">${escapeHtml(t('emptyDesc', 'There are no releases available matching your selected channel filter.'))}</p>
      </div>
    `;
  }

  function renderErrorState() {
    const container = document.getElementById('releases-feed');
    if (!container) return;
    container.innerHTML = `
      <div class="state-box">
        <div class="state-icon" style="color: var(--color-o);"><i class="fas fa-exclamation-triangle" aria-hidden="true"></i></div>
        <h3 class="state-title">${escapeHtml(t('errorTitle', 'Unable to Load Releases'))}</h3>
        <p class="state-desc">${escapeHtml(t('errorDesc', 'Could not retrieve the release history data. Please check your connection or inspect releases.json.'))}</p>
        <button class="btn btn-secondary" onclick="window.location.reload()" type="button">
          <i class="fas fa-redo-alt" aria-hidden="true"></i> ${escapeHtml(t('retryBtn', 'Retry'))}
        </button>
      </div>
    `;
  }

  // Filter tabs click binding
  function initFilterTabs() {
    const tabs = document.querySelectorAll('.filter-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => {
          t.classList.remove('active');
          t.setAttribute('aria-selected', 'false');
        });
        tab.classList.add('active');
        tab.setAttribute('aria-selected', 'true');
        currentFilter = tab.dataset.filter;
        displayedCount = PAGE_SIZE;
        renderReleases();
      });
    });
  }

  // Theme Switcher for Version History Page
  function initTheme() {
    const themeBtn = document.getElementById('theme-toggle-btn');
    if (!themeBtn) return;

    function applyTheme(theme) {
      const isDark = theme === 'dark';
      document.documentElement.setAttribute('data-theme', theme);
      try {
        localStorage.setItem('xo_theme', theme);
      } catch (e) {}

      const title = t(isDark ? 'themeToggleLight' : 'themeToggleDark', isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode');
      themeBtn.setAttribute('title', title);
      themeBtn.setAttribute('aria-label', title);
      themeBtn.setAttribute('aria-pressed', isDark ? 'true' : 'false');
      themeBtn.innerHTML = isDark
        ? '<i class="fas fa-sun" aria-hidden="true"></i>'
        : '<i class="fas fa-moon" aria-hidden="true"></i>';
    }

    let saved = null;
    try {
      saved = localStorage.getItem('xo_theme');
    } catch (e) {}

    const preferredTheme = saved || (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    applyTheme(preferredTheme);

    themeBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      applyTheme(next);
    });
  }

  // Mobile menu hamburger toggle
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
  }

  // Re-render releases on language change
  if (window.XOI18n && typeof window.XOI18n.onLanguageChange === 'function') {
    window.XOI18n.onLanguageChange(() => {
      renderReleases();
    });
  }

  // Initialize
  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initMobileMenu();
    initFilterTabs();
    loadReleaseData();
  });
})();
