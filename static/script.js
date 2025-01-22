document.getElementById('analyzeButton').addEventListener('click', () => {
    const sourceCode = document.getElementById('sourceCode').value;

    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `sourceCode=${encodeURIComponent(sourceCode)}`,
    })
        .then(response => response.json())
        .then(data => {
            const resultDiv = document.getElementById('result');
            if (data.error) {
                resultDiv.innerHTML = `<div class="error">${data.error}</div>`;
            } else {
                resultDiv.innerHTML = `<pre>${JSON.stringify(data.tokens, null, 2)}</pre>`;
            }
        })
        .catch(err => {
            console.error(err);
            document.getElementById('result').innerHTML = `<div class="error">An error occurred!</div>`;
        });
});
