import XCTest
import SwiftTreeSitter
import TreeSitterStrictdoc

final class TreeSitterStrictdocTests: XCTestCase {
    func testCanLoadGrammar() throws {
        let parser = Parser()
        let language = Language(language: tree_sitter_strictdoc())
        XCTAssertNoThrow(try parser.setLanguage(language),
                         "Error loading StrictDoc grammar")
    }
}
