const TOKEN_LIMIT = 35000; // tokens per minute
let tokensUsed = 0;
let startTime = Date.now();

function calculateAvailableTokens(): number {
    const elapsedMinutes = (Date.now() - startTime) / 60000;
    return Math.max(0, TOKEN_LIMIT * elapsedMinutes - tokensUsed);
}

function trackTokenUsage(tokens: number): void {
    tokensUsed += tokens;
    if (tokensUsed > TOKEN_LIMIT) {
        const waitTime = Math.ceil((tokensUsed - TOKEN_LIMIT) / (TOKEN_LIMIT / 60));
        console.warn(`Rate limit exceeded. Pausing for ${waitTime} seconds.`);
        setTimeout(() => {
            tokensUsed = 0;
            startTime = Date.now();
        }, waitTime * 1000);
    }
}

// Example usage
function processRequest(requestTokens: number): void {
    const availableTokens = calculateAvailableTokens();
    if (requestTokens > availableTokens) {
        console.error("Not enough tokens available. Please wait.");
        return;
    }
    trackTokenUsage(requestTokens);
    // ...process the request...
}
