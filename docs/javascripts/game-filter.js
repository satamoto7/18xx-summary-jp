(() => {
  "use strict";

  const FILTER_READY_ATTR = "data-game-filter-ready";

  function parseIntAttr(element, attrName) {
    const raw = element.getAttribute(attrName);
    if (!raw) {
      return null;
    }
    const parsed = Number.parseInt(raw, 10);
    return Number.isFinite(parsed) ? parsed : null;
  }

  function toQueryKey(text) {
    return String(text || "").trim().toLocaleLowerCase("ja-JP");
  }

  function normalizeRange(minValue, maxValue) {
    if (minValue !== null && maxValue !== null && minValue > maxValue) {
      return [maxValue, minValue];
    }
    return [minValue, maxValue];
  }

  function collectCards(listElement) {
    const cards = Array.from(listElement.querySelectorAll(".game-card"));
    return cards.map((card) => {
      const titleElement = card.querySelector(".game-card__title-text");
      const title = titleElement ? titleElement.textContent.trim() : "";
      return {
        card,
        title,
        titleKey: toQueryKey(title),
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

  function createFilterUI(listElement, playerValues) {
    const filter = document.createElement("div");
    filter.className = "game-filter";
    filter.setAttribute("aria-label", "ゲーム絞り込み");

    filter.innerHTML = `
      <div class="game-filter__group game-filter__group--search">
        <span class="game-filter__label">ゲーム名</span>
        <input class="game-filter__input" type="search" placeholder="タイトルで検索" aria-label="ゲーム名で絞り込み" />
      </div>
      <div class="game-filter__group game-filter__group--solo">
        <span class="game-filter__label">条件</span>
        <button type="button" class="game-filter__chip" data-filter="solo" aria-pressed="false">ソロ対応のみ</button>
      </div>
      <div class="game-filter__group game-filter__group--range">
        <span class="game-filter__label">人数</span>
        <span class="game-filter__range-label">X</span>
        <select class="game-filter__select game-filter__select--min" aria-label="人数レンジ最小値"></select>
        <span class="game-filter__range-sep">〜</span>
        <span class="game-filter__range-label">Y</span>
        <select class="game-filter__select game-filter__select--max" aria-label="人数レンジ最大値"></select>
      </div>
      <div class="game-filter__group game-filter__group--sort">
        <span class="game-filter__label">並び替え</span>
        <button type="button" class="game-filter__chip game-filter__chip--active" data-sort="title" aria-pressed="true">タイトル順</button>
        <button type="button" class="game-filter__chip" data-sort="year" aria-pressed="false">年代順</button>
      </div>
      <span class="game-filter__count" hidden></span>
    `;

    listElement.parentNode.insertBefore(filter, listElement);

    const minSelect = filter.querySelector(".game-filter__select--min");
    const maxSelect = filter.querySelector(".game-filter__select--max");
    buildOptionList(minSelect, playerValues);
    buildOptionList(maxSelect, playerValues);

    return {
      root: filter,
      searchInput: filter.querySelector(".game-filter__input"),
      soloButton: filter.querySelector('[data-filter="solo"]'),
      minSelect,
      maxSelect,
      sortButtons: Array.from(filter.querySelectorAll("[data-sort]")),
      countLabel: filter.querySelector(".game-filter__count"),
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

  function toNullableNumber(value) {
    if (!value) {
      return null;
    }
    const parsed = Number.parseInt(value, 10);
    return Number.isFinite(parsed) ? parsed : null;
  }

  function applyState(cardItems, listElement, controls, state) {
    const total = cardItems.length;
    let visibleCount = 0;

    const [rangeMin, rangeMax] = normalizeRange(state.rangeMin, state.rangeMax);

    cardItems.forEach((item) => {
      const matchesName = !state.query || item.titleKey.includes(state.query);

      const hasPlayers =
        Number.isInteger(item.playersMin) && Number.isInteger(item.playersMax);
      const supportsSolo =
        hasPlayers && item.playersMin <= 1 && item.playersMax >= 1;
      const matchesSolo = !state.soloOnly || supportsSolo;

      let matchesRange = true;
      if (rangeMin !== null || rangeMax !== null) {
        if (!hasPlayers) {
          matchesRange = false;
        } else if (rangeMin !== null && rangeMax !== null) {
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
    const sorted = cardItems.slice().sort(compare);
    sorted.forEach((item) => {
      listElement.appendChild(item.card);
    });

    if (visibleCount === total) {
      controls.countLabel.hidden = true;
      controls.countLabel.textContent = "";
    } else {
      controls.countLabel.hidden = false;
      controls.countLabel.textContent = `${visibleCount} / ${total} タイトル`;
    }
  }

  function initForList(listElement) {
    if (listElement.getAttribute(FILTER_READY_ATTR) === "true") {
      return;
    }

    const cardItems = collectCards(listElement);
    if (cardItems.length === 0) {
      return;
    }

    const existingFilter = listElement.previousElementSibling;
    if (existingFilter && existingFilter.classList.contains("game-filter")) {
      listElement.setAttribute(FILTER_READY_ATTR, "true");
      return;
    }

    const playerValues = collectPlayerValues(cardItems);
    const controls = createFilterUI(listElement, playerValues);
    const state = {
      query: "",
      soloOnly: false,
      rangeMin: null,
      rangeMax: null,
      sortBy: "title",
    };

    controls.searchInput.addEventListener("input", () => {
      state.query = toQueryKey(controls.searchInput.value);
      applyState(cardItems, listElement, controls, state);
    });

    controls.soloButton.addEventListener("click", () => {
      state.soloOnly = !state.soloOnly;
      setChipState(controls.soloButton, state.soloOnly);
      applyState(cardItems, listElement, controls, state);
    });

    controls.minSelect.addEventListener("change", () => {
      state.rangeMin = toNullableNumber(controls.minSelect.value);
      applyState(cardItems, listElement, controls, state);
    });

    controls.maxSelect.addEventListener("change", () => {
      state.rangeMax = toNullableNumber(controls.maxSelect.value);
      applyState(cardItems, listElement, controls, state);
    });

    controls.sortButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const nextSort = button.getAttribute("data-sort");
        if (!nextSort || state.sortBy === nextSort) {
          return;
        }
        state.sortBy = nextSort;
        controls.sortButtons.forEach((targetButton) => {
          const active = targetButton === button;
          setChipState(targetButton, active);
        });
        applyState(cardItems, listElement, controls, state);
      });
    });

    applyState(cardItems, listElement, controls, state);
    listElement.setAttribute(FILTER_READY_ATTR, "true");
  }

  function initGameFilter() {
    const lists = Array.from(document.querySelectorAll(".game-list"));
    lists.forEach((listElement) => initForList(listElement));
  }

  if (typeof document$ !== "undefined" && document$ && typeof document$.subscribe === "function") {
    document$.subscribe(() => {
      initGameFilter();
    });
  } else {
    document.addEventListener("DOMContentLoaded", () => {
      initGameFilter();
    });
  }
})();
