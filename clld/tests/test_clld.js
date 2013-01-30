Test = TestCase("CLLD");

Test.prototype.test_route_url = function() {
    assertEquals(
        '/language/1?format=bib',
        CLLD.route_url('language', {id: 1}, {format: 'bib'}));
};

Test.prototype.test_Feed = function() {
    CLLD.Feed.init({url: 'http://blog.wals.info'});
};

Test.prototype.test_Modal = function() {
    /*:DOC += <div id="Modal"><div id="ModalLabel"></div><div id="ModalBody"></div></div> */
    assertEquals($('#ModalLabel').html(), '');
    CLLD.Modal.show('The Title', 'http://localhost/');
    assertEquals($('#ModalLabel').html(), 'The Title');
};
