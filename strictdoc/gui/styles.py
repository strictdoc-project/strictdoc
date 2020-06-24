
STRICTDOC_QT_STYLES = """
QTableView {
    border: 1px solid '#cccccc';
    gridline-color: '#f0f0f0';
    /* do not seem work */
    color: 'green';
    background: 'red';
}
QTableView::item {
    /* do not seem work */
    background: 'green';
    border: 2px solid 'red';
}
QTableView:item:selected {
    /* do not seem work */
    background-color: 'green'; 
    color: '#FFFFFF'
}
QTableView:item:selected:focus {
    /* do not seem work */
    background-color: 'green';
}
"""