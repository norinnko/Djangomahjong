(() => {
  const form = document.getElementById("calc-form");
  if (!form) return;

  const container = document.querySelector(".container");
  const rawBase = container ? container.dataset.tileBase || "" : "";
  const tileBase = rawBase ? (rawBase.endsWith("/") ? rawBase : `${rawBase}/`) : "";
  const handDisplay = document.getElementById("hand-display");
  const paletteDisplay = document.getElementById("palette-display");
  const tabButtons = document.querySelectorAll("[data-suit]");
  const handInput = document.getElementById("hand-text");
  const winInput = document.getElementById("win-tile-text");
  const seatWind = document.getElementById("seat-wind");
  const isDealer = document.getElementById("is-dealer");
  const errorBox = document.getElementById("js-error");
  const modal = document.getElementById("result-modal");
  const scoreLabel = document.getElementById("score-label");
  const scoreMain = document.getElementById("score-main");
  const scoreSub = document.getElementById("score-sub");
  const yakuList = document.getElementById("yaku-list");
  const aiText = document.getElementById("ai-text");
  const paymentBreakdown = document.getElementById("payment-breakdown");
  const closeButton = document.getElementById("modal-close");

  const MAX_TILES = 14;
  let currentHand = [];

  const tileMap = {
    "1m": "Man1.svg",
    "2m": "Man2.svg",
    "3m": "Man3.svg",
    "4m": "Man4.svg",
    "5m": "Man5.svg",
    "0m": "Man5-Dora.svg",
    "6m": "Man6.svg",
    "7m": "Man7.svg",
    "8m": "Man8.svg",
    "9m": "Man9.svg",
    "1p": "Pin1.svg",
    "2p": "Pin2.svg",
    "3p": "Pin3.svg",
    "4p": "Pin4.svg",
    "5p": "Pin5.svg",
    "0p": "Pin5-Dora.svg",
    "6p": "Pin6.svg",
    "7p": "Pin7.svg",
    "8p": "Pin8.svg",
    "9p": "Pin9.svg",
    "1s": "Sou1.svg",
    "2s": "Sou2.svg",
    "3s": "Sou3.svg",
    "4s": "Sou4.svg",
    "5s": "Sou5.svg",
    "0s": "Sou5-Dora.svg",
    "6s": "Sou6.svg",
    "7s": "Sou7.svg",
    "8s": "Sou8.svg",
    "9s": "Sou9.svg",
    "1z": "Ton.svg",
    "2z": "Nan.svg",
    "3z": "Shaa.svg",
    "4z": "Pei.svg",
    "5z": "Haku.svg",
    "6z": "Hatsu.svg",
    "7z": "Chun.svg",
  };

  const suitTiles = {
    man: ["1m", "2m", "3m", "4m", "5m", "0m", "6m", "7m", "8m", "9m"],
    pin: ["1p", "2p", "3p", "4p", "5p", "0p", "6p", "7p", "8p", "9p"],
    sou: ["1s", "2s", "3s", "4s", "5s", "0s", "6s", "7s", "8s", "9s"],
    ji: ["1z", "2z", "3z", "4z", "5z", "6z", "7z"],
  };

  const tileSrc = (code) => `${tileBase}${tileMap[code] || ""}`;

  const normalizeTile = (code) => {
    if (!code || code.length !== 2) return code;
    return code[0] === "0" ? `5${code[1]}` : code;
  };

  const countTile = (code) => {
    const key = normalizeTile(code);
    return currentHand.filter((tile) => normalizeTile(tile) === key).length;
  };

  const setError = (message) => {
    if (!errorBox) return;
    if (!message) {
      errorBox.textContent = "";
      errorBox.hidden = true;
      return;
    }
    errorBox.textContent = message;
    errorBox.hidden = false;
  };

  const updateHidden = () => {
    if (handInput) handInput.value = currentHand.join("");
    if (winInput) winInput.value = currentHand.length ? currentHand[currentHand.length - 1] : "";
  };

  const renderHand = () => {
    if (!handDisplay) return;
    handDisplay.textContent = "";
    if (!currentHand.length) {
      const hint = document.createElement("span");
      hint.className = "hand-hint";
      hint.textContent = "下のリストから牌を選んでください";
      handDisplay.appendChild(hint);
      return;
    }

    currentHand.forEach((code, index) => {
      if (currentHand.length % 3 === 2 && index === currentHand.length - 1) {
        const divider = document.createElement("div");
        divider.className = "win-tile-divider";
        handDisplay.appendChild(divider);
      }

      const tile = document.createElement("div");
      tile.className = "tile";
      tile.dataset.index = index.toString();
      const img = document.createElement("img");
      img.src = tileSrc(code);
      img.alt = code;
      img.loading = "lazy";
      tile.appendChild(img);
      tile.addEventListener("click", () => removeTile(index));
      handDisplay.appendChild(tile);
    });
  };

  const renderPalette = (suit) => {
    if (!paletteDisplay) return;
    paletteDisplay.textContent = "";
    const tiles = suitTiles[suit] || [];
    tiles.forEach((code) => {
      const tile = document.createElement("div");
      tile.className = "tile";
      tile.dataset.tile = code;
      const img = document.createElement("img");
      img.src = tileSrc(code);
      img.alt = code;
      img.loading = "lazy";
      tile.appendChild(img);
      tile.addEventListener("click", () => addTile(code));
      paletteDisplay.appendChild(tile);
    });
  };

  const addTile = (code) => {
    if (currentHand.length >= MAX_TILES) {
      setError("牌は14枚までです。");
      return;
    }
    if (countTile(code) >= 4) {
      setError("同じ牌は4枚までです。");
      return;
    }
    currentHand.push(code);
    setError("");
    renderHand();
    updateHidden();
  };

  const removeTile = (index) => {
    if (index < 0 || index >= currentHand.length) return;
    currentHand.splice(index, 1);
    setError("");
    renderHand();
    updateHidden();
  };

  const clearHand = () => {
    currentHand = [];
    setError("");
    renderHand();
    updateHidden();
  };

  const parseCompact = (value) => {
    const s = (value || "").trim().toLowerCase().replace(/\s+/g, "");
    if (!s) return [];
    let buf = "";
    const out = [];
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
        out.push(`${d}${ch}`);
      }
      buf = "";
    }
    return out;
  };

  const initFromInputs = () => {
    if (!handInput) return;
    const base = parseCompact(handInput.value);
    const win = (winInput ? winInput.value : "").trim().toLowerCase();
    if (win) {
      let idx = base.findIndex((tile) => tile === win);
      if (idx < 0) {
        const key = normalizeTile(win);
        idx = base.findIndex((tile) => normalizeTile(tile) === key);
      }
      if (idx >= 0) base.splice(idx, 1);
      base.push(win);
    }
    currentHand = base.slice(0, MAX_TILES);
    renderHand();
    updateHidden();
  };

  const updateDealer = () => {
    if (!isDealer || !seatWind) return;
    isDealer.checked = seatWind.value === "E";
  };

  const formatPoints = (value) => {
    const num = Number(value || 0);
    return num.toLocaleString("ja-JP");
  };

  const renderBreakdown = (payout) => {
    if (!paymentBreakdown) return;
    paymentBreakdown.textContent = "";
    if (!payout) return;
    const lines = [];
    if (payout.type === "ron") {
      lines.push(`放銃から: ${formatPoints(payout.pay_from_loser || 0)} 点`);
    } else if (payout.each_pay) {
      lines.push(`子から: ${formatPoints(payout.each_pay)} 点 ×3`);
    } else {
      lines.push(`親から: ${formatPoints(payout.dealer_pay || 0)} 点`);
      lines.push(`子から: ${formatPoints(payout.non_dealer_pay || 0)} 点 ×2`);
    }
    if (payout.riichi_sticks_bonus) {
      lines.push(`リーチ棒: +${formatPoints(payout.riichi_sticks_bonus)} 点`);
    }
    if (payout.total_gain) {
      lines.push(`合計: ${formatPoints(payout.total_gain)} 点`);
    }
    lines.forEach((line) => {
      const p = document.createElement("p");
      p.textContent = line;
      paymentBreakdown.appendChild(p);
    });
  };

  const renderResult = (result) => {
    if (!result) return;
    const payout = result.payout || {};
    if (scoreLabel) {
      scoreLabel.textContent = payout.type === "tsumo" ? "ツモ" : "ロン";
    }
    if (scoreMain) {
      scoreMain.textContent = `${formatPoints(payout.total_gain || 0)} 点`;
    }
    if (scoreSub) {
      scoreSub.textContent = `(${result.fu || 0}符 ${result.han || 0}翻)`;
    }
    if (yakuList) {
      yakuList.textContent = "";
      const names = result.yaku_names || [];
      if (!names.length) {
        const li = document.createElement("li");
        li.textContent = "役なし";
        yakuList.appendChild(li);
      } else {
        names.forEach((name) => {
          const li = document.createElement("li");
          li.textContent = name;
          yakuList.appendChild(li);
        });
      }
    }
    if (aiText) {
      aiText.textContent = result.explain_text || "説明がありません。";
    }
    renderBreakdown(payout);
  };

  const openModal = () => {
    if (modal) modal.style.display = "flex";
  };

  const closeModal = () => {
    if (modal) modal.style.display = "none";
  };

  const submitForm = async (event) => {
    event.preventDefault();
    setError("");
    updateDealer();
    updateHidden();

    if (currentHand.length < MAX_TILES) {
      setError("牌が足りません（少牌）。");
      return;
    }
    if (currentHand.length > MAX_TILES) {
      setError("牌が多すぎます。");
      return;
    }

    const csrf = form.querySelector("[name=csrfmiddlewaretoken]");
    const headers = {
      "X-Requested-With": "XMLHttpRequest",
    };
    if (csrf) headers["X-CSRFToken"] = csrf.value;

    try {
      const res = await fetch(form.action || window.location.href, {
        method: "POST",
        headers,
        body: new FormData(form),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        throw new Error(data.error || "計算に失敗しました。");
      }
      renderResult(data.result);
      openModal();
    } catch (err) {
      setError(err.message || "計算に失敗しました。");
    }
  };

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      tabButtons.forEach((btn) => btn.classList.remove("active"));
      button.classList.add("active");
      renderPalette(button.dataset.suit);
    });
  });

  const clearButton = document.querySelector("[data-action='clear']");
  if (clearButton) {
    clearButton.addEventListener("click", clearHand);
  }

  if (seatWind) {
    seatWind.addEventListener("change", updateDealer);
  }

  if (closeButton) {
    closeButton.addEventListener("click", closeModal);
  }

  if (modal) {
    modal.addEventListener("click", (event) => {
      if (event.target === modal) closeModal();
    });
  }

  form.addEventListener("submit", submitForm);

  updateDealer();
  initFromInputs();
  renderPalette("man");
})();
