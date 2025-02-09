let deferredPrompt;

window.addEventListener("beforeinstallprompt", (event) => {
  // Prevent automatic prompt display
  event.preventDefault();
  deferredPrompt = event;

  // Show the install button
  const installButton = document.getElementById("install-btn");
  if (installButton) {
    installButton.style.display = "block";

    // Handle button click to trigger installation
    installButton.addEventListener("click", () => {
      deferredPrompt.prompt();

      deferredPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === "accepted") {
          console.log("User accepted the install prompt");
        } else {
          console.log("User dismissed the install prompt");
        }
        deferredPrompt = null;
        installButton.style.display = "none"; // Hide after action
      });
    });
  }
});
