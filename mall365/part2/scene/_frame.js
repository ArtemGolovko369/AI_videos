// ---------- кадр ----------
const scA = document.getElementById('scA'), scB = document.getElementById('scB');
window.renderAt = function (t) {
  gid = 0;
  const act = scenes.filter(s => t >= s.t0 - s.fade && t < s.t1 + .0001);
  // текущая — последняя начавшаяся; предыдущая гаснет
  let html = '';
  act.sort((a, b) => a.t0 - b.t0);
  act.forEach((s, i) => {
    const o = i === 0 ? 1 : clamp((t - (s.t0 - s.fade)) / s.fade);
    html += `<g opacity="${o.toFixed(3)}">${s.draw(t)}</g>`;
  });
  scA.innerHTML = html; scB.innerHTML = '';
  document.getElementById('turb').setAttribute('seed', String(Math.floor(t * 30) % 17 + 1));
  renderHUD(t); renderSubs(t); renderOverlays(t);
};
window.SFX = SFX.sort((a, b) => a.t - b.t);
window.DUR = DUR;
})();
