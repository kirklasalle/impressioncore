document.addEventListener("DOMContentLoaded", () => {
    const advancedToggle = document.getElementById("advanced-settings-toggle");
    const advancedTabs = document.getElementById("advanced-settings-tabs");

    advancedToggle.addEventListener("change", (event) => {
        advancedTabs.style.display = event.target.checked ? "block" : "none";
    });

    // Populate tabs with configuration options
    const config = fetch("/config/model_config.json").then((res) => res.json());
    config.then((data) => {
        populateTab("architecture-tab", data.architecture);
        populateTab("optimization-tab", data.optimization);
    });

    function populateTab(tabId, settings) {
        const tab = document.getElementById(tabId);
        Object.entries(settings).forEach(([key, value]) => {
            const settingDiv = document.createElement("div");
            if (Array.isArray(value)) {
                // Create dropdown for advanced options
                const select = document.createElement("select");
                value.forEach((option) => {
                    const opt = document.createElement("option");
                    opt.value = option;
                    opt.textContent = option;
                    select.appendChild(opt);
                });
                settingDiv.innerHTML = `<label>${key}:</label>`;
                settingDiv.appendChild(select);
            } else {
                // Create input for standard options
                settingDiv.innerHTML = `<label>${key}: <input value="${JSON.stringify(value)}" /></label>`;
            }
            tab.appendChild(settingDiv);
        });
    }

    const initializeButton = document.getElementById("initialize-model-button");
    const fileInput = document.getElementById("config-file-input");

    initializeButton.addEventListener("click", () => {
        const selectedFile = fileInput.files[0];
        if (!selectedFile) {
            alert("Please select a configuration file.");
            return;
        }

        const formData = new FormData();
        formData.append("configFile", selectedFile);

        fetch("http://127.0.0.1:5000/initialize-model", {
            method: "POST",
            body: formData,
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Failed to initialize model.");
                }
                return response.json();
            })
            .then((data) => {
                alert(`Model initialized successfully: ${data.message}`);
            })
            .catch((error) => {
                console.error(error);
                alert("Error initializing model. Check console for details.");
            });
    });
});
