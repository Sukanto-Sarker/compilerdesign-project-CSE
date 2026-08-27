const sourceCode = document.getElementById("sourceCode");
const compileBtn = document.getElementById("compileBtn");
const clearBtn = document.getElementById("clearBtn");
const exampleBtn = document.getElementById("exampleBtn");

const tokenBody = document.getElementById("tokenBody");
const symbolBody = document.getElementById("symbolBody");

const astOutput = document.getElementById("astOutput");
const tacOutput = document.getElementById("tacOutput");
const resultBox = document.getElementById("resultBox");

const exampleProgram = `START
x = 10;
y = 20;
result = x + y * 2;
PRINT result;
END`;


exampleBtn.addEventListener("click", () => {
    sourceCode.value = exampleProgram;
});


clearBtn.addEventListener("click", () => {

    sourceCode.value = "";

    tokenBody.innerHTML = "";
    symbolBody.innerHTML = "";

    astOutput.textContent = "";
    tacOutput.textContent = "";

    resultBox.innerHTML = `
        <p class="text-slate-400">
            Click Compile to analyze your program.
        </p>
    `;

    resetPhases();
});


function resetPhases() {

    document.querySelectorAll(".phase").forEach(phase => {

        const status =
            phase.querySelector(".phase-status");

        status.textContent = "Waiting";

        status.className =
            "phase-status text-slate-500";

    });
}


function updatePhase(name, state) {

    const phase =
        document.querySelector(
            `[data-phase="${name}"]`
        );

    if (!phase) return;

    const status =
        phase.querySelector(".phase-status");

    if (state === "success") {

        status.textContent = "✓ Success";

        status.className =
            "phase-status text-green-400 font-medium";

    } else if (state === "error") {

        status.textContent = "✗ Error";

        status.className =
            "phase-status text-red-400 font-medium";

    } else {

        status.textContent = "Waiting";

        status.className =
            "phase-status text-slate-500";
    }
}


function escapeHTML(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function showTokens(tokens) {

    tokenBody.innerHTML = "";

    if (!tokens.length) {

        tokenBody.innerHTML = `
            <tr>
                <td
                    colspan="4"
                    class="px-5 py-6 text-center
                    text-slate-500"
                >
                    No tokens
                </td>
            </tr>
        `;

        return;
    }

    tokens.forEach(token => {

        const row =
            document.createElement("tr");

        row.innerHTML = `
            <td class="px-5 py-3 font-mono">
                ${escapeHTML(token.type)}
            </td>

            <td class="px-5 py-3 font-mono text-sky-300">
                ${escapeHTML(token.value)}
            </td>

            <td class="px-5 py-3">
                ${token.line}
            </td>

            <td class="px-5 py-3">
                ${token.column}
            </td>
        `;

        tokenBody.appendChild(row);
    });
}


function showSymbolTable(symbolTable) {

    symbolBody.innerHTML = "";

    const names =
        Object.keys(symbolTable);

    if (!names.length) {

        symbolBody.innerHTML = `
            <tr>
                <td
                    colspan="2"
                    class="px-5 py-6 text-center
                    text-slate-500"
                >
                    Symbol table is empty
                </td>
            </tr>
        `;

        return;
    }

    names.forEach(name => {

        const row =
            document.createElement("tr");

        row.innerHTML = `
            <td class="px-5 py-3 font-mono">
                ${escapeHTML(name)}
            </td>

            <td class="px-5 py-3">
                ${escapeHTML(
                    symbolTable[name].type
                )}
            </td>
        `;

        symbolBody.appendChild(row);
    });
}


function showSuccess() {

    resultBox.innerHTML = `
        <div class="flex items-start gap-4">

            <div
                class="w-10 h-10 rounded-xl
                bg-green-400/10
                flex items-center justify-center"
            >
                <span class="text-green-400 text-xl">
                    ✓
                </span>
            </div>

            <div>

                <h3
                    class="text-lg font-semibold
                    text-green-400"
                >
                    Compilation Successful
                </h3>

                <p class="text-slate-400 mt-1">
                    All compiler phases completed
                    successfully.
                </p>

            </div>

        </div>
    `;
}


function showError(error) {

    resultBox.innerHTML = `
        <div>

            <h3
                class="text-lg font-semibold
                text-red-400"
            >
                ${escapeHTML(error.type)}
            </h3>

            <p class="mt-3 text-slate-300 font-mono text-sm">
                ${escapeHTML(error.message)}
            </p>

        </div>
    `;
}


compileBtn.addEventListener("click", async () => {

    const source = sourceCode.value.trim();

    if (!source) {

        resultBox.innerHTML = `
            <p class="text-yellow-400">
                Please enter MiniLang source code.
            </p>
        `;

        return;
    }

    compileBtn.disabled = true;

    compileBtn.textContent = "Compiling...";

    resetPhases();

    try {

        const response =
            await fetch("/api", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    source: source
                })

            });

        const data =
            await response.json();

        updatePhase(
            "lexical",
            data.phases?.lexical
        );

        updatePhase(
            "syntax",
            data.phases?.syntax
        );

        updatePhase(
            "semantic",
            data.phases?.semantic
        );

        updatePhase(
            "intermediate",
            data.phases?.intermediate
        );

        showTokens(data.tokens || []);

        showSymbolTable(
            data.symbol_table || {}
        );

        astOutput.textContent =
            JSON.stringify(
                data.ast || {},
                null,
                2
            );

        tacOutput.textContent =
            (data.intermediate_code || [])
                .join("\n");

        if (data.success) {

            showSuccess();

        } else if (data.error) {

            showError(data.error);

        }

        openTab("result");

    } catch (error) {

        showError({
            type: "Connection Error",
            message:
                "Could not connect to the Python compiler."
        });

    } finally {

        compileBtn.disabled = false;

        compileBtn.textContent = "Compile";

    }

});


/* Tabs */

const tabButtons =
    document.querySelectorAll(".tab-btn");

const tabContents =
    document.querySelectorAll(".tab-content");


function openTab(name) {

    tabContents.forEach(content => {

        content.classList.add("hidden");

    });

    tabButtons.forEach(button => {

        button.classList.remove(
            "border-sky-400",
            "text-sky-400"
        );

        button.classList.add(
            "border-transparent",
            "text-slate-400"
        );

    });

    const content =
        document.getElementById(
            `tab-${name}`
        );

    content.classList.remove("hidden");

    const button =
        document.querySelector(
            `[data-tab="${name}"]`
        );

    if (button) {

        button.classList.remove(
            "border-transparent",
            "text-slate-400"
        );

        button.classList.add(
            "border-sky-400",
            "text-sky-400"
        );
    }
}


tabButtons.forEach(button => {

    button.addEventListener("click", () => {

        openTab(
            button.dataset.tab
        );

    });

});