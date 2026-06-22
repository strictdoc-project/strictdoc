# Arrow keys pan the diagram view while editing a field

## WHAT

Pressing Arrow Up/Down/Left/Right while focus is in any editable field
(contenteditable, autocomplete dropdown navigation, input, textarea) must
not also scroll/pan the table/diagram view. Only the field's own behavior
(caret move, dropdown option navigation) should happen.

## WHY

`strictdoc/export/html/_static/pan_with_space.js` adds a `document`-level
`keydown` listener for panning a `[js-pan_with_space]` view. The Spacebar
branch already skips itself when `document.activeElement` is editable, but
the Arrow* branches had no such check — they always ran
`element.scrollTop/scrollLeft += 20`. So every arrow press anywhere on the
page (typing in a field, navigating autocomplete options, etc.) also panned
the view by a fixed 20px, on top of whatever the field itself did. This was
most visible with the autocomplete dropdown (selection moved AND the page
jumped on every key press), but affected any editable field equally, and
reproduced the same way in Chrome/Firefox/Safari (not a browser quirk).

## HOW

`strictdoc/export/html/_static/pan_with_space.js`: compute `isEditable`
once at the top of the keydown handler (same check already used for
Spacebar — `INPUT`/`TEXTAREA`/`isContentEditable`) and `return` early for
the Arrow* branches when it's true, mirroring the existing Spacebar guard.
No changes needed elsewhere (the autocomplete controller itself was not at
fault).
