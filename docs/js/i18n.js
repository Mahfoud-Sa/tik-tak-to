/**
 * XO Game - Internationalization (i18n) Engine
 * Full bilingual support: English (en) and Arabic (ar)
 * Handles text updates, RTL/LTR layout direction, date localization, and game event hooks.
 */

(function () {
  'use strict';

  const TRANSLATIONS = {
    en: {
      // Document & Navigation
      pageTitle: "XO Game - Fast, Modern Tic-Tac-Toe for Web & Windows",
      pageDescription: "Play Tic-Tac-Toe online in your browser or download the standalone Windows desktop edition with LAN multiplayer, custom themes, and automatic updates.",
      skipLink: "Skip to Game",
      brandName: "XO Game",
      navPlay: "Play Now",
      navFeatures: "Features",
      navHowToPlay: "How to Play",
      navOpenSource: "Open Source",
      navDesktop: "Desktop Edition",
      navVersions: "Version History",
      themeToggleLight: "Switch to Light Mode",
      themeToggleDark: "Switch to Dark Mode",
      langToggleText: "العربية",
      langToggleAria: "Switch language to Arabic",

      // Hero Section
      heroPillPrefix: "Latest Stable: ",
      heroTitlePart1: "The Classic ",
      heroTitlePart2: " and ",
      heroTitlePart3: " Game, Reimagined.",
      heroSubtitle: "Play instantly in your browser against friends or computer, or download the portable Windows desktop edition with LAN multiplayer and customizable themes.",
      heroPlayNow: "Play Now",
      heroViewGitHub: "View on GitHub",
      heroVersionHistory: "Version History",
      heroWindowsDownload: "Windows Download",
      heroBadgeWebDesktop: "Web & Windows",
      heroBadgeOpenSource: "Open Source MIT",
      heroBadgeOffline: "Zero Install Needed",
      heroPreviewBadge: "Interactive Preview",
      heroPreviewCaption: "Tap any tile or click Play Now to start an instant match!",

      // Play Arena (The Real Game)
      gameTag: "Play In Browser",
      gameTitle: "Play XO Game Now",
      gameDesc: "Quick, responsive, and fully playable online. Switch between local 2-player Pass & Play or challenge the AI.",
      modePvp: "Pass & Play",
      modeAi: "vs Computer",
      soundToggleTitleMute: "Mute Sound",
      soundToggleTitleUnmute: "Unmute Sound",
      resetScoreboardTitle: "Reset Scoreboard",
      playerXLabel: "Player X",
      playerOLabel: "Player O",
      drawsLabel: "Draws",
      turnX: "Player X's turn",
      turnO: "Player O's turn",
      winX: "Player X Wins!",
      winO: "Player O Wins!",
      winTie: "It's a draw!",
      newRoundBtn: "New Round",
      colorPaletteLabel: "Color Palette:",
      themeCyanGray: "Cyan & Gray",
      themeOrangeGreen: "Orange & Green",
      themePurpleGray: "Purple & Cyan",
      themeClassic: "Classic Red & Blue",

      // Features Section
      featuresTag: "Game Capabilities",
      featuresTitle: "Built for Seamless Play",
      featuresDesc: "Every feature implemented in the XO Game project across the web and native Windows editions.",
      feat1Title: "Instant 3x3 Grid Engine",
      feat1Desc: "Responsive canvas with immediate win detection across rows, columns, and diagonals, instant draw resolution, synthesized sound effects, and score tracking.",
      feat2Title: "10 Aesthetic Color Themes",
      feat2Desc: "Customizable visual themes inspired by the desktop Tkinter palette, allowing players to personalize grid and token hues.",
      feat3Title: "Pass & Play + Computer Opponent",
      feat3Desc: "Play with a friend locally on the same screen or test your tactical skills against the browser computer engine with instant response.",
      feat4Title: "Standalone Windows Portable Build",
      feat4Desc: "Packaged with PyInstaller into a clean portable archive. Run directly on any modern Windows PC without installing Python.",
      feat5Title: "Socket-Based LAN Multiplayer",
      feat5Desc: "Host and join matches over your local WiFi or Ethernet network via robust direct TCP client-server sockets on the desktop edition.",
      feat6Title: "Automated Background Updater",
      feat6Desc: "Integrated updater checks GitHub releases in the background, parses SemVer versions, shows release notes, and offers direct downloads.",

      // How to Play Section
      howTag: "Rules & Controls",
      howTitle: "How to Play",
      howDesc: "Simple rules for players of all ages. Keyboard, mouse, and touch-friendly.",
      step1Num: "1",
      step1Title: "Take Turns Marking",
      step1Desc: "Player X always moves first. Click, tap, or use keys 1–9 (or arrow keys with Enter/Space) to claim an empty grid square.",
      step2Num: "2",
      step2Title: "Form 3 in a Row",
      step2Desc: "Align three of your marks horizontally, vertically, or diagonally across the board before your opponent does to win the round.",
      step3Num: "3",
      step3Title: "Block & Strategize",
      step3Desc: "Defend your lines by anticipating your opponent’s next move. If all 9 cells are filled without a 3-in-a-row, it’s a draw!",

      // Open Source / Clone Section
      osTag: "Open Source",
      osTitle: "Explore, Clone & Contribute",
      osDesc: "XO Game is 100% free and open source. Developers can inspect the Python Tkinter desktop source code, the web engine, or build custom packages.",
      osRepoUrlLabel: "Repository URL",
      osCloneCommandLabel: "Clone Command",
      osCopyBtn: "Copy",
      osCopiedFeedback: "Copied!",
      osCopyError: "Failed to copy",
      osViewRepoBtn: "View Repository",
      osReportIssueBtn: "Report an Issue",
      osSetupTitle: "Installation & Startup Guide",
      osSetupDesc: "Run the desktop game from source code in four simple steps:",
      osStepClone: "Clone the repository",
      osStepCd: "Navigate into the project folder",
      osStepInstall: "Install optional build dependencies",
      osStepRun: "Launch the game",
      osLicenseNotice: "Licensed under the",
      osLicenseLink: "MIT License",

      // Latest Release Section
      relTag: "Official Release",
      relStableBadge: "Latest Stable",
      relDownloadBtn: "Download for Windows (ZIP)",
      relNotesBtn: "View Release Notes",
      relAllVersionsBtn: "All Versions",
      relDefaultSummary: "The official Windows desktop release includes standalone executable packaging, in-game auto-update notifications, socket multiplayer, and full theme customization without needing Python installed.",

      // Footer
      footerDesc: "An open-source Tic-Tac-Toe project featuring in-browser play, Windows desktop distribution, socket multiplayer, and an automated release pipeline.",
      footerNavHeading: "Navigation",
      footerCodeHeading: "Project & Code",
      footerPlayOnline: "Play Online",
      footerGitHubRepo: "GitHub Repository",
      footerGitHubReleases: "GitHub Releases",
      footerReleasesManifest: "Releases Manifest (JSON)",
      footerVersionManifest: "Latest Manifest (JSON)",
      footerLicense: "MIT License (docs/LICENSE.txt)",
      footerCopyright: "© 2026 XO Game. Developed by Mahfoud Mohamed Binsabbah.",
      footerOpenSourceNote: "Open Source under MIT License."
    },

    ar: {
      // Document & Navigation
      pageTitle: "لعبة إكس أو - تجربة عصرية وسريعة للويب وويندوز",
      pageDescription: "العب لعبة إكس أو أونلاين في متصفحك أو حمّل النسخة المكتبية المستقلة لويندوز مع اللعب الجماعي عبر الشبكة المحلية والسمات المخصصة والتحديثات التلقائية.",
      skipLink: "الانتقال إلى اللعبة",
      brandName: "لعبة إكس أو",
      navPlay: "العب الآن",
      navFeatures: "المميزات",
      navHowToPlay: "طريقة اللعب",
      navOpenSource: "المصدر المفتوح",
      navDesktop: "نسخة ويندوز",
      navVersions: "سجل الإصدارات",
      themeToggleLight: "التبديل إلى الوضع الفاتح",
      themeToggleDark: "التبديل إلى الوضع الداكن",
      langToggleText: "English",
      langToggleAria: "Switch language to English",

      // Hero Section
      heroPillPrefix: "أحدث إصدار مستقر: ",
      heroTitlePart1: "لعبة ",
      heroTitlePart2: " و ",
      heroTitlePart3: " الكلاسيكية، برؤية عصرية.",
      heroSubtitle: "العب فوراً في متصفحك ضد صديق أو ضد الكمبيوتر، أو حمّل نسخة ويندوز المكتبية المستقلة مع ميزة اللعب الجماعي عبر الشبكة المحلية والسمات المخصصة.",
      heroPlayNow: "العب الآن",
      heroViewGitHub: "عرض على GitHub",
      heroVersionHistory: "سجل الإصدارات",
      heroWindowsDownload: "تحميل لويندوز",
      heroBadgeWebDesktop: "للويب وويندوز",
      heroBadgeOpenSource: "مفتوح المصدر MIT",
      heroBadgeOffline: "بدون أي تثبيت",
      heroPreviewBadge: "معاينة تفاعلية",
      heroPreviewCaption: "المس أي مربع أو انقر على 'العب الآن' لبدء جولة حماسية فوراً!",

      // Play Arena (The Real Game)
      gameTag: "العب في المتصفح",
      gameTitle: "العب لعبة إكس أو الآن",
      gameDesc: "سريعة وتفاعلية وقابلة للعب بالكامل في المتصفح. بدّل بين اللعب الثنائي المحلي أو تحدي الحاسوب.",
      modePvp: "لعب ثنائي محلي",
      modeAi: "ضد الكمبيوتر",
      soundToggleTitleMute: "كتم الصوت",
      soundToggleTitleUnmute: "تشغيل الصوت",
      resetScoreboardTitle: "إعادة ضبط النتائج",
      playerXLabel: "اللاعب X",
      playerOLabel: "اللاعب O",
      drawsLabel: "التعادل",
      turnX: "دور اللاعب X",
      turnO: "دور اللاعب O",
      winX: "فاز اللاعب X!",
      winO: "فاز اللاعب O!",
      winTie: "تعادل!",
      newRoundBtn: "جولة جديدة",
      colorPaletteLabel: "لوحة الألوان:",
      themeCyanGray: "سماوي ورمادي",
      themeOrangeGreen: "برتقالي وأخضر",
      themePurpleGray: "بنفسجي وسماوي",
      themeClassic: "أحمر وأزرق كلاسيكي",

      // Features Section
      featuresTag: "قدرات ومميزات اللعبة",
      featuresTitle: "صُممت لتجربة لعب سلسة",
      featuresDesc: "جميع المميزات المنفذة فعلياً في مشروع لعبة إكس أو عبر المتصفح ونسخة ويندوز المستقلة.",
      feat1Title: "محرك شبكة 3×3 فوري",
      feat1Desc: "لوحة تفاعلية مع كشف فوري للفوز عبر الصفوف والأعمدة والأقطار، وحساب التعادل بدقة مع مؤثرات صوتية وتتبع مستمر للنتائج.",
      feat2Title: "10 سمات لونية جذابة",
      feat2Desc: "خصّص مظهر اللوحة والرموز مع 10 أنماط لونية مدمجة مستوحاة من مكتبة Tkinter وواجهات المستخدم الحديثة.",
      feat3Title: "لعب ثنائي محلي + خصم ذكي",
      feat3Desc: "العب مع صديق على نفس الجهاز أو اختبر مهاراتك التكتيكية ضد محرك الذكاء الاصطناعي في المتصفح باستجابة فورية.",
      feat4Title: "نسخة محمولة مستقلة لويندوز",
      feat4Desc: "مُحزّمة عبر PyInstaller في ملف محمول خفيف. تعمل مباشرة على أي جهاز ويندوز دون الحاجة لتثبيت بايثون.",
      feat5Title: "لعب جماعي عبر الشبكة المحلية (LAN)",
      feat5Desc: "أنشئ غرفة أو انضم لمباراة عبر شبكة الواي فاي أو الشبكة المحلية عبر بروتوكول مقابس TCP المتين في نسخة سطح المكتب.",
      feat6Title: "نظام تحديثات تلقائي مدمج",
      feat6Desc: "نظام تحديث مدمج يتحقق من إصدارات GitHub في الخلفية وفق المعيار الدلالي SemVer ويعرض الملاحظات والتحميل المباشر.",

      // How to Play Section
      howTag: "القواعد وطريقة التحكم",
      howTitle: "كيف تلعب",
      howDesc: "قواعد بسيطة لجميع الأعمار، متوافقة مع لوحة المفاتيح واللمس والفأرة.",
      step1Num: "1",
      step1Title: "تبادل الأدوار ووضع العلامات",
      step1Desc: "يبدأ اللاعب X دائماً أولاً. انقر أو المس أو استخدم الأرقام 1-9 (أو الأسهم مع Enter/Space) لاختيار مربع فارغ.",
      step2Num: "2",
      step2Title: "صِفّ 3 رموز في خط مستقيم",
      step2Desc: "ضع ثلاثة من رموزك بشكل أفقي أو رأسي أو قطري عبر اللوحة قبل أن يسبقك منافسك لتحقيق الفوز.",
      step3Num: "3",
      step3Title: "امنع الخصم وفكّر بتكتيك",
      step3Desc: "توقّع خطوة خصمك القادمة واقطع عليه طريق الفوز. وإذا امتلأت المربعات التسعة دون فائز، تنتهي الجولة بالتعادل.",

      // Open Source / Clone Section
      osTag: "المصدر المفتوح",
      osTitle: "استكشف الكود، واستنسخه، وساهم",
      osDesc: "مشروع لعبة إكس أو مجاني ومفتوح المصدر بالكامل. يمكن للمطورين استكشاف كود بايثون Tkinter لسطح المكتب، أو محرك الويب، أو بناء حزم مخصصة.",
      osRepoUrlLabel: "رابط المستودع",
      osCloneCommandLabel: "أمر الاستنساخ",
      osCopyBtn: "نسخ",
      osCopiedFeedback: "تم النسخ!",
      osCopyError: "فشل النسخ",
      osViewRepoBtn: "عرض المستودع",
      osReportIssueBtn: "الإبلاغ عن مشكلة",
      osSetupTitle: "دليل التثبيت والتشغيل المحلي",
      osSetupDesc: "شغّل اللعبة المكتبية من المصدر في أربع خطوات بسيطة:",
      osStepClone: "استنساخ المستودع",
      osStepCd: "الانتقال لمجلد المشروع",
      osStepInstall: "تثبيت متطلبات البناء الاختيارية",
      osStepRun: "تشغيل اللعبة",
      osLicenseNotice: "مرخصة بموجب",
      osLicenseLink: "رخصة MIT",

      // Latest Release Section
      relTag: "الإصدار الرسمي",
      relStableBadge: "أحدث إصدار مستقر",
      relDownloadBtn: "تحميل لويندوز (ZIP)",
      relNotesBtn: "عرض ملاحظات الإصدار",
      relAllVersionsBtn: "جميع الإصدارات",
      relDefaultSummary: "يتضمن إصدار ويندوز المكتبي حزمة تنفيذية محمولة ومستقلة، مع إشعارات التحديث التلقائي، واللعب الجماعي عبر المقابس، وتخصيص السمات دون الحاجة لتثبيت بايثون.",

      // Footer
      footerDesc: "مشروع لعبة إكس أو مفتوح المصدر يتميز باللعب عبر المتصفح وتوزيع نسخة سطح المكتب لويندوز واللعب الجماعي عبر الشبكة المحلية ونظام تحديثات تلقائي.",
      footerNavHeading: "التنقل",
      footerCodeHeading: "المشروع والكود",
      footerPlayOnline: "العب أونلاين",
      footerGitHubRepo: "مستودع GitHub",
      footerGitHubReleases: "إصدارات GitHub",
      footerReleasesManifest: "ملف بيانات الإصدارات (JSON)",
      footerVersionManifest: "ملف أحدث إصدار (JSON)",
      footerLicense: "رخصة MIT (ملف docs/LICENSE.txt)",
      footerCopyright: "© 2026 لعبة إكس أو. تطوير محفوظ محمد بن سباح.",
      footerOpenSourceNote: "مفتوح المصدر بموجب رخصة MIT."
    }
  };

  let currentLang = 'en';
  const listeners = [];

  function getSavedLanguage() {
    try {
      const saved = localStorage.getItem('xo_lang');
      if (saved === 'ar' || saved === 'en') return saved;
      if (navigator.language && navigator.language.startsWith('ar')) return 'ar';
    } catch (e) {}
    return 'en';
  }

  function setLanguage(lang) {
    if (lang !== 'en' && lang !== 'ar') lang = 'en';
    currentLang = lang;
    try {
      localStorage.setItem('xo_lang', lang);
    } catch (e) {}

    const isRtl = lang === 'ar';
    document.documentElement.setAttribute('lang', lang);
    document.documentElement.setAttribute('dir', isRtl ? 'rtl' : 'ltr');

    // Update document title and meta description
    if (TRANSLATIONS[lang].pageTitle) {
      document.title = TRANSLATIONS[lang].pageTitle;
    }
    const metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc && TRANSLATIONS[lang].pageDescription) {
      metaDesc.setAttribute('content', TRANSLATIONS[lang].pageDescription);
    }

    // Update all elements with data-i18n
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (TRANSLATIONS[lang] && TRANSLATIONS[lang][key] !== undefined) {
        el.textContent = TRANSLATIONS[lang][key];
      }
    });

    // Update elements with data-i18n-attr (e.g. data-i18n-attr="title:themeToggleLight,aria-label:themeToggleLight")
    const attrElements = document.querySelectorAll('[data-i18n-attr]');
    attrElements.forEach(el => {
      const raw = el.getAttribute('data-i18n-attr');
      const pairs = raw.split(',');
      pairs.forEach(pair => {
        const [attr, key] = pair.split(':').map(s => s.trim());
        if (attr && key && TRANSLATIONS[lang] && TRANSLATIONS[lang][key] !== undefined) {
          el.setAttribute(attr, TRANSLATIONS[lang][key]);
        }
      });
    });

    // Update Language Toggle button
    const langBtn = document.getElementById('lang-toggle-btn');
    if (langBtn) {
      const langText = TRANSLATIONS[lang].langToggleText;
      const langAria = TRANSLATIONS[lang].langToggleAria;
      langBtn.innerHTML = `<i class="fas fa-globe" aria-hidden="true"></i> <span>${langText}</span>`;
      langBtn.setAttribute('aria-label', langAria);
      langBtn.setAttribute('title', langAria);
    }

    // Update Theme Toggle button aria/title
    const themeBtn = document.getElementById('theme-toggle-btn');
    if (themeBtn) {
      const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
      const themeTitle = TRANSLATIONS[lang][isDark ? 'themeToggleLight' : 'themeToggleDark'];
      themeBtn.setAttribute('title', themeTitle);
      themeBtn.setAttribute('aria-label', themeTitle);
    }

    // Notify listeners
    listeners.forEach(fn => {
      try {
        fn(lang);
      } catch (err) {
        console.error('Error in i18n change listener:', err);
      }
    });
  }

  function t(key) {
    if (TRANSLATIONS[currentLang] && TRANSLATIONS[currentLang][key] !== undefined) {
      return TRANSLATIONS[currentLang][key];
    }
    if (TRANSLATIONS.en && TRANSLATIONS.en[key] !== undefined) {
      return TRANSLATIONS.en[key];
    }
    return key;
  }

  function formatDate(isoStr, lang = currentLang) {
    if (!isoStr) return '';
    try {
      const d = new Date(isoStr);
      if (isNaN(d.getTime())) return isoStr;
      const locale = lang === 'ar' ? 'ar-EG' : 'en-US';
      return new Intl.DateTimeFormat(locale, {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      }).format(d);
    } catch (e) {
      return isoStr;
    }
  }

  function onLanguageChange(fn) {
    if (typeof fn === 'function') {
      listeners.push(fn);
    }
  }

  // Initialize
  function init() {
    const initialLang = getSavedLanguage();
    setLanguage(initialLang);

    const langBtn = document.getElementById('lang-toggle-btn');
    if (langBtn) {
      langBtn.addEventListener('click', () => {
        const next = currentLang === 'en' ? 'ar' : 'en';
        setLanguage(next);
      });
    }
  }

  window.XOI18n = {
    init,
    t,
    setLanguage,
    getCurrentLanguage: () => currentLang,
    formatDate,
    onLanguageChange,
    translations: TRANSLATIONS
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
