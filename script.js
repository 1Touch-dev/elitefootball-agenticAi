function appendValue(value) {
    const display = document.getElementById('result');
    // Prevent multiple operators in a row
    const lastChar = display.value[display.value.length - 1];
    if (['+', '-', '*', '/'].includes(lastChar) && ['+', '-', '*', '/'].includes(value)) {
        return;
    }
    display.value += value;
}

function clearDisplay() {
    document.getElementById('result').value = '';
}

function calculateResult() {
    try {
        document.getElementById('result').value = eval(document.getElementById('result').value);
    } catch (error) {
        document.getElementById('result').value = 'Error';
    }
}

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
}
