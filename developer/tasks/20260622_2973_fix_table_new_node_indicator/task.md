# Clear new-node indicator on click outside the row

## WHAT

Retain the previously implemented indicator `data-node-created=“true”` for
a newly created TR (new node). This attribute controls the CSS styling.

When a user clicks outside this TR, remove this attribute.
When a user clicks inside this TR (for example, when editing cells within it),
retain this indicator.

### Test case

- A new row is assigned the attribute `data-node-created=“true”`
  when it is created.
- Clicking inside the row (to open or close the cell for editing) -
  the attribute remains.
- Clicking outside the row - the attribute is removed.

## WHY

The thick border does not disappear until a new element is created in the table
or the window is refreshed. And some users find this indicator too intrusive.

At the same time, we want to keep the indicator for a newly created node to make
it easier to navigate the table.

## HOW


