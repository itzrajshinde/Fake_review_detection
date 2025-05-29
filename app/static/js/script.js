// File: app/static/js/script.js

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded and parsed.");

    // --- Get DOM Elements ---
    const commentForm = document.getElementById('comment-analyzer-form');
    const commentTextInput = document.getElementById('comment-text-input');
    const analyzeButton = document.getElementById('analyze-button');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorDisplay = document.getElementById('error-message');
    const resultSection = document.getElementById('result-section');
    const resultVerdict = document.getElementById('result-verdict');
    const resultSentiment = document.getElementById('result-sentiment');
    const resultConfidence = document.getElementById('result-confidence');
    const confidenceBarInner = document.getElementById('confidence-bar-inner');
    const themeToggleButton = document.getElementById('theme-toggle');
    const bodyElement = document.body;

    // --- Check if Model Loaded (Passed from Flask Template) ---
    const isModelLoaded = typeof window.MODEL_LOADED !== 'undefined' ? window.MODEL_LOADED : false;
    console.log("Model loaded status from window:", isModelLoaded);

    // --- Theme Toggle Logic ---
    function applyTheme(theme) {
        bodyElement.classList.remove('light-mode', 'dark-mode');
        if (theme === 'dark') {
            bodyElement.classList.add('dark-mode');
        } else {
            bodyElement.classList.add('light-mode');
        }
        console.log("Applied theme:", theme);
    }

    const savedTheme = localStorage.getItem('theme') || 'dark'; // Default to dark
    applyTheme(savedTheme);

    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', () => {
            const newTheme = bodyElement.classList.contains('dark-mode') ? 'light' : 'dark';
            applyTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        });
        console.log("Theme toggle listener attached.");
    } else {
        console.warn("Theme toggle button not found.");
    }

    // --- Form Submission Logic ---
    // Check if essential form elements exist first
    if (!commentForm) {
        console.error("CRITICAL: Form element #comment-analyzer-form not found!");
        return;
    }
    if (!commentTextInput) console.error("Form element #comment-text-input not found!");
    if (!analyzeButton) console.error("Form element #analyze-button not found!");
    if (!loadingIndicator) console.error("Form element #loading-indicator not found!");
    if (!errorDisplay) console.error("Form element #error-message not found!");
    if (!resultSection) console.error("Form element #result-section not found!");

    console.log("Analysis form elements seem to be present.");

    // Determine initial disabled state based on model status
    const isInitiallyDisabled = !isModelLoaded;
    if (isInitiallyDisabled) {
        console.warn("Model not loaded - disabling analysis form via JS.");
        disableForm(true);
    } else {
        disableForm(false);
    }

    // Attach the event listener
    commentForm.addEventListener('submit', async (event) => {
        console.log("Submit event triggered.");
        event.preventDefault();

        // Re-check if button is disabled (safety check)
        if (analyzeButton.disabled) {
            console.warn("Analyze button is disabled. Submission aborted.");
            return;
        }

        const commentText = commentTextInput.value.trim();
        if (!commentText) {
            console.log("Validation failed: No comment text.");
            showError('Please enter some text to analyze.');
            return;
        }

        console.log("Comment text retrieved:", commentText);

        // --- UI Updates ---
        disableForm(true);
        showElement(loadingIndicator, 'flex');
        hideElement(resultSection);
        hideElement(errorDisplay);
        resetResultDisplay();
        console.log("UI updated for loading state.");

        try {
            console.log("Attempting fetch to /analyze_comment...");
            // --- API Call ---
            const response = await fetch('/analyze_comment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ text: commentText })
            });
            console.log("Fetch response status:", response.status);

            const responseData = await handleResponse(response);
            console.log("Response data parsed:", responseData);
            displayResult(responseData);

        } catch (error) {
            console.error('Analysis Request Error:', error);
            showError(`Analysis Failed: ${error.message}`);
        } finally {
            console.log("Fetch finished (finally block).");
            hideElement(loadingIndicator);
            if (!isInitiallyDisabled) {
                disableForm(false);
            } else {
                console.log("Form remains disabled as model was not loaded initially.");
            }
        }
    });
    console.log("Submit event listener attached to form.");

    // --- Helper: Handle Fetch Response & JSON Parsing ---
    async function handleResponse(response) {
        let responseData;
        const responseText = await response.text();
        if (!responseText) {
            throw new Error(`Server returned empty response (Status: ${response.status})`);
        }
        try {
            responseData = JSON.parse(responseText);
        } catch (jsonError) {
            console.error("Response handling error - Invalid JSON:", jsonError);
            console.error("Received text:", responseText);
            throw new Error(`Server returned invalid data (Status: ${response.status}). Check server logs.`);
        }
        if (!response.ok) {
            throw new Error(responseData?.error || `Request failed (Status: ${response.status})`);
        }
        if (responseData.error) {
            throw new Error(responseData.error);
        }
        return responseData;
    }

    // --- Function to Display Result ---
    function displayResult(data) {
        if (!resultSection || !resultVerdict || !resultSentiment || !resultConfidence || !confidenceBarInner) {
            console.error("Result display elements missing!");
            showError("Page Error: Cannot display results.");
            return;
        }
        console.log("Displaying results:", data);

        resultVerdict.textContent = data.verdict ? data.verdict.toUpperCase() : 'Error';
        resultSentiment.textContent = data.sentiment ? data.sentiment.charAt(0).toUpperCase() + data.sentiment.slice(1) : 'N/A';
        resultConfidence.textContent = typeof data.confidence === 'number' ? `${data.confidence.toFixed(1)}%` : 'N/A';

        resultVerdict.className = 'result-verdict'; // Reset
        if (data.verdict === 'fake') {
            resultVerdict.classList.add('fake');
        } else if (data.verdict === 'genuine') {
            resultVerdict.classList.add('genuine');
        }

        resultSentiment.className = 'value'; // Reset
        if (data.sentiment === 'positive') {
            resultSentiment.classList.add('positive');
        } else if (data.sentiment === 'negative') {
            resultSentiment.classList.add('negative');
        }

        const confidencePercentage = typeof data.confidence === 'number' ? data.confidence : 0;
        requestAnimationFrame(() => {
            confidenceBarInner.style.width = `${confidencePercentage}%`;
            confidenceBarInner.style.backgroundColor = '';
            if (data.verdict === 'fake') {
                confidenceBarInner.style.backgroundColor = 'var(--danger-color)';
            } else if (data.verdict === 'genuine') {
                confidenceBarInner.style.backgroundColor = 'var(--success-color)';
            }
        });

        showElement(resultSection);
        setTimeout(() => {
            resultSection.classList.add('visible');
        }, 50);
        hideElement(errorDisplay);
    }

    // --- Function to Reset Result Display Area ---
    function resetResultDisplay() {
        if (!resultSection) return;
        resultSection.classList.remove('visible');
        if (resultVerdict) resultVerdict.textContent = '';
        if (resultSentiment) resultSentiment.textContent = '';
        if (resultConfidence) resultConfidence.textContent = '';
        if (confidenceBarInner) confidenceBarInner.style.width = '0%';
        if (resultVerdict) resultVerdict.className = 'result-verdict';
        if (resultSentiment) resultSentiment.className = 'value';
        console.log("Result display reset.");
    }

    // --- Helper: Show/Hide Elements ---
    function showElement(el, displayType = 'block') {
        if (el) el.style.display = displayType;
    }
    function hideElement(el) {
        if (el) el.style.display = 'none';
    }

    // --- Helper: Show Errors ---
    function showError(message) {
        if (errorDisplay) {
            errorDisplay.textContent = message;
            showElement(errorDisplay);
            hideElement(resultSection);
            console.log("Error displayed to user:", message);
        } else {
            console.error("Error display element not found! Error:", message);
        }
    }

    // --- Helper: Disable/Enable Form ---
    function disableForm(isDisabled) {
        if (commentTextInput) {
            commentTextInput.disabled = isDisabled;
        }
        if (analyzeButton) {
            analyzeButton.disabled = isDisabled;
        }
        console.log(`Form elements disabled state set to: ${isDisabled}`);
    }

    // Final check to disable form if model didn't load
    if (!isModelLoaded && analyzeButton && commentTextInput) {
        disableForm(true);
    }
}); // End DOMContentLoaded