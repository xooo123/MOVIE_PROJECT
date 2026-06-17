if (document.getElementById("votes")) {
  ["votes", "actor", "writer", "director"].forEach(id => {
    document.getElementById(id).addEventListener("input", validateInputs);
  });
}

function clearErrors() {
  ["votesError", "actorError", "writerError", "directorError"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerText = "";
  });
}

function validateInputs() {
  clearErrors();
  let valid = true;

  const votes = parseFloat(document.getElementById("votes").value);
  const actor = parseFloat(document.getElementById("actor").value);
  const writer = parseFloat(document.getElementById("writer").value);
  const director = parseFloat(document.getElementById("director").value);

  if (votes < 0 || votes > 10000) {
    document.getElementById("votesError").innerText = "Invalid votes";
    valid = false;
  }
  if (actor < 0 || actor > 10) {
    document.getElementById("actorError").innerText = "Actor score is invalid";
    valid = false;
  }
  if (writer < 0 || writer > 10) {
    document.getElementById("writerError").innerText = "Writer score is invalid";
    valid = false;
  }
  if (director < 0 || director > 10) {
    document.getElementById("directorError").innerText = "Director score is invalid";
    valid = false;
  }
  return valid;
}

async function predictMovie() {
  const resultEl = document.getElementById("result");

  const data = {
    numVotes: parseFloat(document.getElementById("votes").value),
    genre: document.getElementById("genre").value,
    avg_actor_score: parseFloat(document.getElementById("actor").value),
    writer_avg_score: parseFloat(document.getElementById("writer").value),
    director_avg_score: parseFloat(document.getElementById("director").value)
  };

  resultEl.innerText = "🎬 Analyzing...";

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    const result = await response.json();
    resultEl.innerText = result.label;

  } catch (err) {
    resultEl.innerText = "Error connecting to backend";
  }
}
const spot = document.getElementById('spot');
if (spot) {
  let mx = window.innerWidth / 2, my = window.innerHeight * 0.35, cx = mx, cy = my;
  addEventListener('pointermove', e => { mx = e.clientX; my = e.clientY; });
  (function loop() {
    cx += (mx - cx) * 0.12;
    cy += (my - cy) * 0.12;
    spot.style.left = cx + 'px';
    spot.style.top = cy + 'px';
    requestAnimationFrame(loop);
  })();
}

/* 3D parallax tilt on posters (cursor-reactive) */
const stage = document.getElementById('stage');
if (stage) {
  const posters = [...stage.querySelectorAll('.poster')];
  stage.addEventListener('pointermove', e => {
    const r = stage.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width - 0.5;
    const py = (e.clientY - r.top) / r.height - 0.5;
    posters.forEach(p => {
      const d = +p.dataset.depth;
      p.style.transform =
        `rotateY(${px * 14}deg) rotateX(${-py * 14}deg) translate(${px * d}px,${py * d}px) translateZ(${d}px)`;
    });
  });
  stage.addEventListener('pointerleave', () => posters.forEach(p => p.style.transform = ''));

  /* Per-poster sheen follows cursor */
  posters.forEach(p => p.addEventListener('pointermove', e => {
    const r = p.getBoundingClientRect();
    p.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100) + '%');
    p.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100) + '%');
  }));
}

/* AI score meter — count up + ring fill when scrolled into view */
const score = document.getElementById('score');
if (score) {
  const bar = document.getElementById('bar');
  const numEl = document.getElementById('num');
  const target = +score.dataset.target;
  const C = 534; /* circumference: 2 * PI * r(85) */
  const runScore = () => {
    bar.style.strokeDashoffset = C - (C * target / 100);
    let n = 0;
    const step = () => {
      n += Math.ceil((target - n) / 8) || 1;
      if (n >= target) n = target;
      numEl.textContent = n;
      if (n < target) requestAnimationFrame(step);
      else score.classList.add('done');
    };
    requestAnimationFrame(step);
  };
  new IntersectionObserver((entries, o) => {
    entries.forEach(en => { if (en.isIntersecting) { runScore(); o.disconnect(); } });
  }, { threshold: 0.4 }).observe(score);
}

/* Scroll-reveal feature cards */
document.querySelectorAll('.card').forEach(c => {
  new IntersectionObserver((entries, o) => {
    entries.forEach(en => { if (en.isIntersecting) { en.target.classList.add('in'); o.disconnect(); } });
  }, { threshold: 0.25 }).observe(c);
});