const index = new FlexSearch.Document({
    document: {
        id: "MID",
        store: true,
        index: [
            {
                field: "UID",
                // important: a forward tokenizer is minimum
                // required by an instant search
                tokenize: "forward"
            },
            {
                field: "STATEMENT",
                // important: a forward tokenizer is minimum
                // required by an instant search
                tokenize: "forward"
            },
        ]
    }
});

const data = window.searchIndex;
console.log(data);
for(let i = 0; i < data.length; i++){
    index.add({
        "MID": data[i]["MID"],
        "UID":       data[i]["UID"] || "",
        "STATEMENT": data[i]["STATEMENT"] || "",
    });
}

const suggestions = document.getElementById("suggestions");
const userinput = document.getElementById("userinput");

let selectedIndex = 0;

userinput.addEventListener("input", handleInputEvent_input, true);
userinput.addEventListener("keyup", handleInputEvent_keyUp, true);
userinput.addEventListener("keydown", handleInputEvent_keyDown, true);
suggestions.addEventListener("click", accept_suggestion, true);

function handleInputEvent_input(){
    if (userinput.value === "") {
      suggestions.replaceChildren();
      return;
    }

    console.log("User input: " + userinput.value);

    let results = index.searchCache({
        query: userinput.value,
        index: ["UID", "STATEMENT"],
        suggest: true,
        enrich: true,
        limit: 25,
        //pluck: "UID",
        highlight: "<b>$1</b>"
    });

    console.log(results);
    let i = 0, len = results.length;

    if (len == 0) {
      suggestions.replaceChildren();
      return;
    }

    let flatResults = [];
    let mapMIDtoResult = {};
    for (let i = 0; i < len; i++) {
        const fieldResults = results[i];
        for(let j = 0; j < fieldResults.result.length; j++) {
            const result = fieldResults.result[j];

            let displayResult = null;
            if (!(result.id in mapMIDtoResult)) {
                displayResult = {
                    "MID": result.id,
                }
                flatResults.push(displayResult);
                mapMIDtoResult[result.id] = displayResult;
            } else {
                displayResult = mapMIDtoResult[result.id];
            }
            displayResult[fieldResults.field] = result.highlight;
        }
    }
    console.log("mapMIDtoResult");
    console.log(mapMIDtoResult);

    const children = suggestions.childNodes;

    for(; i < flatResults.length; i++){
        let flatResult = flatResults[i];
        let entry = children[i];

        if(!entry){
            entry = document.createElement("div");
            suggestions.appendChild(entry);
        }

        node_key_values = "";

        Object.entries(flatResult).forEach(([key, value]) => {
            if (key === "MID") {
                return;
            }
            node_key_values = node_key_values + `<div class="static_search_result_node_field">${key}: ${value}</div>`;
        });

        entry.innerHTML = `<div class="static_search_result_node">
${node_key_values}
</div>
`;

    }

    while (children.length > flatResults.length){
        suggestions.removeChild(children[i]);
    }

    select_result(0);
}

function handleInputEvent_keyDown(event) {
    const keyCode = (event || window.event).keyCode;

    if (keyCode === 13 || keyCode === 39) {
        event.preventDefault && event.preventDefault();
        const node = suggestions.childNodes[selectedIndex];
        if (!node) {
            return;
        }
        userinput.value = node.textContent;
        suggestions.textContent = "";
        return;
    }
}

function handleInputEvent_keyUp(event) {
    if(event){
        const key = event.key;
        if (key === "ArrowUp") {
            if (selectedIndex > 0) {
                select_result(selectedIndex - 1);
            }
            event.preventDefault && event.preventDefault();
            return;
        }
        if(key === "ArrowDown"){
            if (selectedIndex < (suggestions.childNodes.length - 1)) {
                select_result(selectedIndex + 1);
            }
            event.preventDefault && event.preventDefault();
            return;
        }
    }
}

function select_result(index){

    let node = suggestions.childNodes[selectedIndex];
    node && (node.style.backgroundColor = "");

    selectedIndex = index;

    node = suggestions.childNodes[selectedIndex];
    node && (node.style.backgroundColor = "rgba(0, 0, 255, 0.1)");
}

function accept_suggestion(event) {
    console.log("accept_autocomplete");
    const target = (event || window.event).target;
    userinput.value = target.textContent;
    suggestions.textContent = "";
    return false;
}
