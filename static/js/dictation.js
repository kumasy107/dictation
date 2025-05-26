function checkAnswer() {
    const input = document.getElementById('userInput').value;
    fetch('', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: input })
    })
    .then(res => res.json())
    .then(data => {
        const resultElem = document.getElementById('result');
        resultElem.innerText = data.result + (data.correct ? `: ${data.correct}` : '');

        // 色を設定（正解: 緑、不正解: 赤）
        if (data.result.toLowerCase() === 'correct') {
            resultElem.style.color = 'green';
        } else {
            resultElem.style.color = 'red';
        }

        const vocabDiv = document.getElementById('vocab-info');
        vocabDiv.innerHTML = "<h3>Vocabulary Info</h3>";
        data.vocabularies.forEach(v => {
            vocabDiv.innerHTML += `
                <div class="vocab-block">
                    <b>${v.word}</b> [${v.pronunciation}]<br>
                    <span class="meaning">Meaning:</span> ${v.meaning}<br>
                    <span class="comment">Comment:</span> ${v.comment}<br><br>
                </div>`;
        });
    });
}
