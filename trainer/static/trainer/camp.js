// A small pixel landscape for the matchup stage, drawn locally at sprite resolution.
function paintArena() {
    const canvas = document.querySelector(".arena canvas");
    if (!canvas) return;
    canvas.width = 360;
    canvas.height = 96;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    function rect(x, y, w, h, color) {
        ctx.fillStyle = color;
        ctx.fillRect(x, y, w, h);
    }
    rect(0, 0, 360, 96, "#dcebd3");
    for (const [x, y] of [[18, 11], [105, 20], [205, 9], [297, 16]]) {
        rect(x, y, 24, 3, "#f2f5e2");
        rect(x + 6, y - 3, 12, 4, "#f2f5e2");
    }
    for (let x = 0; x < 360; x += 4) {
        const far = Math.round(29 + 8 * Math.sin(x / 36) + 4 * Math.sin(x / 15));
        const near = Math.round(43 + 7 * Math.sin(x / 22));
        rect(x, far, 4, 65, "#b7cfab");
        rect(x, near, 4, 60, "#9dbb96");
    }
    function pine(x, y, size, color) {
        for (let row = 0; row < 6; row++) {
            rect(x - row * size, y + row * size * 2, (row * 2 + 1) * size, size * 2, color);
        }
        rect(x - size, y + 12 * size, size * 3, size * 3, color);
    }
    for (let x = 0; x < 370; x += 9) pine(x, 41 + Math.round(5 * Math.sin(x)), 1, "#7e9f7c");
    rect(0, 57, 360, 39, "#b8cd92");
    rect(0, 72, 360, 24, "#a8c38b");
    for (const x of [1, 12, 23, 339, 351, 360]) pine(x, 28 + x % 12, 2, "#668d70");
    for (let i = 0; i < 115; i++) {
        const x = (i * 97) % 360, y = 60 + (i * 19) % 36;
        rect(x, y, 2 + i % 4, 1, i % 3 ? "#91ad7d" : "#d8dfa9");
    }
}
paintArena();

const copyPhrase = document.querySelector("#copy-phrase");
if (copyPhrase && navigator.clipboard) {
    copyPhrase.hidden = false;
    copyPhrase.addEventListener("click", async () => {
        const phrase = document.querySelector("#issued");
        const status = document.querySelector("#copy-status");
        try {
            await navigator.clipboard.writeText(phrase.value);
            status.textContent = "Copied.";
        } catch {
            phrase.select();
            status.textContent = "Phrase selected. Use your device’s copy command.";
        }
    });
}

const lesson = document.getElementById("lesson");
let submitting = false;
if (lesson) lesson.addEventListener("submit", async (event) => {
    if (!event.submitter || !window.fetch) return;
    event.preventDefault();
    if (submitting) return;
    submitting = true;
    const form = event.target;
    const data = new FormData(form);
    if (event.submitter.name) data.set(event.submitter.name, event.submitter.value);
    lesson.setAttribute("aria-busy", "true");
    try {
        const response = await fetch(form.getAttribute("action") || window.location.pathname, {
            method: "POST", body: data, headers: {"X-Trainer-Fragment": "1"}
        });
        if (!response.ok) throw new Error("Practice update failed");
        lesson.innerHTML = await response.text();
        paintArena();
        const focus = lesson.querySelector(".feedback") || lesson.querySelector(".question h2, .summary .primary");
        if (focus) focus.focus({preventScroll: true});
    } catch {
        let status = lesson.querySelector("[data-error]");
        if (!status) {
            status = document.createElement("p");
            status.dataset.error = "true";
            status.setAttribute("role", "alert");
            form.after(status);
        }
        status.textContent = "Connection interrupted. Try again to sync your practice.";
    } finally {
        submitting = false;
        lesson.removeAttribute("aria-busy");
    }
});
