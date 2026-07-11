(() => {
  "use strict";

  const FILTER_READY_ATTR = "data-game-filter-ready";
  const PARAMS = {
    query: "q",
    solo: "solo",
    minPlayers: "min_players",
    maxPlayers: "max_players",
    sort: "sort",
  };

  function parseIntAttr(element, attrName) {
    const raw = element.getAttribute(attrName);
    if (!raw) {
      return null;
    }
    const parsed = Number.parseInt(raw, 10);
    return Number.isFinite(parsed) ? parsed : null;
  }

  function toQueryKey(text) {
    return String(text || "")
      .normalize("NFKC")
      .toLocaleLowerCase("ja-JP")
      .replace(/[\s\p{P}\p{S}_]+/gu, "");
  }

  function normalizeRange(minValue, maxValue) {
    if (minValue !== null && maxValue !== null && minValue > maxValue) {
      return [maxValue, minValue];
    }
    return [minValue, maxValue];
  }

  function toNullableNumber(value) {
    if (!value) {
      return null;
    }
    const parsed = Number.parseInt(value, 10);
    return Number.isFinite(parsed) ? parsed : null;
  }

  function collectCards(listElement) {
    const cards = Array.from(listElement.querySelectorAll(".game-card"));
    const navigationLinks = Array.from(document.querySelectorAll(".md-nav a[href]"));

    function navigationAlias(summaryHref) {
      if (!summaryHref) {
        return "";
      }
      const summaryPath = new URL(summaryHref, window.location.href).pathname.replace(/\/$/, "");
      const matchingLink = navigationLinks.find((link) => {
        const linkPath = new URL(link.href, window.location.href).pathname.replace(/\/$/, "");
        return linkPath === summaryPath;
      });
      return matchingLink ? matchingLink.textContent.trim() : "";
    }

    return cards.map((card) => {
      const titleElement = card.querySelector(".game-card__title-text");
      const title = titleElement ? titleElement.textContent.trim() : "";
      const summaryHref = card.querySelector(".game-card__cta")?.getAttribute("href") || "";
      const bggHref = card.querySelector('.game-card__description a[href*="boardgamegeek.com"]')?.href || "";
      const searchText = [
        card.getAttribute("data-search-text"),
        title,
        navigationAlias(summaryHref),
        bggHref,
      ]
        .filter(Boolean)
        .join(" ");
      return {
        card,
        title,
        searchKey: toQueryKey(searchText),
        year: parseIntAttr(card, "data-year"),
        playersMin: parseIntAttr(card, "data-players-min"),
        playersMax: parseIntAttr(card, "data-players-max"),
      };
    });
  }

  function collectPlayerValues(cardItems) {
    const values = new Set();
    cardItems.forEach((item) => {
      const min = item.playersMin;
      const max = item.playersMax;
      if (!Number.isInteger(min) || !Number.isInteger(max) || min > max) {
        return;
      }
      for (let current = min; current <= max; current += 1) {
        values.add(current);
      }
    });
    return Array.from(values).sort((a, b) => a - b);
  }

  function buildOptionList(selectElement, values) {
    selectElement.innerHTML = "";
    const noneOption = document.createElement("option");
    noneOption.value = "";
    noneOption.textContent = "指定なし";
    selectElement.appendChild(noneOption);

    values.forEach((value) => {
      const option = document.createElement("option");
      option.value = String(value);
      option.textContent = `${value}人`;
      selectElement.appendChild(option);
    });
  }

  function setChipState(button, isActive) {
    button.classList.toggle("game-filter__chip--active", isActive);
    button.setAttribute("aria-pressed", String(isActive));
  }

  function readStateFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const sort = params.get(PARAMS.sort);
    return {
      query: params.get(PARAMS.query) || "",
      soloOnly: params.get(PARAMS.solo) === "1",
      rangeMin: toNullableNumber(params.get(PARAMS.minPlayers)),
      rangeMax: toNullableNumber(params.get(PARAMS.maxPlayers)),
      sortBy: sort === "year" ? "year" : "title",
    };
  }

  function writeStateToUrl(state) {
    const url = new URL(window.location.href);
    const params = url.searchParams;
    const values = [
      [PARAMS.query, state.query],
      [PARAMS.solo, state.soloOnly ? "1" : ""],
      [PARAMS.minPlayers, state.rangeMin === null ? "" : String(state.rangeMin)],
      [PARAMS.maxPlayers, state.rangeMax === null ? "" : String(state.rangeMax)],
      [PARAMS.sort, state.sortBy === "year" ? "year" : ""],
    ];

    values.forEach(([key, value]) => {
      if (value) {
        params.set(key, value);
      } else {
        params.delete(key);
      }
    });
    window.history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);
  }

  function hasActiveConditions(state) {
    return Boolean(
      state.query ||
        state.soloOnly ||
        state.rangeMin !== null ||
        state.rangeMax !== null ||
        state.sortBy !== "title"
    );
  }

  function createFilterUI(listElement, playerValues) {
    const filter = document.createElement("form");
    filter.className = "game-filter";
    filter.setAttribute("aria-label", "ゲーム絞り込み");
    filter.innerHTML = `
      <div class="game-filter__primary">
        <label class="game-filter__label" for="game-filter-query">ゲーム名</label>
        <div class="game-filter__query-row">
          <input class="game-filter__input" id="game-filter-query" type="search" placeholder="タイトル・別名で検索" aria-describedby="game-filter-status" />
          <button type="button" class="game-filter__clear" hidden>条件を解除</button>
        </div>
      </div>
      <details class="game-filter__advanced">
        <summary>詳細条件</summary>
        <div class="game-filter__advanced-body">
          <fieldset class="game-filter__fieldset">
            <legend>対応人数</legend>
            <div class="game-filter__range">
              <label>最少
                <select class="game-filter__select game-filter__select--min" aria-label="対応人数の最少値"></select>
              </label>
              <span class="game-filter__range-sep">〜</span>
              <label>最多
                <select class="game-filter__select game-filter__select--max" aria-label="対応人数の最多値"></select>
              </label>
            </div>
          </fieldset>
          <div class="game-filter__group game-filter__group--solo">
            <span class="game-filter__label">条件</span>
            <button type="button" class="game-filter__chip" data-filter="solo" aria-pressed="false">ソロ対応のみ</button>
          </div>
          <div class="game-filter__group game-filter__group--sort">
            <span class="game-filter__label">並び替え</span>
            <button type="button" class="game-filter__chip game-filter__chip--active" data-sort="title" aria-pressed="true">タイトル順</button>
            <button type="button" class="game-filter__chip" data-sort="year" aria-pressed="false">年代順</button>
          </div>
        </div>
      </details>
      <p class="game-filter__count" id="game-filter-status" role="status" aria-live="polite"></p>
      <p class="game-filter__empty" role="status" aria-live="polite" hidden>該当するゲームはありません。条件を解除してもう一度お試しください。</p>
    `;

    listElement.parentNode.insertBefore(filter, listElement);

    const minSelect = filter.querySelector(".game-filter__select--min");
    const maxSelect = filter.querySelector(".game-filter__select--max");
    buildOptionList(minSelect, playerValues);
    buildOptionList(maxSelect, playerValues);

    return {
      root: filter,
      searchInput: filter.querySelector(".game-filter__input"),
      clearButton: filter.querySelector(".game-filter__clear"),
      advanced: filter.querySelector(".game-filter__advanced"),
      soloButton: filter.querySelector('[data-filter="solo"]'),
      minSelect,
      maxSelect,
      sortButtons: Array.from(filter.querySelectorAll("[data-sort]")),
      countLabel: filter.querySelector(".game-filter__count"),
      emptyLabel: filter.querySelector(".game-filter__empty"),
    };
  }

  function compareByTitle(a, b) {
    return a.title.localeCompare(b.title, "ja");
  }

  function compareByYear(a, b) {
    const aYear = a.year;
    const bYear = b.year;
    const aMissing = !Number.isInteger(aYear);
    const bMissing = !Number.isInteger(bYear);
    if (aMissing && bMissing) {
      return compareByTitle(a, b);
    }
    if (aMissing) {
      return 1;
    }
    if (bMissing) {
      return -1;
    }
    if (aYear !== bYear) {
      return aYear - bYear;
    }
    return compareByTitle(a, b);
  }

  function syncControls(controls, state) {
    controls.searchInput.value = state.query;
    controls.minSelect.value = state.rangeMin === null ? "" : String(state.rangeMin);
    controls.maxSelect.value = state.rangeMax === null ? "" : String(state.rangeMax);
    setChipState(controls.soloButton, state.soloOnly);
    controls.sortButtons.forEach((button) => {
      setChipState(button, button.getAttribute("data-sort") === state.sortBy);
    });
    controls.advanced.open = state.soloOnly || state.rangeMin !== null || state.rangeMax !== null || state.sortBy !== "title";
    controls.clearButton.hidden = !hasActiveConditions(state);
  }

  function applyState(cardItems, listElement, controls, state) {
    const total = cardItems.length;
    let visibleCount = 0;
    const query = toQueryKey(state.query);
    const [rangeMin, rangeMax] = normalizeRange(state.rangeMin, state.rangeMax);

    cardItems.forEach((item) => {
      const matchesName = !query || item.searchKey.includes(query);
      const hasPlayers = Number.isInteger(item.playersMin) && Number.isInteger(item.playersMax);
      const supportsSolo = hasPlayers && item.playersMin <= 1 && item.playersMax >= 1;
      const matchesSolo = !state.soloOnly || !hasPlayers || supportsSolo;

      let matchesRange = true;
      if ((rangeMin !== null || rangeMax !== null) && hasPlayers) {
        if (rangeMin !== null && rangeMax !== null) {
          matchesRange = item.playersMin <= rangeMin && item.playersMax >= rangeMax;
        } else {
          const target = rangeMin !== null ? rangeMin : rangeMax;
          matchesRange = item.playersMin <= target && item.playersMax >= target;
        }
      }

      const isVisible = matchesName && matchesSolo && matchesRange;
      item.card.style.display = isVisible ? "" : "none";
      if (isVisible) {
        visibleCount += 1;
      }
    });

    const compare = state.sortBy === "year" ? compareByYear : compareByTitle;
    cardItems.slice().sort(compare).forEach((item) => listElement.appendChild(item.card));

    controls.countLabel.textContent = `${visibleCount} / ${total} タイトル`;
    controls.emptyLabel.hidden = visibleCount !== 0;
  }

  function initForList(listElement) {
    const existingRefresh = listElement._gameFilterRefresh;
    if (typeof existingRefresh === "function") {
      existingRefresh();
      return;
    }

    const cardItems = collectCards(listElement);
    if (cardItems.length === 0) {
      return;
    }

    const playerValues = collectPlayerValues(cardItems);
    const controls = createFilterUI(listElement, playerValues);
    const state = readStateFromUrl();

    function refreshFromUrl() {
      Object.assign(state, readStateFromUrl());
      syncControls(controls, state);
      applyState(cardItems, listElement, controls, state);
    }

    function update(nextState) {
      Object.assign(state, nextState);
      syncControls(controls, state);
      applyState(cardItems, listElement, controls, state);
      writeStateToUrl(state);
    }

    controls.root.addEventListener("submit", (event) => event.preventDefault());
    controls.searchInput.addEventListener("input", () => update({ query: controls.searchInput.value }));
    controls.soloButton.addEventListener("click", () => update({ soloOnly: !state.soloOnly }));
    controls.minSelect.addEventListener("change", () => update({ rangeMin: toNullableNumber(controls.minSelect.value) }));
    controls.maxSelect.addEventListener("change", () => update({ rangeMax: toNullableNumber(controls.maxSelect.value) }));
    controls.clearButton.addEventListener("click", () => {
      update({ query: "", soloOnly: false, rangeMin: null, rangeMax: null, sortBy: "title" });
    });
    controls.sortButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const sortBy = button.getAttribute("data-sort");
        if (sortBy === "title" || sortBy === "year") {
          update({ sortBy });
        }
      });
    });

    listElement._gameFilterRefresh = refreshFromUrl;
    listElement.setAttribute(FILTER_READY_ATTR, "true");
    refreshFromUrl();
  }

  function initGameFilter() {
    Array.from(document.querySelectorAll(".game-list")).forEach((listElement) => initForList(listElement));
  }

  window.addEventListener("pageshow", initGameFilter);
  if (typeof document$ !== "undefined" && document$ && typeof document$.subscribe === "function") {
    document$.subscribe(initGameFilter);
  } else {
    document.addEventListener("DOMContentLoaded", initGameFilter);
  }
})();
