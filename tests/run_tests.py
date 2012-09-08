import os
import shutil
from subprocess import Popen, PIPE, call
import sys
import unittest

TEST_DIR    = os.path.dirname(os.path.abspath(__file__))
ITSTOOL_DIR = os.path.dirname(TEST_DIR)

class ItstoolTests(unittest.TestCase):
    def tearDown(self):
        for test_file in ('test.pot', 'test.mo', 'test.xml'):
            path = os.path.join(TEST_DIR, test_file)
            if os.path.exists(path):
                os.remove(path)

    def run_command(self, cmd, expected_status=0):
        """ Helper method to run a shell command """
        # Set stdout = sys.stdout to debug a subprocess if you set a breakpoint in it
        pipe = Popen(cmd, shell=True, env=os.environ, stdin=None, stdout=PIPE, stderr=PIPE)
        (output, errout) = map(lambda x:x.decode('utf-8'), pipe.communicate())
        status = pipe.returncode
        self.assertEqual(status, expected_status, errout or output)
        return {'status': status, 'output': output, 'errors': errout}

    def assertFilesEqual(self, f1, f2):
        options = ""
        if f1.endswith(".po") or f1.endswith(".pot"):
            options = "--ignore-matching-lines=^\\\"POT-Creation-Date"
        result = self.run_command("diff -u %s %s %s" % (options, f1, f2))
        self.assertEqual(result['output'], "", result['output'])

    def _test_pot_generation(self, start_file, reference_pot=None, expected_status=0):
        start_file_base = os.path.splitext(start_file)[0]
        result = self.run_command("cd %(dir)s && python itstool_test -o %(out)s %(in)s" % {
            'dir' : ITSTOOL_DIR,
            'out' : os.path.join('tests', "test.pot"),
            'in'  : os.path.join('tests', start_file),
        }, expected_status)
        # If a reference pot file is present, test the output with this file
        if reference_pot is None:
            reference_pot = start_file_base + ".pot"
        if os.path.exists(os.path.join(TEST_DIR, reference_pot)):
            self.assertFilesEqual(os.path.join(TEST_DIR, "test.pot"), os.path.join(TEST_DIR, reference_pot))
        return result

    def _test_translation_join(self, start_file, langs, xml_file=None):
        start_file_base = os.path.splitext(start_file)[0]
        self._test_pot_generation(start_file)

        for lang in langs:
            po_file = '%s.%s.po' % (start_file_base, lang)
            mo_file = '%s.mo' % lang
            self.run_command("cd %(dir)s && msgfmt -o %(mo_file)s %(po_file)s" %
                             {'dir': TEST_DIR, 'mo_file': mo_file, 'po_file': po_file})
        result = self.run_command("cd %(dir)s && python itstool_test -o%(res)s -j %(src)s %(mo)s" % {
                'dir': ITSTOOL_DIR,
                'res': os.path.join(TEST_DIR, 'test.xml'),
                'src': os.path.join(TEST_DIR, start_file),
                'mo': ' '.join([os.path.join(TEST_DIR, '%s.mo' % lang) for lang in langs])
                })
        if xml_file is None:
            xml_file = '%s.ll.xml' % start_file_base
        self.assertFilesEqual(
            os.path.join(TEST_DIR, 'test.xml'),
            os.path.join(TEST_DIR, xml_file)
            )
        return result
            

    def _test_translation_process(self, start_file, expected_status=0, po_file=None, xml_file=None, options=None):
        start_file_base = os.path.splitext(start_file)[0]
        self._test_pot_generation(start_file)

        # Compile mo and merge
        if po_file is None:
            po_file = "%s.ll.po" % start_file_base
        self.run_command("cd %(dir)s && msgfmt -o test.mo %(po_file)s" % {'dir': TEST_DIR, 'po_file': po_file}) 
        result = self.run_command("cd %(dir)s && python itstool_test %(opt)s -m %(mo)s -o %(res)s %(src)s" % {
            'dir': ITSTOOL_DIR,
            'opt': (options or ''),
            'mo' : os.path.join(TEST_DIR, "test.mo"),
            'res': os.path.join(TEST_DIR, "test.xml"),
            'src': os.path.join(TEST_DIR, start_file),
        }, expected_status)
        if xml_file is None:
            xml_file = "%s.ll.xml" % start_file_base
        if (expected_status == 0):
            self.assertFilesEqual(
                os.path.join(TEST_DIR, "test.xml"),
                os.path.join(TEST_DIR, xml_file)
            )
        return result


    def test_LocNote1(self):
        # FIXME: only the third note appears currently, as notes on subnodes don't propagate to parent nodes
        self._test_pot_generation('LocNote1.xml')

    def test_LocNote2(self):
        # FIXME: only the third note appears currently, as notes on subnodes don't propagate to parent nodes
        self._test_pot_generation('LocNote2.xml')

    def test_LocNote3(self):
        self._test_pot_generation('LocNote3.xml')

    def test_LocNote4(self):
        self._test_pot_generation('LocNote4.xml')

    def test_EX_locNote_element_1(self):
        self._test_pot_generation('EX-locNote-element-1.xml')

    def test_EX_locNote_selector_2(self):
        self._test_pot_generation('EX-locNote-selector-2.xml')

    def test_EX_locNotePointer_attribute_1(self):
        self._test_pot_generation('EX-locNotePointer-attribute-1.xml')

    def test_EX_locNoteRef_attribute_1(self):
        self._test_pot_generation('EX-locNoteRef-attribute-1.xml')

    def test_EX_locNoteRefPointer_attribute_1(self):
        self._test_pot_generation('EX-locNoteRefPointer-attribute-1.xml')

    def test_PreserveSpace1(self):
        self._test_pot_generation('preservespace1xml.xml')

    def test_PreserveSpace2(self):
        self._test_pot_generation('preservespace2xml.xml')

    def test_PreserveSpace3(self):
        self._test_pot_generation('preservespace3xml.xml')

    def test_PreserveSpace4(self):
        self._test_pot_generation('preservespace4xml.xml')

    def test_Translate1(self):
        self._test_translation_process('Translate1.xml')

    def test_Translate2(self):
        self._test_translation_process('Translate2.xml')

    def test_Translate3(self):
        self._test_translation_process('Translate3.xml')

    def test_Translate4(self):
        self._test_translation_process('Translate4.xml')

    def test_Translate5(self):
        self._test_translation_process('Translate5.xml')

    def test_Translate6(self):
        self._test_translation_process('Translate6.xml')

    def test_Translate7(self):
        self._test_translation_process('Translate7.xml')

    def test_TranslateGlobal(self):
        self._test_translation_process('TranslateGlobal.xml')

    def test_WithinText1(self):
        self._test_translation_process('WithinText1.xml')

    def test_WithinText2(self):
        self._test_translation_process('WithinText2.xml')

    def test_IT_locNote_inline(self):
        self._test_pot_generation('IT-locNote-inline.xml')

    def test_IT_locNote_multiples(self):
        self._test_pot_generation('IT-locNote-multiples.xml')

    # **** custom itst rules ****
    def test_IT_dropRule_1(self):
        self._test_translation_process('IT-dropRule-1.xml')

    def test_IT_attributes_1(self):
        self._test_translation_process('IT-attributes-1.xml')

    def test_IT_context_1(self):
        self._test_translation_process('IT-context-1.xml')

    def test_IT_placeholder_1(self):
        self._test_translation_process('IT-placeholder-1.xml')

    def test_IT_malformed(self):
        """ Test that a malformed XML generates a proper exception """
        res = self._test_pot_generation('IT-malformed.xml', expected_status=1)
        #self.assertTrue("libxml2.parserError" in res['errors'])

    def test_IT_join_1(self):
        res = self._test_translation_join('IT-join-1.xml', ('cs', 'de', 'fr'))

    def test_Translate3_wrong1(self):
        """ Test that bad XML syntax in translation generates a proper exception """
        res = self._test_translation_process('Translate3.xml', expected_status=1,
                                             po_file='Translate3.ll.wrong.po',
                                             options='-s')
        #self.assertTrue("libxml2.parserError" in res['errors'])

    def test_Translate3_wrong2(self):
        """ Test that bad XML syntax in translation is handled gracefully """
        res = self._test_translation_process('Translate3.xml',
                                             po_file='Translate3.ll.wrong.po',
                                             xml_file='Translate3.ll.wrong.xml')


class ITSTestRunner(unittest.TextTestRunner):
    def run(self, test):
        # Global setup
        test_binary_path = os.path.join(ITSTOOL_DIR, "itstool_test")
        shutil.copy(os.path.join(ITSTOOL_DIR, "itstool.in"), test_binary_path)
        data_dir = os.path.join(ITSTOOL_DIR, "its")
        call("sed -i -e 's/@DATADIR@/%s/' %s" % (data_dir.replace('/', '\/'), test_binary_path), shell=True)

        result = super(ITSTestRunner, self).run(test)

        os.remove(test_binary_path)
        return result


if __name__ == '__main__':
    unittest.main(testRunner=ITSTestRunner)

