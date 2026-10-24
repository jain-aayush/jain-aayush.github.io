// Progressive enhancement only: the résumé and browser Print work without JS.
const printButton = document.getElementById("print-resume");
if (printButton) {
  printButton.hidden = false;
  printButton.addEventListener("click", () => window.print());
}
