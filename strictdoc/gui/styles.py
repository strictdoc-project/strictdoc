
STRICTDOC_QT_STYLES = """
QTableView {
    border: 1px solid '#cccccc';
    gridline-color: '#f0f0f0';
    /* do not seem work */
    color: 'green';
    background: 'red';
    background-color: 'red';
}
QTableView::item {
    /* 
     * padding and margin are important for edited cell to appear on the same
     * position 
     */
    padding: 0px 0px;
    margin: -3px;
    /* do not seem work */
    background: 'green';
    background-color: 'green';
    border: 2px solid 'red';
}
QTableView:item:selected {
    /* do not seem work */
    background-color: 'green'; 
    color: '#FFFFFF';
    border: 2px solid 'red';
}
QTableView:item:selected:focus {
    /* do not seem work */
    border: 2px solid 'red';
    background-color: 'green';
}
"""