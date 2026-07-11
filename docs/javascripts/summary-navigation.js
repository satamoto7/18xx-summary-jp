(() => {
  "use strict";

  const READY_ATTR = "data-summary-navigation-ready";
  const STORAGE_PREFIX = "18xx-summary-navigation:";
  let currentContexts = [];
  let hashHandlerAttached = false;

  function toQueryKey(text) {
    return String(text || "")
      .normalize("NFKC")
      .toLocaleLowerCase("ja-JP")
      .replace(/[\s\p{P}\p{S}_]+/gu, "");
  }

  function storageKey(context, suffix) {
    return `${STORAGE_PREFIX}${window.location.pathname}:${context.index}:${suffix}`;
  }

  function readStored(context, suffix) {
    try {
      return window.sessionStorage.getItem(storageKey(context, suffix));
    } catch (_) {
      return null;
    }
  }

  function writeStored(context, suffix, value) {
    try {
      window.sessionStorage.setItem(storageKey(context, suffix), String(value));
    } catch (_) {
      // Browsing remains fully usable when storage is unavailable.
    }
  }

  function activeIndex(context) {
    const index = context.inputs.findIndex((input) => input.checked);
    return index >= 0 ? index : 0;
  }

  function selectTab(context, index) {
    const input = context.inputs[index];
    if (!input) {
      return;
    }
    input.checked = true;
    context.activeIndex = index;
    writeStored(context, "active", index);
    renderNavigation(context);
    updateScrollableTables();
  }

  function restoreScroll(context, index) {
    const stored = Number.parseInt(readStored(context, `scroll:${index}`) || "", 10);
    if (!Number.isFinite(stored) || stored < 0) {
      return;
    }
    window.requestAnimationFrame(() => window.scrollTo({ top: stored, behavior: "auto" }));
  }

  function saveScroll(context) {
    writeStored(context, `scroll:${context.activeIndex}`, Math.max(0, Math.round(window.scrollY)));
  }

  function targetForHash() {
    const hash = window.location.hash.slice(1);
    if (!hash) {
      return null;
    }
    try {
      return document.getElementById(decodeURIComponent(hash));
    } catch (_) {
      return null;
    }
  }

  function contextForTarget(contexts, target) {
    if (!target) {
      return null;
    }
    const set = target.closest(".tabbed-set");
    return contexts.find((context) => context.set === set) || null;
  }

  function indexForTarget(context, target) {
    const inputIndex = context.inputs.indexOf(target);
    if (inputIndex >= 0) {
      return inputIndex;
    }
    const block = target.closest(".tabbed-block");
    return context.blocks.indexOf(block);
  }

  function openHashTarget(contexts) {
    const target = targetForHash();
    const context = contextForTarget(contexts, target);
    if (!context || !target) {
      return;
    }

    const index = indexForTarget(context, target);
    if (index < 0) {
      return;
    }

    selectTab(context, index);
    if (!target.matches('input[type="radio"]')) {
      window.requestAnimationFrame(() => target.scrollIntoView({ block: "start" }));
    }
  }

  function sectionText(heading) {
    const parts = [heading.textContent || ""];
    let current = heading.nextElementSibling;
    while (current && !current.matches("h2, h3")) {
      parts.push(current.textContent || "");
      current = current.nextElementSibling;
    }
    return parts.join(" ");
  }

  function buildEntries(context) {
    return context.blocks.flatMap((block, tabIndex) =>
      Array.from(block.querySelectorAll("h2, h3"))
        .filter((heading) => heading.id)
        .map((heading) => ({
          tabIndex,
          heading,
          label: heading.textContent.replace("¶", "").trim(),
          searchKey: toQueryKey(sectionText(heading)),
        }))
    );
  }

  function addResultLink(list, context, entry) {
    const item = document.createElement("li");
    const link = document.createElement("a");
    link.href = `#${encodeURIComponent(entry.heading.id)}`;
    link.textContent = entry.tabIndex === context.activeIndex
      ? entry.label
      : `${context.labels[entry.tabIndex]}：${entry.label}`;
    link.addEventListener("click", (event) => {
      event.preventDefault();
      context.navigation.details.open = false;
      const nextHash = `#${encodeURIComponent(entry.heading.id)}`;
      if (window.location.hash === nextHash) {
        openHashTarget([context]);
      } else {
        window.location.hash = nextHash;
      }
    });
    item.appendChild(link);
    list.appendChild(item);
  }

  function renderNavigation(context) {
    if (!context.navigation) {
      return;
    }
    const { input, list, status } = context.navigation;
    const query = toQueryKey(input.value);
    const entries = query
      ? context.entries.filter((entry) => entry.searchKey.includes(query))
      : context.entries.filter((entry) => entry.tabIndex === context.activeIndex);
    list.innerHTML = "";

    entries.slice(0, 20).forEach((entry) => addResultLink(list, context, entry));
    if (entries.length === 0) {
      status.textContent = query ? "該当する見出しはありません。" : "見出しはありません。";
    } else if (entries.length > 20) {
      status.textContent = `先頭の20件を表示しています。`;
    } else {
      status.textContent = "";
    }
  }

  function createNavigation(context) {
    const nav = document.createElement("nav");
    nav.className = "summary-nav";
    nav.setAttribute("aria-label", "サマリー内移動");
    nav.innerHTML = `
      <details class="summary-nav__details">
        <summary>目次・検索</summary>
        <div class="summary-nav__panel">
          <label class="summary-nav__label">このゲーム内を検索
            <input class="summary-nav__search" type="search" placeholder="見出し・本文で検索">
          </label>
          <p class="summary-nav__status" role="status" aria-live="polite"></p>
          <ol class="summary-nav__list"></ol>
        </div>
      </details>
    `;
    context.set.insertBefore(nav, context.content);

    const details = nav.querySelector(".summary-nav__details");
    const input = nav.querySelector(".summary-nav__search");
    const list = nav.querySelector(".summary-nav__list");
    const status = nav.querySelector(".summary-nav__status");
    context.navigation = { nav, details, input, list, status };
    input.addEventListener("input", () => renderNavigation(context));
    renderNavigation(context);
  }

  function updateScrollableTables() {
    Array.from(document.querySelectorAll(".md-typeset__table")).forEach((wrapper) => {
      const rect = wrapper.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) {
        return;
      }
      const isScrollable = wrapper.scrollWidth > wrapper.clientWidth + 1;
      wrapper.classList.toggle("summary-table--scrollable", isScrollable);
      let hint = wrapper.querySelector(".summary-table__hint");
      if (isScrollable && !hint) {
        hint = document.createElement("span");
        hint.className = "summary-table__hint";
        hint.setAttribute("aria-hidden", "true");
        hint.textContent = "横にスクロールできます";
        wrapper.appendChild(hint);
      }
      if (!isScrollable && hint) {
        hint.remove();
      }
    });
  }

  function createContext(set, index) {
    const inputs = Array.from(set.querySelectorAll(':scope > input[type="radio"]'));
    const content = set.querySelector(":scope > .tabbed-content");
    const blocks = content ? Array.from(content.querySelectorAll(":scope > .tabbed-block")) : [];
    const labels = Array.from(set.querySelectorAll(":scope > .tabbed-labels > label"))
      .map((label) => label.textContent.trim());
    if (inputs.length === 0 || inputs.length !== blocks.length) {
      return null;
    }
    return {
      set,
      index,
      inputs,
      blocks,
      labels: labels.length === inputs.length ? labels : inputs.map((_, itemIndex) => `タブ${itemIndex + 1}`),
      content,
      activeIndex: 0,
      entries: [],
      navigation: null,
    };
  }

  function initSummaryNavigation() {
    const contexts = Array.from(document.querySelectorAll(".md-typeset .tabbed-set"))
      .map((set, index) => set._summaryNavigationContext || createContext(set, index))
      .filter(Boolean);

    contexts.forEach((context) => {
      if (context.set.hasAttribute(READY_ATTR)) {
        return;
      }
      context.set.setAttribute(READY_ATTR, "true");
      context.set._summaryNavigationContext = context;
      context.activeIndex = activeIndex(context);
      context.entries = buildEntries(context);
      createNavigation(context);
      const savedActive = Number.parseInt(readStored(context, "active") || "", 10);
      if (!window.location.hash && Number.isInteger(savedActive) && context.inputs[savedActive]) {
        selectTab(context, savedActive);
        restoreScroll(context, savedActive);
      }

      context.inputs.forEach((input, index) => {
        input.addEventListener("change", () => {
          if (!input.checked || context.activeIndex === index) {
            return;
          }
          saveScroll(context);
          context.activeIndex = index;
          writeStored(context, "active", index);
          renderNavigation(context);
          restoreScroll(context, index);
          updateScrollableTables();
        });
      });
    });

    currentContexts = contexts;
    if (!hashHandlerAttached) {
      window.addEventListener("hashchange", () => openHashTarget(currentContexts));
      hashHandlerAttached = true;
    }
    if (contexts.length > 0) {
      window.requestAnimationFrame(() => {
        openHashTarget(contexts);
        updateScrollableTables();
      });
    }
  }

  let resizeFrame = 0;
  window.addEventListener("resize", () => {
    window.cancelAnimationFrame(resizeFrame);
    resizeFrame = window.requestAnimationFrame(updateScrollableTables);
  });

  if (typeof document$ !== "undefined" && document$ && typeof document$.subscribe === "function") {
    document$.subscribe(initSummaryNavigation);
  } else {
    document.addEventListener("DOMContentLoaded", initSummaryNavigation);
  }
})();
