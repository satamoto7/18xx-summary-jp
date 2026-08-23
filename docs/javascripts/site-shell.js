(() => {
  "use strict";

  const PAGE_CLASSES = ["is-home", "is-game-index", "is-game-summary"];

  function normalizedPath(value) {
    const path = new URL(value, window.location.href).pathname;
    return path.endsWith("/") ? path : `${path}/`;
  }

  function siteRootHref() {
    const logo = document.querySelector(".md-header__button.md-logo[href]");
    if (logo) {
      return logo.href;
    }
    const canonical = document.querySelector('link[rel="canonical"][href]');
    if (canonical) {
      return new URL("./", canonical.href).href;
    }
    return new URL("./", window.location.href).href;
  }

  function pageFamily(rootHref) {
    const currentPath = normalizedPath(window.location.href);
    const rootPath = normalizedPath(rootHref);
    const gamesPath = normalizedPath(new URL("games/", rootHref).href);
    if (currentPath === rootPath) {
      return "home";
    }
    if (currentPath === gamesPath) {
      return "game-index";
    }
    if (currentPath.startsWith(gamesPath)) {
      return "game-summary";
    }
    return "content";
  }

  function applyPageClass(family) {
    PAGE_CLASSES.forEach((className) => document.body.classList.remove(className));
    if (family !== "content") {
      document.body.classList.add(`is-${family}`);
    }
    document.body.dataset.pageFamily = family;
  }

  function ensureHeaderNavigation(rootHref, family) {
    const inner = document.querySelector(".md-header__inner");
    if (!inner) {
      return;
    }

    let navigation = inner.querySelector(".signal-header-nav");
    if (!navigation) {
      navigation = document.createElement("nav");
      navigation.className = "signal-header-nav";
      navigation.setAttribute("aria-label", "主要ナビゲーション");
      navigation.innerHTML = '<a class="signal-header-nav__link" href="">ゲーム一覧</a>';
      const search = inner.querySelector(".md-search");
      inner.insertBefore(navigation, search || null);
    }

    const gamesLink = navigation.querySelector(".signal-header-nav__link");
    gamesLink.href = new URL("games/", rootHref).href;
    if (family === "game-index") {
      gamesLink.setAttribute("aria-current", "page");
    } else {
      gamesLink.removeAttribute("aria-current");
    }
  }

  function wrapSummaryIdentity(family) {
    if (family !== "game-summary") {
      return;
    }
    const content = document.querySelector(".md-content__inner");
    if (!content || content.querySelector(":scope > .summary-identity")) {
      return;
    }

    const heading = content.querySelector(":scope > h1");
    const actions = content.querySelector(":scope > .actions");
    if (!heading || !actions) {
      return;
    }

    const identity = document.createElement("section");
    identity.className = "summary-identity";
    identity.setAttribute("aria-labelledby", heading.id || "summary-title");
    if (!heading.id) {
      heading.id = "summary-title";
    }
    content.insertBefore(identity, heading);
    identity.append(heading, actions);
  }

  function labelSecondaryNavigation() {
    document.querySelectorAll(".md-nav--secondary .md-nav__link").forEach((link) => {
      const label = link.textContent.trim();
      if (label && !link.title) {
        link.title = label;
      }
    });
  }

  function initSiteShell() {
    const rootHref = siteRootHref();
    const family = pageFamily(rootHref);
    applyPageClass(family);
    ensureHeaderNavigation(rootHref, family);
    wrapSummaryIdentity(family);
    labelSecondaryNavigation();
  }

  window.addEventListener("pageshow", initSiteShell);
  if (typeof document$ !== "undefined" && document$ && typeof document$.subscribe === "function") {
    document$.subscribe(initSiteShell);
  } else {
    document.addEventListener("DOMContentLoaded", initSiteShell);
  }
})();
