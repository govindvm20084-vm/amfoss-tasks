var panel = document.getElementById('panel');
var startBtn = document.getElementById('startBtn');
var againBtn = document.getElementById('againBtn');
var resultsBox = document.getElementById('results');
var roundLabel = document.getElementById('roundLabel');
var gates = document.querySelectorAll('.gate');

var ROUNDS = 5;
var roundNum = 0;
var clickTimes = [];
var waitTimer = null;
var goTime = 0;
var gameState = 'idle';
var BEST_KEY = 'reaction-gate-best-avg';

function setPanel(cls, label, big, sub) {
  panel.className = 'panel ' + cls;
  panel.innerHTML = '<div class="label">' + label + '</div>' +
    '<div class="big">' + big + '</div>' +
    '<div class="sub">' + sub + '</div>';
}

function updateRoundLabel() {
  var n = roundNum > ROUNDS ? ROUNDS : roundNum;
  roundLabel.textContent = 'ROUND ' + n + ' / ' + ROUNDS;
}

function resetStrip() {
  for (var i = 0; i < gates.length; i++) {
    gates[i].className = 'gate';
    gates[i].textContent = '-';
  }
}

function fillGate(i, ms, wasFoul) {
  var g = gates[i];
  if (wasFoul) {
    g.className = 'gate foul';
    g.textContent = 'FOUL';
  } else {
    g.className = 'gate filled';
    g.textContent = ms + 'ms';
  }
}

function highlightGate(i) {
  gates.forEach(function(g) { g.classList.remove('active'); });
  if (gates[i]) gates[i].classList.add('active');
}

function getBest() {
  var v = localStorage.getItem(BEST_KEY);
  if (!v) return null;
  return Number(v);
}

function saveBest(val) {
  localStorage.setItem(BEST_KEY, val);
}

function startRound() {
  gameState = 'waiting';
  highlightGate(roundNum);
  setPanel('wait', 'Armed', 'Wait for it...', 'Do not click until the gate turns green.');

  var delay = 1200 + Math.random() * 2800;
  waitTimer = setTimeout(function() {
    gameState = 'go';
    goTime = performance.now();
    setPanel('go', 'Go', 'CLICK', '');
  }, delay);
}

function registerFoul() {
  clearTimeout(waitTimer);
  gameState = 'foul';
  fillGate(roundNum, 0, true);
  setPanel('foul', 'Too soon', 'False start', 'Click anywhere to retry this round.');
}

function registerHit() {
  var ms = Math.round(performance.now() - goTime);
  clickTimes.push(ms);
  fillGate(roundNum, ms, false);
  roundNum = roundNum + 1;
  updateRoundLabel();

  if (roundNum >= ROUNDS) {
    finishGame();
  } else {
    gameState = 'between';
    setPanel('idle', 'Recorded', ms + 'ms', 'Click to arm the next round.');
  }
}

panel.addEventListener('click', function() {
  if (gameState == 'waiting') registerFoul();
  else if (gameState == 'go') registerHit();
  else if (gameState == 'foul') startRound();
  else if (gameState == 'between') startRound();
});

function getRating(avg) {
  if (avg < 200) return ['LIGHTNING', 'Elite-tier reflexes. Top few percent.'];
  if (avg < 250) return ['FAST', 'Quicker than the average adult.'];
  if (avg < 300) return ['AVERAGE', 'Right around typical human reaction time.'];
  if (avg < 350) return ['STEADY', 'A bit unhurried, plenty of room to sharpen.'];
  return ['SLOW GATE', 'Reaction time is well behind average, try again.'];
}

function finishGame() {
  gameState = 'idle';

  var total = 0;
  for (var i = 0; i < clickTimes.length; i++) total += clickTimes[i];
  var avg = Math.round(total / clickTimes.length);
  var fastest = Math.min.apply(null, clickTimes);
  var slowest = Math.max.apply(null, clickTimes);
  var rating = getRating(avg);

  document.getElementById('avgVal').textContent = avg + 'ms';
  document.getElementById('fastVal').textContent = fastest + 'ms';
  document.getElementById('slowVal').textContent = slowest + 'ms';
  document.getElementById('ratingTag').textContent = rating[0];
  document.getElementById('ratingNote').textContent = rating[1];

  var prevBest = getBest();
  var best = prevBest;
  var newBestNote = document.getElementById('newBestNote');

  if (prevBest === null || avg < prevBest) {
    best = avg;
    saveBest(avg);
    newBestNote.style.display = 'block';
  } else {
    newBestNote.style.display = 'none';
  }

  document.getElementById('bestVal').textContent = best + 'ms';

  panel.style.display = 'none';
  startBtn.style.display = 'none';
  resultsBox.classList.add('show');
}

function resetGame() {
  roundNum = 0;
  clickTimes = [];
  resetStrip();
  updateRoundLabel();
  resultsBox.classList.remove('show');
  panel.style.display = 'flex';
}

startBtn.addEventListener('click', function(e) {
  e.stopPropagation();
  resetGame();
  startRound();
});

againBtn.addEventListener('click', function() {
  resetGame();
  panel.className = 'panel idle';
  panel.innerHTML = '<div class="label">Timing gate idle</div>' +
    '<div class="big">Test your reflexes</div>' +
    '<div class="sub">5 rounds. Click the instant the gate opens.</div>' +
    '<button class="startbtn" id="startBtn2">Start Game</button>';

  document.getElementById('startBtn2').addEventListener('click', function(e) {
    e.stopPropagation();
    resetGame();
    startRound();
  });
});

updateRoundLabel();
