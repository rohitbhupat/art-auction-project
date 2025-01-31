document.addEventListener("DOMContentLoaded", () => {
  const themeText = document.getElementById("bd-theme-text");
  const themeItems = document.querySelectorAll(".dropdown-item");
  const navbar = document.getElementById("navbar");

  const setTheme = (theme) => {
    document.body.classList.remove("light-mode", "dark-mode");
    navbar.classList.remove("light-mode", "dark-mode");

    if (theme === "light") {
      document.body.classList.add("light-mode");
      navbar.classList.add("light-mode");
      themeText.innerText = "Light Mode";
    } else if (theme === "dark") {
      document.body.classList.add("dark-mode");
      navbar.classList.add("dark-mode");
      themeText.innerText = "Dark Mode";
    } else {
      const prefersDarkScheme = window.matchMedia(
        "(prefers-color-scheme: dark)"
      ).matches;
      if (prefersDarkScheme) {
        document.body.classList.add("dark-mode");
        navbar.classList.add("dark-mode");
      } else {
        document.body.classList.add("light-mode");
        navbar.classList.add("light-mode");
      }
      themeText.innerText = "Auto Mode";
    }

    localStorage.setItem("theme", theme);
  };

  themeItems.forEach((item) => {
    item.addEventListener("click", (e) => {
      const theme = e.target.getAttribute("data-theme");
      setTheme(theme);
    });
  });

  const storedTheme = localStorage.getItem("theme") || "auto";
  setTheme(storedTheme);
});
