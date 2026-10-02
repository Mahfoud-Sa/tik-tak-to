/**
 * XO Game - Version History Management & Rendering
 * Shared release data consumer with category grouping (Added/Improved/Fixed),
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

  // Format ISO Date: e.g. "October 2, 2026"
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

  // Format File Size
  function formatBytes(bytes) {
    if (!bytes || isNaN(bytes)) return '';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return parseFloat((bytes / Math.pow(1024, i)).toFixed(1)) + ' ' + sizes[i];
  }

  /**
   * Parse Release Notes into structured categories: Added, Improved, Fixed
   */
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
        // Place in current explicit section or general
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

  // Strip git hash or redundant prefix markers if present
  function cleanCommitPrefix(line) {
    // e.g. "3bbd6bc chore(release): ..." -> "chore(release): ..."
    return line.replace(/^[0-9a-f]{7,8}\s+/, '');
  }

  // Determine relative data URL based on current path
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

      // Extract target tag from URL hash or query param (e.g. #v3.0.1 or ?v=3.0.1)
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

  // Filter releases by channel
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

    // If an individual release was linked, make sure it is within displayed count
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

    // Identify latest stable version across all releases
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

      return `
        <article 
          class="release-card ${isLatest ? 'is-latest-stable' : ''} ${isTargeted ? 'is-targeted' : ''}" 
          id="${escapeHtml(release.tag_name)}"
          data-version="${escapeHtml(release.version)}"
        >
          <header class="release-card-header">
            <div class="release-meta-main">
              <h2 class="release-version-heading">${escapeHtml(release.name || ('XO Game ' + release.tag_name))}</h2>
              ${isLatest ? '<span class="badge badge-stable"><span class="badge-dot"></span> Latest Stable</span>' : ''}
              ${isPrerelease ? '<span class="badge badge-prerelease"><span class="badge-dot"></span> Prerelease</span>' : ''}
              <time class="release-published-date" datetime="${escapeHtml(release.published_at)}">
                <i class="far fa-calendar-alt" aria-hidden="true"></i> ${formatDate(release.published_at)}
              </time>
            </div>
            <div class="release-header-actions">
              <button 
                class="copy-permalink-btn" 
                data-tag="${escapeHtml(release.tag_name)}"
                title="Copy direct link to this release"
                aria-label="Copy direct link to ${escapeHtml(release.tag_name)}"
              >
                <i class="fas fa-link" aria-hidden="true"></i> Link
              </button>
            </div>
          </header>

          <div class="release-notes-container">
            ${renderStructuredNotes(parsedNotes)}
          </div>

          <footer class="release-assets-bar">
            <div class="asset-details">
              ${downloadInfo.fileName ? `
                <span class="asset-pill" title="Package file name">
                  <i class="fas fa-file-archive" aria-hidden="true"></i> ${escapeHtml(downloadInfo.fileName)}
                </span>
              ` : ''}
              ${downloadInfo.sha256 ? `
                <span class="asset-pill asset-sha256" title="SHA-256: ${escapeHtml(downloadInfo.sha256)}">
                  SHA-256: ${escapeHtml(downloadInfo.sha256.substring(0, 10))}...
                </span>
              ` : ''}
            </div>
            <div class="asset-actions">
              ${downloadInfo.downloadUrl ? `
                <a href="${escapeHtml(downloadInfo.downloadUrl)}" class="btn btn-primary btn-sm" download>
                  <i class="fas fa-download" aria-hidden="true"></i> Download for Windows
                </a>
              ` : ''}
              ${release.release_page_url ? `
                <a href="${escapeHtml(release.release_page_url)}" class="btn btn-secondary btn-sm" target="_blank" rel="noopener noreferrer">
                  <i class="fab fa-github" aria-hidden="true"></i> GitHub Notes
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
        paginationContainer.innerHTML = `
          <button id="btn-load-more" class="btn btn-secondary">
            Load More Releases (${remaining} remaining)
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
        navigator.clipboard.writeText(url).then(() => {
          const original = btn.innerHTML;
          btn.innerHTML = '<i class="fas fa-check" aria-hidden="true"></i> Copied!';
          setTimeout(() => {
            btn.innerHTML = original;
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
        }, 100);
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
      return '<p class="raw-notes-body">No detailed release notes provided for this build.</p>';
    }

    let out = '';

    if (parsed.added.length > 0) {
      out += `
        <section class="release-category">
          <h3 class="category-header added"><i class="fas fa-plus-circle" aria-hidden="true"></i> Added</h3>
          <ul class="category-list">
            ${parsed.added.map(item => `<li>${escapeHtml(item)}</li>`).join('')}
          </ul>
        </section>
      `;
    }

    if (parsed.improved.length > 0) {
      out += `
        <section class="release-category">
          <h3 class="category-header improved"><i class="fas fa-arrow-circle-up" aria-hidden="true"></i> Improved</h3>
          <ul class="category-list">
            ${parsed.improved.map(item => `<li>${escapeHtml(item)}</li>`).join('')}
          </ul>
        </section>
      `;
    }

    if (parsed.fixed.length > 0) {
      out += `
        <section class="release-category">
          <h3 class="category-header fixed"><i class="fas fa-wrench" aria-hidden="true"></i> Fixed</h3>
          <ul class="category-list">
            ${parsed.fixed.map(item => `<li>${escapeHtml(item)}</li>`).join('')}
          </ul>
        </section>
      `;
    }

    if (parsed.general.length > 0) {
      out += `
        <section class="release-category">
          <h3 class="category-header"><i class="fas fa-list-ul" aria-hidden="true"></i> Changes</h3>
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
        <h3 class="state-title">No Releases Found</h3>
        <p class="state-desc">There are no releases available matching your selected channel filter.</p>
      </div>
    `;
  }

  function renderErrorState() {
    const container = document.getElementById('releases-feed');
    if (!container) return;
    container.innerHTML = `
      <div class="state-box">
        <div class="state-icon" style="color: var(--color-o);"><i class="fas fa-exclamation-triangle" aria-hidden="true"></i></div>
        <h3 class="state-title">Unable to Load Release History</h3>
        <p class="state-desc">We couldn't retrieve the latest release metadata. You can retry or visit GitHub directly.</p>
        <div style="display: flex; gap: 0.75rem; margin-top: 0.5rem;">
          <button id="btn-retry-releases" class="btn btn-primary btn-sm">
            <i class="fas fa-redo" aria-hidden="true"></i> Retry
          </button>
          <a href="https://github.com/Mahfoud-Sa/tik-tak-to/releases" class="btn btn-secondary btn-sm" target="_blank" rel="noopener noreferrer">
            <i class="fab fa-github" aria-hidden="true"></i> View on GitHub
          </a>
        </div>
      </div>
    `;
    const btnRetry = document.getElementById('btn-retry-releases');
    if (btnRetry) {
      btnRetry.addEventListener('click', loadReleaseData);
    }
  }

  // Filter tabs setup
  function initFilterTabs() {
    const tabs = document.querySelectorAll('.filter-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => {
          t.classList.remove('active');
          t.setAttribute('aria-pressed', 'false');
        });
        tab.classList.add('active');
        tab.setAttribute('aria-pressed', 'true');
        currentFilter = tab.dataset.filter || 'all';
        displayedCount = PAGE_SIZE;
        renderReleases();
      });
    });
  }

  // Expose to window
  window.XOVersions = {
    init: function () {
      initFilterTabs();
      loadReleaseData();

      // Listen for hash changes to deep link
      window.addEventListener('hashchange', () => {
        extractTargetFromUrl();
        renderReleases();
      });
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.XOVersions.init);
  } else {
    window.XOVersions.init();
  }
})();
