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

    def run_command(self, cmd):
        """ Helper method to run a shell command """
        # Set stdout = sys.stdout to debug a subprocess if you set a breakpoint in it
        pipe = Popen(cmd, shell=True, env=os.environ, stdin=None, stdout=PIPE, stderr=PIPE)
        (output, errout) = map(lambda x:x.decode(), pipe.communicate())
        status = pipe.returncode
        self.assertEqual(status, 0, errout or output)
        return (status, output, errout)

    def assertFilesEqual(self, f1, f2):
        options = ""
        if f1.endswith(".po") or f1.endswith(".pot"):
            options = "--ignore-matching-lines=^\\\"POT-Creation-Date"
        result = self.run_command("diff -u %s %s %s" % (options, f1, f2))
        return self.assertEqual(result[1], "", result[1])

    def _test_pot_generation(self, start_file, reference_pot=None):
        start_file_base = os.path.splitext(start_file)[0]
        result = self.run_command("cd %(dir)s && python itstool_test -o %(out)s %(in)s" % {
            'dir' : ITSTOOL_DIR,
            'out' : os.path.join('tests', "test.pot"),
            'in'  : os.path.join('tests', start_file),
        })
        # If a reference pot file is present, test the output with this file
        if reference_pot is None:
            reference_pot = start_file_base + ".pot"
        if os.path.exists(os.path.join(TEST_DIR, reference_pot)):
            self.assertFilesEqual(os.path.join(TEST_DIR, "test.pot"), os.path.join(TEST_DIR, reference_pot))

    def _test_translation_process(self, start_file):
        start_file_base = os.path.splitext(start_file)[0]
        self._test_pot_generation(start_file)

        # Compile mo and merge
        self.run_command("cd %(dir)s && msgfmt -o test.mo %(base)s.ll.po" % {'dir': TEST_DIR, 'base': start_file_base}) 
        res = self.run_command("cd %(dir)s && python itstool_test -m %(mo)s -o %(res)s %(src)s" % {
            'dir': ITSTOOL_DIR,
            'mo' : os.path.join(TEST_DIR, "test.mo"),
            'res': os.path.join(TEST_DIR, "test.xml"),
            'src': os.path.join(TEST_DIR, start_file),
        })
        self.assertFilesEqual(os.path.join(TEST_DIR, "test.xml"), os.path.join(TEST_DIR, "%s.ll.xml" % start_file_base))


    def test_locnotes(self):
        # FIXME: only the third note appears currently, as notes on subnodes don't propagate to parent nodes
        self._test_pot_generation('LocNote1.xml')

    def test_locnotes_external(self):
        # FIXME: only the third note appears currently, as notes on subnodes don't propagate to parent nodes
        self._test_pot_generation('LocNote2.xml')

    def test_locnotes_ontags(self):
        self._test_pot_generation('LocNote3.xml')

    def test_locnotes_onspan(self):
        self._test_pot_generation('LocNote4.xml')

    def test_locnotes_pointer(self):
        self._test_pot_generation('EX-locNotePointer-attribute-1.xml')

    def test_locnotes_refpointer(self):
        self._test_pot_generation('EX-locNoteRefPointer-attribute-1.xml')

    # FIXME: test EX-locNote-selector-2.xml when parent locNotes will propagate to children

    def test_unicode_markup(self):
        self._test_translation_process('Translate1.xml')

    def test_external_rules(self):
        self._test_translation_process('Translate2.xml')

    def test_embedded_its(self):
        self._test_translation_process('Translate3.xml')

    def test_notranslate_to_simpletag(self):
        self._test_translation_process('Translate4.xml')

    def test_selector_translate_rule(self):
        self._test_translation_process('Translate5.xml')

    def test_root_selector(self):
        self._test_translation_process('Translate6.xml')

    def test_last_rule_win(self):
        self._test_translation_process('Translate7.xml')

    def test_attribute_selectable(self):
        self._test_translation_process('TranslateGlobal.xml')

    def test_withintext(self):
        self._test_translation_process('WithinText1.xml')

    def test_withintext_linkedrules(self):
        self._test_translation_process('WithinText2.xml')

    # **** custom itst rules ****
    def test_droprule(self):
        self._test_translation_process('Droprule.xml')

    def test_attributes1(self):
        self._test_translation_process('Attributes1.xml')

    def test_context(self):
        self._test_translation_process('Context.xml')


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

