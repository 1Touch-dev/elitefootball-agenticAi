describe('Calculator Tests', () => {
    let display;
    beforeEach(() => {
        // Set up our document body
        document.body.innerHTML = `
            <div class="calculator">
                <div class="display">
                    <input type="text" id="result" disabled>
                </div>
                <div class="buttons">
                    <button class="btn" onclick="clearDisplay()">C</button>
                    <button class="btn" onclick="appendValue('/')">/</button>
                    <button class="btn" onclick="appendValue('*')">*</button>
                    <button class="btn" onclick="appendValue('-')">-</button>
                    <button class="btn" onclick="appendValue('7')">7</button>
                    <button class="btn" onclick="appendValue('8')">8</button>
                    <button class="btn" onclick="appendValue('9')">9</button>
                    <button class="btn" onclick="appendValue('+')">+</button>
                    <button class="btn" onclick="appendValue('4')">4</button>
                    <button class="btn" onclick="appendValue('5')">5</button>
                    <button class="btn" onclick="appendValue('6')">6</button>
                    <button class="btn" onclick="calculateResult()">=</button>
                    <button class="btn" onclick="appendValue('1')">1</button>
                    <button class="btn" onclick="appendValue('2')">2</button>
                    <button class="btn" onclick="appendValue('3')">3</button>
                    <button class="btn" onclick="appendValue('0')">0</button>
                    <button class="btn" onclick="toggleDarkMode()">🌙</button>
                </div>
            </div>
        `;
        display = document.getElementById('result');
    });

    test('Appending values updates the display', () => {
        appendValue('5');
        appendValue('+');
        appendValue('3');
        expect(display.value).toBe('5+3');
    });

    test('Clear display works', () => {
        appendValue('8');
        clearDisplay();
        expect(display.value).toBe('');
    });

    test('Calculation works correctly', () => {
        appendValue('7');
        appendValue('+');
        appendValue('8');
        calculateResult();
        expect(display.value).toBe('15');
    });

    test('Multiple operators are handled', () => {
        appendValue('6');
        appendValue('+');
        appendValue('+');
        appendValue('3');
        calculateResult();
        expect(display.value).toBe('9');
    });
});
