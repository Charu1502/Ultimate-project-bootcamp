const lengthSlider = document.getElementById("length-slider");
const lengthNum = document.getElementById("length-num");

lengthSlider.addEventListener("input", function() {
  lengthNum.value = lengthSlider.value;
});

lengthNum.addEventListener("input", function() {
    if (lengthNum.value >= 8 && lengthNum.value <= 20) {
        lengthSlider.value = lengthNum.value;
    }
});

const punctuation = document.getElementById("punctuation");
const passwordOutput = document.getElementById("password"); // Variable name standardized
const generateBtn = document.getElementById("generate-btn");
const copyBtn = document.getElementById("copy-btn");

// Fixed arrow function syntax
generateBtn.addEventListener("click", async () => {
  const payload = {
    length: parseInt(lengthSlider.value),
    punctuation: punctuation.checked
  };

  try {
    const response = await fetch('/generate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'}, // Fixed missing comma
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (data.error) {
      passwordOutput.value = data.error;
    } else {
      passwordOutput.value = data.password;
    }
  } catch (error) {
    passwordOutput.value = "Server connection failed!";
    console.error("Fetch Error:", error);
  }
});

copyBtn.addEventListener('click', () => {
    if (passwordOutput.value === "Select an option!" || passwordOutput.value === "" || passwordOutput.value.includes("Error")) return;

    navigator.clipboard.writeText(passwordOutput.value);

    const originalText = copyBtn.innerText;
    copyBtn.innerText = "✅ Copied!";
    setTimeout(() => {
        copyBtn.innerText = originalText;
    }, 2000);
});