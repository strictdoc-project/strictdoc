// MIT License
//
// based on https://github.com/afcapel/stimulus-autocomplete/
// Copyright (c) 2021 Alberto Fernández-Capel

(() => {

  const optionSelector = "[role='option']:not([aria-disabled])"
  const activeSelector = "[aria-selected='true']"

  class AutoCompletable extends Stimulus.Controller {
    static targets = ["name"]
    static classes = ["selected"]
    static values = {
      ready: Boolean,
      url: String,
      minLength: Number,
      delay: { type: Number, default: 10 },
      queryParam: { type: String, default: "q" },
      multipleChoice: Boolean,
    }
    static uniqOptionId = 0

    connect() {
      // this.element is the DOM element to which the controller is connected to.
      const autocompletable = this.element
      this.autocompletable = autocompletable
      this.hidden = autocompletable.nextElementSibling
      this.results = this.hidden.nextElementSibling
      this.abortController = null;

      this.close()

      if (!autocompletable.hasAttribute("autocompletable")) autocompletable.setAttribute("autocompletable", "off")
      autocompletable.setAttribute("spellcheck", "false")

      this.mouseDown = false

      this.onInputChange = debounce(this.onInputChange, this.delayValue)

      this.autocompletable.addEventListener("input", this.onInputChange)

      autocompletable.addEventListener("keydown", (event) => {
        const handler = this[`on${event.key}Keydown`]
        if (handler) handler(event)
      });

      autocompletable.addEventListener("blur", (event) => {
        if (this.mouseDown) return
        this.close()
      });

      autocompletable.addEventListener("click", (event) => {      
        /* Toggle between showing / hiding results. */
        if (this.resultsShown) {
          this.hideAndRemoveOptions();
        } else {
          /* If minLengthValue is 0, we want to get all possible options (i.e. for SingleChoice).
             Otherwise, we want narrow-down-as-you-type behavior, and filter on remainig options.
           */
          const query = this.minLengthValue == 0 ? "" : this.autocompletable.innerText.trim();
          this.fetchResults(query);
        }
      });

      this.results.addEventListener("mousedown", this.onResultsMouseDown)
      this.results.addEventListener("click", this.onResultsClick)

      if (autocompletable.hasAttribute("autofocus")) {
        autocompletable.focus()
      }

      this.readyValue = true
    }

    disconnect() {
      this.autocompletable.removeEventListener("keydown", this.onKeydown)
      this.autocompletable.removeEventListener("blur", this.onInputBlur)
      this.autocompletable.removeEventListener("input", this.onInputChange)

      this.results.removeEventListener("mousedown", this.onResultsMouseDown)
      this.results.removeEventListener("click", this.onResultsClick)
    }

    sibling(next) {
      const options = this.options
      const selected = this.selectedOption
      const index = options.indexOf(selected)
      const sibling = next ? options[index + 1] : options[index - 1]
      const def = next ? options[0] : options[options.length - 1]
      return sibling || def
    }

    select(target) {
      const previouslySelected = this.selectedOption
      if (previouslySelected) {
        previouslySelected.removeAttribute("aria-selected")
        previouslySelected.classList.remove(...this.selectedClassesOrDefault)
      }

      target.setAttribute("aria-selected", "true")
      target.classList.add(...this.selectedClassesOrDefault)
      this.autocompletable.setAttribute("aria-activedescendant", target.id)
      target.scrollIntoView({ behavior: "auto", block: "nearest" })
    }

    selectText(text) {
      const normalizedText = text.trim().toLowerCase();
      const match = this.options.find(option => {
        const label = option.getAttribute("data-autocompletable-label") || option.textContent;
        return label.trim().toLowerCase() === normalizedText;
      });
    
      if (match) {
        this.select(match);
      }
    }

    onEscapeKeydown = (event) => {
      if (!this.resultsShown) return

      this.hideAndRemoveOptions()
      event.stopPropagation()
      event.preventDefault()
    }

    onArrowDownKeydown = (event) => {
      if (!this.resultsShown) return

      const item = this.sibling(true)
      if (item) this.select(item)
      event.preventDefault()
    }

    onArrowUpKeydown = (event) => {
      if (!this.resultsShown) return

      const item = this.sibling(false)
      if (item) this.select(item)
      event.preventDefault()
    }

    onTabKeydown = (event) => {
      if (!this.resultsShown) return

      /* Either use the selected options, or else select the first result. */
      const selected = this.selectedOption || this.sibling(true)
      this.commit(selected)
      event.preventDefault();
    }

    onEnterKeydown = (event) => {
      const selected = this.selectedOption
      if (selected && this.resultsShown) {
        this.commit(selected)
      }
      /* single line, dont allow enter */
      event.preventDefault()
    }

    commit(selected) {
      if (selected.getAttribute("aria-disabled") === "true") return

      if (selected instanceof HTMLAnchorElement) {
        selected.click()
        this.close()
        return
      }

      const textValue = selected.getAttribute("data-autocompletable-label") || selected.textContent.trim()
      let   suggestion = selected.getAttribute("data-autocompletable-value") || textValue
    
      if (this.multipleChoiceValue) {
        // Get the current text content
        const text = this.autocompletable.innerText || "";
        const parts = text.split(",");

        // Replace the last incomplete token with the suggestion.
        parts[parts.length - 1] = " " + suggestion;
        suggestion = parts.map(p => p.trim()).join(", ")
      } 

      this.autocompletable.innerText = suggestion
      this.hidden.value = suggestion

      // Move the cursor to the end of the input. 
      this.autocompletable.focus();
      const range = document.createRange();
      range.selectNodeContents(this.autocompletable);
      range.collapse(false);
      const sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);

      this.hidden.dispatchEvent(new Event("input"))
      this.hidden.dispatchEvent(new Event("change"))

      this.autocompletable.focus()
      this.hideAndRemoveOptions()

      this.element.dispatchEvent(
        new CustomEvent("autocompletable.change", {
          bubbles: true,
          detail: { value: suggestion, textValue: textValue, selected: selected }
        })
      )
    }

    clear() {
      this.autocompletable.innerText = ""
      this.hidden.value = ""
    }

    onResultsClick = (event) => {
      if (!(event.target instanceof Element)) return
      const selected = event.target.closest(optionSelector)
      if (selected) this.commit(selected)
    }

    onResultsMouseDown = () => {
      this.mouseDown = true
      this.results.addEventListener("mouseup", () => {
        this.mouseDown = false
      }, { once: true })
    }

    onInputChange = ()  => {
      const query = this.autocompletable.innerText.trim()
      if (query && query.length >= this.minLengthValue) {
        this.fetchResults(query)
      } else {
        this.hideAndRemoveOptions()
      }

      const text = filterSingleLine(this.autocompletable.innerText)
      this.hidden.value = text
    }

    identifyOptions() {
      const prefix = this.results.id || "autocompletable"
      const optionsWithoutId = this.results.querySelectorAll(`${optionSelector}:not([id])`)
      optionsWithoutId.forEach(el => el.id = `${prefix}-option-${this.constructor.uniqOptionId++}`)
    }

    hideAndRemoveOptions() {
      this.close()
      this.results.innerHTML = null
    }

    fetchResults = async (query) => {
      if (!this.hasUrlValue) return

      /* Abort the previous request as we are about to send a new one. */
      if (this.abortController) {
        this.abortController.abort();
      }
      this.abortController = new AbortController();
      const signal = this.abortController.signal;

      const url = this.buildURL(query)
      try {
        this.element.dispatchEvent(new CustomEvent("loadstart"))
        const html = await this.doFetch(url, signal)
        this.replaceResults(html)
        /* Check if an entry matches the current text and select it. */
        this.selectText(this.autocompletable.innerText.trim());
        this.element.dispatchEvent(new CustomEvent("load"))
        this.element.dispatchEvent(new CustomEvent("loadend"))
      } catch (error) {
        if (error.name === 'AbortError') {
          return;
        }
        this.element.dispatchEvent(new CustomEvent("error"))
        this.element.dispatchEvent(new CustomEvent("loadend"))
        throw error
      }
    }

    buildURL(query) {
      const url = new URL(this.urlValue, window.location.href)
      const params = new URLSearchParams(url.search.slice(1))
      params.append(this.queryParamValue, query)
      url.search = params.toString()

      return url.toString()
    }

    doFetch = async (url, signal) => {
      const response = await fetch(url, {signal})

      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`)
      }

      const html = await response.text()
      return html
    }

    replaceResults(html) {
      this.results.innerHTML = html
      this.identifyOptions()
      if (!!this.options) {
        this.open()
      } else {
        this.close()
      }
    }

    open() {
      if (this.resultsShown) return

      this.resultsShown = true
      this.element.setAttribute("aria-expanded", "true")
      this.element.dispatchEvent(
        new CustomEvent("toggle", {
          detail: { action: "open", autocompletable: this.autocompletable, results: this.results }
        })
      )
    }

    close() {
      if (!this.resultsShown) return

      this.resultsShown = false
      this.autocompletable.removeAttribute("aria-activedescendant")
      this.element.setAttribute("aria-expanded", "false")
      this.element.dispatchEvent(
        new CustomEvent("toggle", {
          detail: { action: "close", autocompletable: this.autocompletable, results: this.results }
        })
      )
    }

    get resultsShown() {
      return !this.results.hidden
    }

    set resultsShown(value) {
      this.results.hidden = !value
    }

    get options() {
      return Array.from(this.results.querySelectorAll(optionSelector))
    }

    get selectedOption() {
      return this.results.querySelector(activeSelector)
    }

    get selectedClassesOrDefault() {
      return this.hasSelectedClass ? this.selectedClasses : ["autocomplete-active"]
    }

  }

  Stimulus.application.register("autocompletable", AutoCompletable);

  function filterSingleLine(text) {
    return text.replace(/\s/g, ' ').replace(/\s\s+/g, ' ')
  }

  const debounce = (fn, delay = 10) => {
    let timeoutId = null

    return (...args) => {
      clearTimeout(timeoutId)
      timeoutId = setTimeout(fn, delay)
    }
  }

})();

