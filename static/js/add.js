let vocabIndex = 0;

function addVocabForm() {
    const container = document.getElementById('vocab-container');
    const div = document.createElement('div');
    div.id = `vocab-${vocabIndex}`;
    div.innerHTML = `
        <fieldset class="vocab-fieldset">
            <legend>Vocabulary ${vocabIndex + 1}</legend>
            <div class="form-row">
                <label for="vocab_${vocabIndex}_word">Word:</label>
                <input type="text" name="vocab_${vocabIndex}_word" id="vocab_${vocabIndex}_word" class="form-input">
            </div>
            <div class="form-row">
                <label for="vocab_${vocabIndex}_pron">Pronunciation:</label>
                <input type="text" name="vocab_${vocabIndex}_pron" id="vocab_${vocabIndex}_pron" class="form-input">
            </div>
            <div class="form-row">
                <label for="vocab_${vocabIndex}_meaning">Meaning:</label>
                <input type="text" name="vocab_${vocabIndex}_meaning" id="vocab_${vocabIndex}_meaning" class="form-input">
            </div>
            <div class="form-row">
                <label for="vocab_${vocabIndex}_comment">Comment:</label>
                <input type="text" name="vocab_${vocabIndex}_comment" id="vocab_${vocabIndex}_comment" class="form-input">
            </div>
            <button type="button" class="cancel-btn" onclick="removeVocabForm(${vocabIndex})">❌ Remove</button>
        </fieldset>
    `;
    container.appendChild(div);
    vocabIndex++;
    document.getElementById("vocab_count").value = vocabIndex;
}

function removeVocabForm(index) {
    const elem = document.getElementById(`vocab-${index}`);
    if (elem) {
        elem.remove();
        vocabIndex--;
        document.getElementById("vocab_count").value = vocabIndex;
    }
}
