(() => {
  const picker = document.querySelector("[data-tile-picker]");
  if (!picker) return;

  const inputs = {
    hand: document.getElementById("id_hand_text"),
    win: document.getElementById("id_win_tile_text"),
    dora: document.getElementById("id_dora_text"),
    ura: document.getElementById("id_ura_dora_text"),
  };

  const suitMax = { m: 9, p: 9, s: 9, z: 7 };
  const suitOrder = ["m", "p", "s", "z"];
  const tileList = [];
  suitOrder.forEach((suit) => {
    for (let i = 1; i <= suitMax[suit]; i += 1) {
      tileList.push(`${i}${suit}`);
    }
    if (suit !== "z") tileList.push(`0${suit}`);
  });
  const tileSet = new Set(tileList);

  const honorLabels = {
    "1z": "E",
    "2z": "S",
    "3z": "W",
    "4z": "N",
    "5z": "Wh",
    "6z": "G",
    "7z": "R",
  };
  const suitLabels = { m: "M", p: "P", s: "S", z: "Z" };
  const suitColors = { m: "#c62828", p: "#1565c0", s: "#2e7d32", z: "#333333" };
  const honorColors = { "5z": "#555555", "6z": "#2e7d32", "7z": "#c62828" };

  const targets = {};
  picker.querySelectorAll("[data-target]").forEach((el) => {
    const name = el.dataset.target;
    const max = Number(el.dataset.max || 0);
    if (!name || !max) return;
    targets[name] = {
      name,
      max,
      el,
      tiles: [],
    };
  });
  const targetNames = Object.keys(targets);
  if (!targetNames.length) return;
  let active = targets.hand || targets[targetNames[0]];

  const tileCache = new Map();
  const tileImgCache = new Map();

  const parseCompact = (value) => {
    const s = (value || "").trim().toLowerCase().replace(/\s+/g, "");
    if (!s) return [];
    const out = [];
    let buf = "";
    for (const ch of s) {
      if (/\d/.test(ch)) {
        buf += ch;
        continue;
      }
      if (!"mpsz".includes(ch)) {
        buf = "";
        continue;
      }
      for (const d of buf) {
        const tile = `${d}${ch}`;
        if (tileSet.has(tile)) out.push(tile);
      }
      buf = "";
    }
    return out;
  };

  const parseCsv = (value) => {
    return (value || "")
      .split(",")
      .map((part) => part.trim().toLowerCase())
      .filter((tile) => tileSet.has(tile));
  };

  const tileSrc = (tile) => {
    if (tileCache.has(tile)) return tileCache.get(tile);
    const suit = tile[1];
    const isHonor = suit === "z";
    const main = isHonor ? honorLabels[tile] || tile[0] : tile[0] === "0" ? "5" : tile[0];
    const sub = isHonor ? "" : suitLabels[suit];
    let color = suitColors[suit] || "#333333";
    if (tile[0] === "0") color = "#c62828";
    if (honorColors[tile]) color = honorColors[tile];
    const subText = sub
      ? `<text x="36" y="72" font-size="12" fill="${color}" font-weight="700" text-anchor="middle">${sub}</text>`
      : "";
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="72" height="90" viewBox="0 0 72 90">
      <rect x="4" y="4" width="64" height="82" rx="10" ry="10" fill="#ffffff" stroke="#d4d4d4" stroke-width="2"/>
      <rect x="8" y="8" width="56" height="74" rx="8" ry="8" fill="#fbfbfb" stroke="#efefef"/>
      <text x="36" y="48" font-size="28" fill="${color}" font-weight="700" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif">${main}</text>
      ${subText}
    </svg>`;
    const src = `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
    tileCache.set(tile, src);
    return src;
  };

  const tileImg = (tile) => {
    if (tileImgCache.has(tile)) return tileImgCache.get(tile).cloneNode();
    const img = document.createElement("img");
    img.alt = tile;
    img.src = tileSrc(tile);
    img.decoding = "async";
    tileImgCache.set(tile, img);
    return img.cloneNode();
  };

  const normalizeTile = (tile) => {
    if (!tile) return tile;
    return tile[0] === "0" ? `5${tile[1]}` : tile;
  };

  const countInHand = (tile) => {
    const hand = targets.hand ? targets.hand.tiles : [];
    const key = normalizeTile(tile);
    return hand.filter((t) => normalizeTile(t) === key).length;
  };

  const toCompact = (tiles) => tiles.join("");
  const toCsv = (tiles) => tiles.join(",");

  const setActive = (name) => {
    const target = targets[name];
    if (!target) return;
    active = target;
    Object.values(targets).forEach((t) => {
      t.el.classList.toggle("active", t === target);
    });
  };

  const renderTarget = (target) => {
    const slots = target.el.querySelector("[data-slots]");
    if (!slots) return;
    slots.textContent = "";
    const frag = document.createDocumentFragment();
    for (let i = 0; i < target.max; i += 1) {
      const slot = document.createElement("button");
      slot.type = "button";
      slot.className = "tile-slot";
      slot.dataset.slotIndex = i.toString();
      const tile = target.tiles[i];
      if (tile) {
        slot.classList.add("filled");
        slot.appendChild(tileImg(tile));
        slot.setAttribute("aria-label", tile);
      } else {
        const empty = document.createElement("span");
        empty.className = "tile-empty";
        empty.textContent = "+";
        slot.appendChild(empty);
      }
      frag.appendChild(slot);
    }
    slots.appendChild(frag);
    const count = target.el.querySelector("[data-count]");
    if (count) {
      count.textContent = `${target.tiles.length}/${target.max}`;
    }
  };

  const updateInputs = () => {
    if (inputs.hand) inputs.hand.value = toCompact(targets.hand ? targets.hand.tiles : []);
    if (inputs.win) inputs.win.value = targets.win && targets.win.tiles[0] ? targets.win.tiles[0] : "";
    if (inputs.dora) inputs.dora.value = toCsv(targets.dora ? targets.dora.tiles : []);
    if (inputs.ura) inputs.ura.value = toCsv(targets.ura ? targets.ura.tiles : []);
  };

  const updateWarning = () => {
    const warning = picker.querySelector("[data-warning]");
    if (!warning) return;
    const win = targets.win && targets.win.tiles[0] ? targets.win.tiles[0] : "";
    if (win && targets.hand) {
      const key = normalizeTile(win);
      const has = targets.hand.tiles.some((tile) => normalizeTile(tile) === key);
      if (!has) {
      warning.textContent = warning.dataset.warningText || "";
      return;
      }
    }
    warning.textContent = "";
  };

  const renderAll = () => {
    Object.values(targets).forEach(renderTarget);
    updateInputs();
    updateWarning();
  };

  const addTile = (tile) => {
    if (!active || !tileSet.has(tile)) return;
    if (active.max === 1) {
      active.tiles = [tile];
      renderAll();
      return;
    }
    if (active.tiles.length >= active.max) return;
    if (active.name === "hand" && countInHand(tile) >= 4) return;
    active.tiles.push(tile);
    renderAll();
  };

  const removeTile = (target, index) => {
    if (!target) return;
    if (index < 0 || index >= target.tiles.length) return;
    target.tiles.splice(index, 1);
    renderAll();
  };

  const clearTarget = (target) => {
    if (!target) return;
    target.tiles = [];
    renderAll();
  };

  const clearAll = () => {
    Object.values(targets).forEach((t) => {
      t.tiles = [];
    });
    renderAll();
  };

  const undo = () => {
    if (!active || !active.tiles.length) return;
    active.tiles.pop();
    renderAll();
  };

  const initValues = () => {
    if (inputs.hand) targets.hand.tiles = parseCompact(inputs.hand.value).slice(0, targets.hand.max);
    if (inputs.win) targets.win.tiles = parseCompact(inputs.win.value).slice(0, targets.win.max);
    if (inputs.dora) targets.dora.tiles = parseCsv(inputs.dora.value).slice(0, targets.dora.max);
    if (inputs.ura) targets.ura.tiles = parseCsv(inputs.ura.value).slice(0, targets.ura.max);
  };

  const buildBank = () => {
    suitOrder.forEach((suit) => {
      const group = picker.querySelector(`.tile-bank-group[data-suit="${suit}"]`);
      const row = group ? group.querySelector(".tile-bank-row") : null;
      if (!row) return;
      for (let i = 1; i <= suitMax[suit]; i += 1) {
        const tile = `${i}${suit}`;
        const button = document.createElement("button");
        button.type = "button";
        button.className = "tile-button";
        button.dataset.tile = tile;
        button.setAttribute("aria-label", tile);
        button.appendChild(tileImg(tile));
        row.appendChild(button);
        if (i === 5 && suit !== "z") {
          const red = `0${suit}`;
          const redButton = document.createElement("button");
          redButton.type = "button";
          redButton.className = "tile-button";
          redButton.dataset.tile = red;
          redButton.setAttribute("aria-label", red);
          redButton.appendChild(tileImg(red));
          row.appendChild(redButton);
        }
      }
    });
  };

  buildBank();
  initValues();
  renderAll();

  Object.values(targets).forEach((target) => {
    target.el.addEventListener("click", (event) => {
      const action = event.target.closest("[data-action]");
      if (action && action.dataset.action === "clear-target") {
        clearTarget(target);
        setActive(target.name);
        return;
      }
      const slot = event.target.closest("[data-slot-index]");
      if (slot) {
        const index = Number(slot.dataset.slotIndex || -1);
        removeTile(target, index);
        setActive(target.name);
        return;
      }
      setActive(target.name);
    });
  });

  const bank = picker.querySelector("[data-bank]");
  if (bank) {
    bank.addEventListener("click", (event) => {
      const button = event.target.closest("[data-tile]");
      if (!button) return;
      addTile(button.dataset.tile);
    });
  }

  picker.addEventListener("click", (event) => {
    const action = event.target.closest("[data-action]");
    if (!action) return;
    if (action.dataset.action === "undo") {
      undo();
    } else if (action.dataset.action === "clear-all") {
      clearAll();
    }
  });
})();
