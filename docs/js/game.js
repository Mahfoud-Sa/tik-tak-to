/**
 * XO Game - Accessible In-Browser Playable Game Engine
 * Implements 3x3 Tic-Tac-Toe with Pass & Play and Single Player vs AI,
 * synthesized Web Audio, full keyboard navigation, themes, and score tracking.
 */

(function () {
  'use strict';

  // Game Constants
  const WINNING_COMBOS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], // Rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8], // Columns
    [0, 4, 8], [2, 4, 6]             // Diagonals
  ];

  // State
  const state = {
    board: Array(9).fill(null),
    currentPlayer: 'X',
    isGameOver: false,
    winningCombo: null,
    mode: 'pvp', // 'pvp' | 'ai'
    theme: 'cyan-gray',
    audioMuted: false,
    scores: {
      x: 0,
      o: 0,
      ties: 0
    }
  };

  // Sound Synth via Web Audio API
  let audioCtx = null;

  function initAudio() {
    if (!audioCtx && (window.AudioContext || window.webkitAudioContext)) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      audioCtx = new AudioContextClass();
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
  }

  function playTone(freq, type = 'sine', duration = 0.12, volume = 0.15) {
    if (state.audioMuted) return;
    try {
      initAudio();
      if (!audioCtx) return;

      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();

      osc.type = type;
      osc.frequency.setValueAtTime(freq, audioCtx.currentTime);

      gain.gain.setValueAtTime(volume, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);

      osc.connect(gain);
      gain.connect(audioCtx.destination);

      osc.start();
      osc.stop(audioCtx.currentTime + duration);
    } catch (e) {
      // Audio autoplay policy fallback
    }
  }

  function playSound(name) {
    if (state.audioMuted) return;
    switch (name) {
      case 'mark-x':
        playTone(520, 'sine', 0.1, 0.18);
        break;
      case 'mark-o':
        playTone(380, 'triangle', 0.12, 0.18);
        break;
      case 'win':
        playTone(587.33, 'triangle', 0.12, 0.2); // D5
        setTimeout(() => playTone(880, 'sine', 0.25, 0.22), 120); // A5
        break;
      case 'tie':
        playTone(280, 'sawtooth', 0.2, 0.12);
        break;
      case 'click':
        playTone(440, 'sine', 0.05, 0.08);
        break;
    }
  }

  // DOM Elements cache
  let dom = {};

  function cacheDom() {
    dom = {
      board: document.getElementById('game-board'),
      cells: Array.from(document.querySelectorAll('.game-cell')),
      statusBanner: document.getElementById('status-banner'),
      statusLive: document.getElementById('status-live-region'),
      scoreX: document.getElementById('score-x'),
      scoreO: document.getElementById('score-o'),
      scoreTies: document.getElementById('score-ties'),
      cardX: document.getElementById('card-player-x'),
      cardO: document.getElementById('card-player-o'),
      btnRestart: document.getElementById('btn-restart-game'),
      btnResetScores: document.getElementById('btn-reset-scores'),
      btnToggleSound: document.getElementById('btn-toggle-sound'),
      modeBtns: Array.from(document.querySelectorAll('.mode-btn')),
      themeSwatches: Array.from(document.querySelectorAll('.theme-swatch'))
    };
  }

  // Win Checker
  function checkWinner(board) {
    for (const combo of WINNING_COMBOS) {
      const [a, b, c] = combo;
      if (board[a] && board[a] === board[b] && board[a] === board[c]) {
        return { winner: board[a], combo };
      }
    }
    if (board.every(cell => cell !== null)) {
      return { winner: 'tie', combo: null };
    }
    return null;
  }

  // Smart AI Move
  function getBestAiMove() {
    const emptyIndices = state.board
      .map((val, idx) => (val === null ? idx : null))
      .filter(val => val !== null);

    if (emptyIndices.length === 0) return null;

    // 1. Can AI (O) win in 1 move?
    for (const idx of emptyIndices) {
      const tempBoard = [...state.board];
      tempBoard[idx] = 'O';
      if (checkWinner(tempBoard)?.winner === 'O') {
        return idx;
      }
    }

    // 2. Can Player (X) win in 1 move? Block it!
    for (const idx of emptyIndices) {
      const tempBoard = [...state.board];
      tempBoard[idx] = 'X';
      if (checkWinner(tempBoard)?.winner === 'X') {
        return idx;
      }
    }

    // 3. Take Center if available
    if (state.board[4] === null) {
      return 4;
    }

    // 4. Take Opposite Corners if available
    const corners = [0, 2, 6, 8].filter(c => state.board[c] === null);
    if (corners.length > 0) {
      return corners[Math.floor(Math.random() * corners.length)];
    }

    // 5. Take any remaining cell
    return emptyIndices[Math.floor(Math.random() * emptyIndices.length)];
  }

  // Make Move
  function makeMove(index) {
    if (state.isGameOver || state.board[index] !== null) return false;

    state.board[index] = state.currentPlayer;
    playSound(state.currentPlayer === 'X' ? 'mark-x' : 'mark-o');

    const result = checkWinner(state.board);

    if (result) {
      handleGameOver(result);
    } else {
      state.currentPlayer = state.currentPlayer === 'X' ? 'O' : 'X';
      updateStatus(`${state.currentPlayer}'s turn`);

      // If AI mode and O's turn, schedule AI move
      if (state.mode === 'ai' && state.currentPlayer === 'O') {
        setCellsDisabled(true);
        setTimeout(() => {
          if (!state.isGameOver) {
            const aiIdx = getBestAiMove();
            setCellsDisabled(false);
            if (aiIdx !== null) {
              makeMove(aiIdx);
            }
          }
        }, 320);
      }
    }

    render();
    return true;
  }

  function handleGameOver(result) {
    state.isGameOver = true;
    state.winningCombo = result.combo;

    if (result.winner === 'tie') {
      state.scores.ties++;
      playSound('tie');
      updateStatus("It's a draw!", 'tie');
    } else {
      if (result.winner === 'X') {
        state.scores.x++;
        playSound('win');
        updateStatus("Player X Wins!", 'win-x');
      } else {
        state.scores.o++;
        playSound('win');
        updateStatus("Player O Wins!", 'win-o');
      }
    }

    saveScores();
  }

  function updateStatus(text, badgeClass = '') {
    if (dom.statusBanner) {
      if (badgeClass) {
        dom.statusBanner.innerHTML = `<span class="status-badge ${badgeClass}">${text}</span>`;
      } else {
        dom.statusBanner.textContent = text;
      }
    }
    if (dom.statusLive) {
      dom.statusLive.textContent = text;
    }
  }

  function setCellsDisabled(disabled) {
    dom.cells.forEach((cell, idx) => {
      if (state.board[idx] === null) {
        cell.disabled = disabled;
      }
    });
  }

  // Render DOM from state
  function render() {
    dom.cells.forEach((cell, idx) => {
      const val = state.board[idx];
      cell.textContent = val || '';
      cell.className = 'game-cell';
      cell.disabled = state.isGameOver || val !== null;

      if (val === 'X') {
        cell.classList.add('cell-x');
      } else if (val === 'O') {
        cell.classList.add('cell-o');
      }

      if (state.winningCombo && state.winningCombo.includes(idx)) {
        cell.classList.add('winning-cell');
        cell.classList.add(val === 'X' ? 'cell-x' : 'cell-o');
      }

      const row = Math.floor(idx / 3) + 1;
      const col = (idx % 3) + 1;
      const stateText = val ? `Marked ${val}` : 'Empty';
      cell.setAttribute('aria-label', `Row ${row}, Column ${col}, ${stateText}`);
    });

    // Active player highlight
    if (dom.cardX) {
      dom.cardX.classList.toggle('active-turn', !state.isGameOver && state.currentPlayer === 'X');
    }
    if (dom.cardO) {
      dom.cardO.classList.toggle('active-turn', !state.isGameOver && state.currentPlayer === 'O');
    }

    // Scores
    if (dom.scoreX) dom.scoreX.textContent = state.scores.x;
    if (dom.scoreO) dom.scoreO.textContent = state.scores.o;
    if (dom.scoreTies) dom.scoreTies.textContent = state.scores.ties;
  }

  function resetGame() {
    state.board = Array(9).fill(null);
    state.currentPlayer = 'X';
    state.isGameOver = false;
    state.winningCombo = null;
    playSound('click');
    updateStatus("Player X's turn");
    render();
  }

  function resetScores() {
    state.scores = { x: 0, o: 0, ties: 0 };
    saveScores();
    resetGame();
  }

  function loadScores() {
    try {
      const stored = localStorage.getItem('xo_game_scores');
      if (stored) {
        const parsed = JSON.parse(stored);
        state.scores.x = Number(parsed.x) || 0;
        state.scores.o = Number(parsed.o) || 0;
        state.scores.ties = Number(parsed.ties) || 0;
      }
    } catch (e) {}
  }

  function saveScores() {
    try {
      localStorage.setItem('xo_game_scores', JSON.stringify(state.scores));
    } catch (e) {}
  }

  // Keyboard navigation for 3x3 board
  function handleBoardKeyDown(e) {
    const activeEl = document.activeElement;
    const currentIndex = dom.cells.indexOf(activeEl);

    if (currentIndex === -1) return;

    let targetIndex = null;
    const row = Math.floor(currentIndex / 3);
    const col = currentIndex % 3;

    switch (e.key) {
      case 'ArrowUp':
        targetIndex = row > 0 ? currentIndex - 3 : currentIndex + 6;
        e.preventDefault();
        break;
      case 'ArrowDown':
        targetIndex = row < 2 ? currentIndex + 3 : currentIndex - 6;
        e.preventDefault();
        break;
      case 'ArrowLeft':
        targetIndex = col > 0 ? currentIndex - 1 : currentIndex + 2;
        e.preventDefault();
        break;
      case 'ArrowRight':
        targetIndex = col < 2 ? currentIndex + 1 : currentIndex - 2;
        e.preventDefault();
        break;
      case 'Home':
        targetIndex = 0;
        e.preventDefault();
        break;
      case 'End':
        targetIndex = 8;
        e.preventDefault();
        break;
      case '1': case '2': case '3': case '4': case '5':
      case '6': case '7': case '8': case '9':
        targetIndex = parseInt(e.key, 10) - 1;
        makeMove(targetIndex);
        e.preventDefault();
        return;
    }

    if (targetIndex !== null && dom.cells[targetIndex]) {
      dom.cells[targetIndex].focus();
    }
  }

  // Theme Handling
  function setTheme(themeName) {
    state.theme = themeName;
    document.documentElement.setAttribute('data-game-theme', themeName);
    dom.themeSwatches.forEach(swatch => {
      swatch.classList.toggle('active', swatch.dataset.theme === themeName);
      swatch.setAttribute('aria-pressed', swatch.dataset.theme === themeName ? 'true' : 'false');
    });
    try {
      localStorage.setItem('xo_game_theme', themeName);
    } catch (e) {}
  }

  function loadTheme() {
    try {
      const saved = localStorage.getItem('xo_game_theme');
      if (saved) {
        setTheme(saved);
        return;
      }
    } catch (e) {}
    setTheme('cyan-gray');
  }

  // Initialize event bindings
  function initEvents() {
    dom.cells.forEach((cell, idx) => {
      cell.addEventListener('click', () => {
        makeMove(idx);
      });
    });

    if (dom.board) {
      dom.board.addEventListener('keydown', handleBoardKeyDown);
    }

    if (dom.btnRestart) {
      dom.btnRestart.addEventListener('click', resetGame);
    }

    if (dom.btnResetScores) {
      dom.btnResetScores.addEventListener('click', resetScores);
    }

    if (dom.btnToggleSound) {
      dom.btnToggleSound.addEventListener('click', () => {
        state.audioMuted = !state.audioMuted;
        dom.btnToggleSound.setAttribute('aria-pressed', state.audioMuted ? 'false' : 'true');
        dom.btnToggleSound.innerHTML = state.audioMuted
          ? '<i class="fas fa-volume-mute" aria-hidden="true"></i>'
          : '<i class="fas fa-volume-up" aria-hidden="true"></i>';
        dom.btnToggleSound.setAttribute('title', state.audioMuted ? 'Unmute Sound' : 'Mute Sound');
      });
    }

    dom.modeBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        dom.modeBtns.forEach(b => {
          b.classList.remove('active');
          b.setAttribute('aria-pressed', 'false');
        });
        btn.classList.add('active');
        btn.setAttribute('aria-pressed', 'true');
        state.mode = btn.dataset.mode;
        resetGame();
      });
    });

    dom.themeSwatches.forEach(swatch => {
      swatch.addEventListener('click', () => {
        setTheme(swatch.dataset.theme);
      });
    });
  }

  // Public interface
  window.XOGame = {
    init: function () {
      cacheDom();
      if (!dom.board) return;
      loadScores();
      loadTheme();
      initEvents();
      resetGame();
    },
    focusBoard: function () {
      if (dom.cells && dom.cells[0]) {
        dom.cells[0].focus();
      }
    }
  };

  // Auto initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.XOGame.init);
  } else {
    window.XOGame.init();
  }
})();
